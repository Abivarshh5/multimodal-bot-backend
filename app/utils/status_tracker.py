# Global trackers for background task status
crawl_status_tracker = {}
training_status_tracker = {}

def update_crawl_status(website_id: int, status: str, urls_found: int = 0, urls: list = None, error: str = None):
    crawl_status_tracker[website_id] = {
        "status": status,
        "urls_found": urls_found,
        "urls": urls or [],
        "error": error
    }

def update_training_status(key, status: str, error: str = None):
    training_status_tracker[key] = {
        "status": status,
        "error": error
    }
