import asyncio
from app.db.postgres import execute_query
from app.db.queries import UPSERT_CRAWL_STATUS, UPSERT_CRAWLED_PAGE, ADD_URLS_COLUMN
from app.db.database import get_connection
from app.services.crawl_service import discover_urls
from app.utils.status_tracker import update_crawl_status
from app.utils.async_utils import get_event_loop
from sqlalchemy import text

def run_background_crawl(website_id: int, website_url: str):
    update_crawl_status(website_id, "crawling", 0, [])
    try:
        execute_query(UPSERT_CRAWL_STATUS, {"website_id": website_id, "status": "crawling", "urls_found": 0, "error": None, "urls": []})
    except Exception:
        pass

    try:
        loop = get_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            discovered_urls = loop.run_until_complete(discover_urls(website_url))
            print(f"Crawl completed for website ID {website_id} found {len(discovered_urls)} urls.")
            
            with get_connection() as connection:
                for page_url in discovered_urls:
                    connection.execute(text(UPSERT_CRAWLED_PAGE), {
                        "website_id": website_id, 
                        "website_url": website_url, 
                        "page_url": page_url
                    })
                connection.commit()
                
            try:
                execute_query(ADD_URLS_COLUMN)
            except Exception:
                pass
                
            update_crawl_status(website_id, "completed", len(discovered_urls), discovered_urls)
            
            try:
                execute_query(UPSERT_CRAWL_STATUS, {
                    "website_id": website_id, 
                    "status": "completed", 
                    "urls_found": len(discovered_urls), 
                    "error": None, 
                    "urls": discovered_urls
                })
            except Exception:
                pass
                
        finally:
            loop.close()
            
    except Exception as error:
        update_crawl_status(website_id, "failed", 0, [], str(error))
        try:
            execute_query(UPSERT_CRAWL_STATUS, {
                "website_id": website_id, 
                "status": "failed", 
                "urls_found": 0, 
                "error": str(error), 
                "urls": []
            })
        except Exception:
            pass
        print(f"Crawl failed for website {website_id}: {error}")
