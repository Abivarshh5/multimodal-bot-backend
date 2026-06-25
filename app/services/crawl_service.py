import asyncio
import ssl
import certifi
import xml.etree.ElementTree as ET
from collections import deque
from urllib.parse import urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import httpx
from crawl4ai import AsyncWebCrawler
from app.services.scraper_service import (
    BROWSER_CONFIG,
    CRAWL_CONFIG,
    playwright_extract_links,
    patchright_extract_links
)
from app.utils.helpers import normalize_url

CONCURRENCY = 3
MAX_URLS = 200
ENABLE_RECURSIVE_CRAWL = True
SITEMAP_RECURSIVE_THRESHOLD = 50

EXCLUDED_PATHS = {"/cart", "/checkout", "/checkouts", "/account", "/customer_authentication", "/orders", "/admin", "/cdn-cgi"}
EXCLUDED_QUERY_PARAMS = {"page", "sort_by", "filter", "preview_theme_id", "preview_script_id", "oseid", "ls", "utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid", "ref"}
NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

def should_crawl(url: str) -> bool:
    parsed = urlparse(url)
    if any(parsed.path.startswith(p) for p in EXCLUDED_PATHS):
        return False
    return True

async def get_robots(base_url: str):
    rp = RobotFileParser()
    try:
        async with httpx.AsyncClient(timeout=20, verify=SSL_CONTEXT, follow_redirects=True) as client:
            response = await client.get(f"{base_url}/robots.txt")
        if response.status_code == 200:
            rp.parse(response.text.splitlines())
            print("robots.txt loaded")
            return rp, response.text
    except Exception as e:
        print(f"robots.txt failed: {e}")
    return rp, ""

def extract_sitemaps(robots_text: str) -> list[str]:
    return [
        line.split(":", 1)[1].strip()
        for line in robots_text.splitlines()
        if line.lower().startswith("sitemap:") and line.split(":", 1)[1].strip()
    ]

async def parse_sitemap(sitemap_url: str, discovered: set) -> None:
    try:
        async with httpx.AsyncClient(timeout=30, verify=SSL_CONTEXT, follow_redirects=True) as client:
            response = await client.get(sitemap_url)
        if response.status_code != 200:
            return
        root = ET.fromstring(response.text)

        if root.tag.endswith("sitemapindex"):
            tasks = [
                parse_sitemap(loc.text.strip(), discovered)
                for sitemap in root.findall("sm:sitemap", NAMESPACE)
                if (loc := sitemap.find("sm:loc", NAMESPACE)) is not None
            ]
            await asyncio.gather(*tasks)
        elif root.tag.endswith("urlset"):
            for url_el in root.findall("sm:url", NAMESPACE):
                loc = url_el.find("sm:loc", NAMESPACE)
                if loc is None:
                    continue
                normalized = normalize_url(loc.text.strip())
                if should_crawl(normalized):
                    discovered.add(normalized)
    except Exception as e:
        print(f"Sitemap parse failed: {sitemap_url} — {e}")

def _filter_links(links: list, domain: str) -> list:
    return [
        href for raw in links
        if (href := normalize_url(raw if isinstance(raw, str) else raw.get("href", "")))
        and should_crawl(href)
        and urlparse(href).netloc == domain
    ]

async def crawl_url(crawler: AsyncWebCrawler, url: str, domain: str) -> list:
    try:
        result = await crawler.arun(url=url, config=CRAWL_CONFIG)
        if result.success and result.links:
            cleaned = _filter_links(result.links.get("internal", []), domain)
            if cleaned:
                print(f"Crawl4AI success: {url}")
                return cleaned
    except Exception as e:
        print(f"Crawl4AI failed: {url} — {e}")

    try:
        links = await playwright_extract_links(url)
        cleaned = _filter_links(links, domain)
        if cleaned:
            return cleaned
    except Exception:
        pass

    try:
        links = await patchright_extract_links(url)
        cleaned = _filter_links(links, domain)
        if cleaned:
            return cleaned
    except Exception:
        pass
    return []

async def recursive_discovery(start_url: str, discovered: set) -> None:
    domain = urlparse(start_url).netloc
    queue = deque([start_url])
    visited = set()
    queued = {start_url}
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def worker(crawler: AsyncWebCrawler, url: str):
        async with semaphore:
            return await crawl_url(crawler, url, domain)

    async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
        while queue:
            if len(discovered) >= MAX_URLS:
                break
            batch = []
            while queue and len(batch) < CONCURRENCY:
                url = queue.popleft()
                if url not in visited:
                    batch.append(url)
            if not batch:
                continue
            results = await asyncio.gather(*[worker(crawler, url) for url in batch])
            for url, links in zip(batch, results):
                visited.add(url)
                discovered.add(url)
                for href in links:
                    if href not in visited and href not in queued:
                        queue.append(href)
                        queued.add(href)

async def discover_urls(website_url: str) -> list[str]:
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url
    parsed = urlparse(website_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    discovered = set()

    print("\nstarting crawl")
    print("reading robots.txt")
    _, robots_text = await get_robots(base_url)

    print("Looking for sitemaps")
    sitemaps = extract_sitemaps(robots_text)
    if sitemaps:
        print(f"Found {len(sitemaps)} sitemap(s)")
        await asyncio.gather(*[parse_sitemap(s, discovered) for s in sitemaps])
    print(f"Sitemap URLs discovered: {len(discovered)}")

    if ENABLE_RECURSIVE_CRAWL and len(discovered) < SITEMAP_RECURSIVE_THRESHOLD:
        print("\nrunning recursive crawl")
        await recursive_discovery(website_url, discovered)
    else:
        print("\nskipping recursive crawl")

    print("found urls:", len(discovered))
    return sorted(discovered)
