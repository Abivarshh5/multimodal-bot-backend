import threading
from app.db.postgres import execute_query, fetch_one, fetch_all, execute_returning_id
from app.db.queries import (FIND_WEBSITE_BY_URL, INSERT_WEBSITE, RENAME_WEBSITE, DELETE_WEBSITE, GET_ALL_DATA_SOURCES,DELETE_CRAWLED_PAGES_BY_WEBSITE, DELETE_CRAWL_STATUS, GET_CRAWL_STATUS, COUNT_TOTAL_PAGES, GET_DATASOURCE_PAGES)
from app.db.weaviate import get_weaviate_client, delete_chunks_for_website
from app.models.requests import WebsiteRequest, DataSourceRenameRequest
from app.utils.response import success_response, error_response
from app.utils.helpers import normalize_url
from app.utils.status_tracker import crawl_status_tracker

def _start_background_crawl(website_id: int, website_url: str):
    from app.main_crawl_task import run_background_crawl  
    background_thread = threading.Thread(target=run_background_crawl, args=(website_id, website_url), daemon=True)
    background_thread.start()

def _start_background_branding(website_id: int, website_url: str):
    def branding_task():
        from app.services.branding_service import extract_branding, save_branding
        branding = extract_branding(website_url)
        if branding:
            save_branding(website_id, branding)
            
    threading.Thread(target=branding_task, daemon=True).start()

def add_website(request_data: WebsiteRequest):
    try:
        url = request_data.url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        normalized = normalize_url(url)
        
        row = fetch_one(FIND_WEBSITE_BY_URL, {"url": normalized, "url_slash": normalized + "/"})
        if row:
            return success_response({"id": row[0], "url": row[1], "message": "already_exists"})

        new_website_id = execute_returning_id(INSERT_WEBSITE, {"tenant_id": request_data.tenant_id, "base_url": url})
        
        _start_background_branding(new_website_id, url)
        _start_background_crawl(new_website_id, url)
        return success_response({"id": new_website_id, "url": url})
    except Exception as error:
        return error_response(str(error))

def get_data_sources():
    try:
        rows = fetch_all(GET_ALL_DATA_SOURCES)
        sources_list = [{
            "id": row[0],
            "url": row[1],
            "name": row[2] or row[1], 
            "created_at": row[3].isoformat() if row[3] else None,
            "total_pages": row[4],
            "trained_pages": int(row[5]) if row[5] is not None else 0,
            "status": row[6]
        } for row in rows]
        return success_response({"dataSources": sources_list})
    except Exception as error:
        return error_response(str(error))

def rename_data_source(id: int, request_data: DataSourceRenameRequest):
    try:
        execute_query(RENAME_WEBSITE, {"name": request_data.name, "id": id})
        return success_response()
    except Exception as error:
        return error_response(str(error))

def delete_data_source(id: int):
    try:
        base_url = fetch_one("SELECT base_url FROM websites WHERE id = :id", {"id": id})
        if base_url:
            try:
                db_client = get_weaviate_client()
                delete_chunks_for_website(db_client, base_url[0])
                db_client.close()
            except Exception:
                pass
        
        execute_query(DELETE_CRAWLED_PAGES_BY_WEBSITE, {"id": id})
        execute_query(DELETE_CRAWL_STATUS, {"id": id})
        execute_query(DELETE_WEBSITE, {"id": id})
        return success_response()
    except Exception as error:
        return error_response(str(error))

def get_crawl_status(website_id: int):
    status = crawl_status_tracker.get(website_id)
    if status is not None:
        return status

    try:
        row = fetch_one(GET_CRAWL_STATUS, {"website_id": website_id})
        if row:
            return {"status": row[0], "urls_found": row[1], "error": row[2], "urls": row[3]}
    except Exception:
        pass

    try:
        page_count = fetch_one(COUNT_TOTAL_PAGES, {"id": website_id})[0]
        if page_count and page_count > 0:
            return {"status": "completed", "urls_found": page_count, "urls": []}
    except Exception:
        pass

    return {"status": "not_found"}

def get_datasource_pages(id: int):
    try:
        rows = fetch_all(GET_DATASOURCE_PAGES, {"id": id})
        pages_list = [{
            "id": row[0],
            "page_url": row[1],
            "selected_for_training": row[2],
            "trained": row[3]
        } for row in rows]
        return success_response({"pages": pages_list})
    except Exception as error:
        return error_response(str(error))
