import asyncio
from app.db.postgres import fetch_all, execute_query
from app.db.queries import GET_UNTRAINED_SELECTED_PAGES, UPDATE_PAGE_CONTENT, MARK_PAGES_TRAINED
from app.services.scraper_service import scrape_url_content
from app.services.vector_service import chunk_page
from app.services.embedding_service import generate_embedding
from app.db.weaviate import get_weaviate_client, ensure_collection, store_chunks_batch
from app.utils.status_tracker import update_training_status
from app.utils.helpers import normalize_url
from crawl4ai import AsyncWebCrawler
from app.services.scraper_service import BROWSER_CONFIG

async def scrape_selected_urls(urls: list[str]) -> dict[str, str]:
    results = {}
    semaphore = asyncio.Semaphore(5)

    async def worker(crawler: AsyncWebCrawler, url: str):
        async with semaphore:
            content = await scrape_url_content(crawler, url)
            results[url] = content

    async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
        await asyncio.gather(*[worker(crawler, url) for url in urls])

    return results

async def run_background_training(website_id: int, website_url: str):
    normalized = normalize_url(website_url)
    update_training_status(normalized, "training")
    update_training_status(website_id, "training")
    
    try:
        db_rows = fetch_all(GET_UNTRAINED_SELECTED_PAGES, {"id": website_id})
        
        if len(db_rows) == 0:
            print(f"No untrained selected URLs found for {website_url}")
            update_training_status(normalized, "completed")
            update_training_status(website_id, "completed")
            return
            
        urls_to_scrape = [row[1] for row in db_rows]
        url_database_ids = [row[0] for row in db_rows]
        print("starting training")
        print("selected pages:", urls_to_scrape)
        print("scraping pages")
        scraped_content_dict = await scrape_selected_urls(urls_to_scrape)
        print("scraping completed")
        total_chunks = 0
        all_chunks = []
        all_embeddings = []
        print("creating chunks and generating embeddings")
        for page_url in urls_to_scrape:
            content_text = scraped_content_dict.get(page_url, "")
            
            if content_text != "":
                execute_query(UPDATE_PAGE_CONTENT, {"content": content_text, "url": page_url})
                chunks = chunk_page(text=content_text, page_url=page_url, website_url=website_url)
                
                if len(chunks) > 0:
                    total_chunks += len(chunks)
                    for chunk in chunks:
                        embedding_numbers = generate_embedding(chunk["chunk_text"])
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding_numbers)
                        
        if len(all_chunks) > 0 and len(all_embeddings) > 0:
            print("saving to weaviate")
            db_client = get_weaviate_client()
            ensure_collection(db_client)
            store_chunks_batch(db_client, all_chunks, all_embeddings)
            db_client.close()
                
        if len(url_database_ids) > 0:
            print("updating trained status")
            print(url_database_ids)
            execute_query(MARK_PAGES_TRAINED, {"ids": url_database_ids})
                
        update_training_status(normalized, "completed")
        update_training_status(website_id, "completed")
        print("training completed")
        
    except Exception as error:
        update_training_status(normalized, "failed", str(error))
        update_training_status(website_id, "failed", str(error))
        print(f"Training failed: {error}")
