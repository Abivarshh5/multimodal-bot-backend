# websites table
FIND_WEBSITE_BY_URL = "SELECT id, base_url FROM websites WHERE base_url = :url OR base_url = :url_slash LIMIT 1"
FIND_WEBSITE_BY_ID = "SELECT base_url FROM websites WHERE id = :id"
INSERT_WEBSITE = "INSERT INTO websites (tenant_id, base_url, created_at) VALUES (:tenant_id, :base_url, NOW()) RETURNING id"
RENAME_WEBSITE = "UPDATE websites SET name = :name WHERE id = :id"
DELETE_WEBSITE = "DELETE FROM websites WHERE id = :id"

GET_ALL_DATA_SOURCES = """
    SELECT w.id, w.base_url, w.name, w.created_at, COUNT(c.id) as total_pages,
           SUM(CASE WHEN c.trained = TRUE THEN 1 ELSE 0 END) as trained_pages,
           cs.status
    FROM websites w
    LEFT JOIN crawled_pages c ON w.id = c.website_id
    LEFT JOIN crawl_status cs ON w.id = cs.website_id
    GROUP BY w.id, cs.status
    ORDER BY w.created_at DESC
"""

UPSERT_CRAWLED_PAGE = """
    INSERT INTO crawled_pages (website_id, website_url, page_url, selected_for_training, trained, created_at) 
    VALUES (:website_id, :website_url, :page_url, FALSE, FALSE, NOW()) 
    ON CONFLICT (page_url) DO UPDATE SET website_id = EXCLUDED.website_id, website_url = EXCLUDED.website_url
"""
GET_UNTRAINED_SELECTED_PAGES = "SELECT id, page_url FROM crawled_pages WHERE website_id = :id AND selected_for_training = TRUE AND trained = FALSE"
UPDATE_PAGE_CONTENT = "UPDATE crawled_pages SET markdown_content = :content, raw_text = :content WHERE page_url = :url"
MARK_PAGES_TRAINED = "UPDATE crawled_pages SET trained = TRUE WHERE id = ANY(:ids)"
GET_DATASOURCE_PAGES = "SELECT id, page_url, selected_for_training, trained FROM crawled_pages WHERE website_id = :id ORDER BY id ASC"
TOGGLE_PAGE_TRAINING = "UPDATE crawled_pages SET selected_for_training = NOT selected_for_training WHERE id = :id"
GET_PAGE_URL = "SELECT page_url FROM crawled_pages WHERE id = :id"
DELETE_PAGE = "DELETE FROM crawled_pages WHERE id = :id"
DELETE_CRAWLED_PAGES_BY_WEBSITE = "DELETE FROM crawled_pages WHERE website_id = :id"
SELECT_ALL_PAGES = "UPDATE crawled_pages SET selected_for_training = :select WHERE website_id = :id AND trained = FALSE"
COUNT_TOTAL_PAGES = "SELECT count(*) FROM crawled_pages WHERE website_id = :id"
COUNT_SELECTED_PAGES = "SELECT count(*) FROM crawled_pages WHERE website_id = :id AND selected_for_training = TRUE"
COUNT_TRAINED_PAGES = "SELECT count(*) FROM crawled_pages WHERE website_id = :id AND selected_for_training = TRUE AND trained = TRUE"
RESET_TRAINED_STATUS = "UPDATE crawled_pages SET trained = FALSE WHERE website_id = :id AND selected_for_training = TRUE"

# crawl_status table
UPSERT_CRAWL_STATUS = """
    INSERT INTO crawl_status (website_id, status, urls_found, error, last_updated)
    VALUES (:website_id, :status, :urls_found, :error, CURRENT_TIMESTAMP)
    ON CONFLICT (website_id) DO UPDATE SET 
        status = EXCLUDED.status,
        urls_found = EXCLUDED.urls_found,
        error = EXCLUDED.error,
        urls = :urls,
        last_updated = CURRENT_TIMESTAMP
"""
GET_CRAWL_STATUS = "SELECT status, urls_found, error, urls FROM crawl_status WHERE website_id = :website_id"
DELETE_CRAWL_STATUS = "DELETE FROM crawl_status WHERE website_id = :id"

# tables creation
CREATE_CRAWLED_PAGES_TABLE = """
CREATE TABLE IF NOT EXISTS crawled_pages (
    id SERIAL PRIMARY KEY,
    website_id INTEGER,
    website_url TEXT,
    page_url TEXT UNIQUE,
    markdown_content TEXT,
    raw_text TEXT,
    selected_for_training BOOLEAN DEFAULT FALSE,
    trained BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
"""
CREATE_WEBSITES_TABLE = """
CREATE TABLE IF NOT EXISTS websites (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER,
    base_url TEXT,
    name TEXT,
    created_at TIMESTAMP
);
"""
CREATE_CRAWL_STATUS_TABLE = """
CREATE TABLE IF NOT EXISTS crawl_status (
    website_id INTEGER PRIMARY KEY,
    status VARCHAR(50),
    urls_found INTEGER DEFAULT 0,
    error TEXT,
    urls JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
ADD_URLS_COLUMN = "ALTER TABLE crawl_status ADD COLUMN IF NOT EXISTS urls JSONB"

CREATE_BRAND_PROFILE_TABLE = """
CREATE TABLE IF NOT EXISTS brand_profile (
    id SERIAL PRIMARY KEY,
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE UNIQUE,
    company_name TEXT,
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

UPSERT_BRAND_PROFILE = """
    INSERT INTO brand_profile (website_id, company_name, logo_url, favicon_url, primary_color, created_at)
    VALUES (:website_id, :company_name, :logo_url, :favicon_url, :primary_color, NOW())
    ON CONFLICT (website_id) DO UPDATE SET
        company_name = EXCLUDED.company_name,
        logo_url = EXCLUDED.logo_url,
        favicon_url = EXCLUDED.favicon_url,
        primary_color = EXCLUDED.primary_color
"""

GET_BRAND_PROFILE = "SELECT company_name, logo_url, favicon_url, primary_color FROM brand_profile WHERE website_id = :website_id"
DELETE_BRAND_PROFILE = "DELETE FROM brand_profile WHERE website_id = :website_id"
