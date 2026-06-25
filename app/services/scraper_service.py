from patchright.async_api import async_playwright as patchright_async
from playwright.async_api import async_playwright as playwright_async
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

STEALTH_DOMAINS = {"nowsecure.nl", "pixelscan.dev", "browserleaks.com", "bot-detector.rebrowser.net", "edwarddonner.com"}

BROWSER_CONFIG = BrowserConfig(
    browser_type="undetected",
    headless=True,
    enable_stealth=True,
    extra_args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--js-flags=--max-old-space-size=256",
    ],
)

CRAWL_CONFIG = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    magic=True,
    simulate_user=True,
    wait_until="domcontentloaded",
    page_timeout=20000,
    delay_before_return_html=0.5,
)


async def patchright_extract_links(url: str) -> list:
    links = []
    try:
        domain = urlparse(url).netloc.lower()
        async with patchright_async() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors", "--allow-running-insecure-content", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions"],
            )
            context = await browser.new_context(
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)
            wait_strategy = "domcontentloaded" if domain in STEALTH_DOMAINS else "networkidle"
            await page.goto(url, wait_until=wait_strategy, timeout=60000)
            await page.wait_for_timeout(5000)
            anchors = await page.locator("a").evaluate_all(
                "els => [...new Set(els.map(e => e.href).filter(Boolean))]"
            )
            links.extend(anchors)
            await browser.close()
            print(f"Patchright success: {url}")
    except Exception as e:
        print(f"Patchright failed: {url} — {e}")
    return links


async def patchright_scrape_page(url: str) -> str:
    content = ""
    try:
        domain = urlparse(url).netloc.lower()
        async with patchright_async() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors", "--allow-running-insecure-content", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions"],
            )
            context = await browser.new_context(
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)
            wait_strategy = "domcontentloaded" if domain in STEALTH_DOMAINS else "networkidle"
            await page.goto(url, wait_until=wait_strategy, timeout=60000)
            await page.wait_for_timeout(5000)
            content = await page.locator("body").inner_text()
            await browser.close()
            print(f"Patchright scrape success: {url} ({len(content)} chars)")
    except Exception as e:
        print(f"Patchright scrape failed: {url} — {e}")
    return content


async def playwright_extract_links(url: str) -> list:
    links = []
    try:
        domain = urlparse(url).netloc.lower()
        async with playwright_async() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors", "--allow-running-insecure-content", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions"],
            )
            context = await browser.new_context(
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)
            wait_strategy = "domcontentloaded" if domain in STEALTH_DOMAINS else "networkidle"
            await page.goto(url, wait_until=wait_strategy, timeout=60000)
            await page.wait_for_timeout(5000)
            anchors = await page.locator("a").evaluate_all(
                "els => [...new Set(els.map(e => e.href).filter(Boolean))]"
            )
            links.extend(anchors)
            await browser.close()
            print(f"Playwright success: {url}")
    except Exception as e:
        print(f"Playwright failed: {url} — {e}")
    return links


async def playwright_scrape_page(url: str) -> str:
    content = ""
    try:
        domain = urlparse(url).netloc.lower()
        async with playwright_async() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors", "--allow-running-insecure-content", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions"],
            )
            context = await browser.new_context(
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)
            wait_strategy = "domcontentloaded" if domain in STEALTH_DOMAINS else "networkidle"
            await page.goto(url, wait_until=wait_strategy, timeout=60000)
            await page.wait_for_timeout(5000)
            content = await page.locator("body").inner_text()
            await browser.close()
            print(f"Playwright scrape success: {url} ({len(content)} chars)")
    except Exception as e:
        print(f"Playwright scrape failed: {url} — {e}")
    return content


async def scrape_url_content(crawler: AsyncWebCrawler, url: str) -> str:
    try:
        result = await crawler.arun(url=url, config=CRAWL_CONFIG)
        if result.success and result.markdown:
            print(f"Crawl4AI scrape success: {url}")
            return result.markdown
    except Exception as e:
        print(f"Crawl4AI scrape failed: {url} — {e}")

    try:
        content = await playwright_scrape_page(url)
        if content:
            return content
    except Exception:
        pass

    try:
        content = await patchright_scrape_page(url)
        if content:
            return content
    except Exception:
        pass

    return ""
