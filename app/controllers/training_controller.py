import threading
from app.db.postgres import execute_query, fetch_one
from app.db.queries import (TOGGLE_PAGE_TRAINING, SELECT_ALL_PAGES, RESET_TRAINED_STATUS, GET_PAGE_URL, DELETE_PAGE,COUNT_TOTAL_PAGES, COUNT_SELECTED_PAGES, COUNT_TRAINED_PAGES, FIND_WEBSITE_BY_ID, FIND_WEBSITE_BY_URL)
from app.db.weaviate import get_weaviate_client, delete_chunks_for_page
from app.models.requests import SelectAllRequest
from app.utils.response import success_response, error_response
from app.utils.helpers import normalize_url
from app.utils.status_tracker import training_status_tracker
from app.services.training_service import run_background_training
from app.utils.async_utils import run_async_task

def _start_background_training(id: int, website_url: str):
    run_async_task(run_background_training(id, website_url))

def toggle_page_training(id: int):
    try:
        execute_query(TOGGLE_PAGE_TRAINING, {"id": id})
        return success_response()
    except Exception as error:
        return error_response(str(error))

def select_all_pages(id: int, request_data: SelectAllRequest):
    try:
        execute_query(SELECT_ALL_PAGES, {"id": id, "select": request_data.select})
        return success_response()
    except Exception as error:
        return error_response(str(error))

def delete_page(id: int):
    try:
        page_url_row = fetch_one(GET_PAGE_URL, {"id": id})
        if page_url_row:
            try:
                db_client = get_weaviate_client()
                delete_chunks_for_page(db_client, page_url_row[0])
                db_client.close()
            except Exception:
                pass

        execute_query(DELETE_PAGE, {"id": id})
        return success_response()
    except Exception as error:
        return error_response(str(error))

def start_datasource_training(id: int):
    try:
        row = fetch_one(FIND_WEBSITE_BY_ID, {"id": id})
        if not row:
            return error_response("Datasource not found")
            
        website_url = normalize_url(row[0])
        training_status_tracker[website_url] = {"status": "training"}
        training_status_tracker[id] = {"status": "training"}

        background_thread = threading.Thread(target=_start_background_training, args=(id, website_url), daemon=True)
        background_thread.start()
        
        return success_response({"message": "Training started", "url": website_url})
    except Exception as error:
        return error_response(str(error))

def retrain_data_source(id: int):
    try:
        execute_query(RESET_TRAINED_STATUS, {"id": id})
        
        row = fetch_one(FIND_WEBSITE_BY_ID, {"id": id})
        if not row:
            return error_response("Datasource not found")
            
        website_url = normalize_url(row[0])
        training_status_tracker[website_url] = {"status": "training"}
        training_status_tracker[id] = {"status": "training"}

        background_thread = threading.Thread(target=_start_background_training, args=(id, website_url), daemon=True)
        background_thread.start()

        return success_response({"message": "Retrain started"})
    except Exception as error:
        return error_response(str(error))

def get_training_progress(id: int):
    try:
        total_pages = fetch_one(COUNT_TOTAL_PAGES, {"id": id})[0]
        total_selected = fetch_one(COUNT_SELECTED_PAGES, {"id": id})[0]
        trained_count = fetch_one(COUNT_TRAINED_PAGES, {"id": id})[0]
        return success_response({
            "total_pages": total_pages, 
            "total_selected": total_selected, 
            "trained_count": trained_count
        })
    except Exception as error:
        return error_response(str(error))

def get_training_status(url: str):
    normalized = normalize_url(url)
    status = training_status_tracker.get(normalized)
    if status is not None:
        return status

    try:
        row = fetch_one(FIND_WEBSITE_BY_URL, {"url": normalized, "url_slash": normalized + "/"})
        if row:
            wid = row[0]
            status = training_status_tracker.get(wid)
            if status is not None:
                return status
    except Exception:
        pass

    return {"status": "not_running"}
