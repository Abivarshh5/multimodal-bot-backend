from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.text_cleaner import preprocess_text
from app.core.constants import CHUNK_SIZE, CHUNK_OVERLAP, WEAVIATE_COLLECTION_NAME
from weaviate.classes.query import Filter, MetadataQuery
from app.db.weaviate import get_weaviate_client
from app.services.embedding_service import get_embedding_model, _FallbackEmbedder
from app.utils.helpers import normalize_url

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,    
    chunk_overlap=CHUNK_OVERLAP,  
    separators=["\n\n", "\n", ". ", ", ", " ", ""],
    keep_separator=True,
    strip_whitespace=True,
)

def chunk_page(text: str, page_url: str, website_url: str, title: str = "", created_at: str = ""):
    cleaned_text = preprocess_text(text)
    if cleaned_text == "":
        return []
        
    raw_text_chunks = text_splitter.split_text(cleaned_text)
    final_chunks_list = []
    chunk_counter = 0
    
    for chunk_piece in raw_text_chunks:
        formatted_chunk = {
            "page_url": page_url,
            "website_url": website_url,
            "chunk_index": chunk_counter,
            "chunk_text": chunk_piece,
            "metadata": {
                "title": title,
                "created_at": created_at,
            },
        }
        final_chunks_list.append(formatted_chunk)
        chunk_counter += 1

    return final_chunks_list

def print_chunks(page_url: str, chunks: list):
    print(f"URL: {page_url}")
    print(f"Total Chunks Generated: {len(chunks)}")
    for chunk in chunks:
        index = chunk["chunk_index"]
        text = chunk["chunk_text"]
        preview_text = text[:100]
        print(f"Chunk {index} Preview: {preview_text}...")

def search_chunks(user_query, limit=5, website_url=None):
    normalized_website_url = normalize_url(website_url) if website_url else None
    print("searching vector db")
    print("search query:", user_query)
    if normalized_website_url:
        print("using website:", normalized_website_url)
    
    model = get_embedding_model()
    query_numbers_raw = model.encode(f"search_query: {user_query}")
    
    try:
        query_numbers = query_numbers_raw.tolist()
    except Exception:
        query_numbers = list(query_numbers_raw)
        
    good_results = []
    skip_words = ["404", "page not found", "toggle theme"]
    
    try:
        db_client = get_weaviate_client()
        if not db_client.collections.exists(WEAVIATE_COLLECTION_NAME):
            db_client.close()
            return []
            
        chunk_collection = db_client.collections.get(WEAVIATE_COLLECTION_NAME)
        search_filter = None
        if normalized_website_url:
            url_with_slash = normalized_website_url + '/'
            search_filter = (
                Filter.by_property("website_url").equal(normalized_website_url) |
                Filter.by_property("website_url").equal(url_with_slash)
            )

        is_fallback = isinstance(model, _FallbackEmbedder)
        print(f"Is Fallback: {is_fallback}")
        
        database_response = chunk_collection.query.hybrid(
            query=user_query,
            vector=query_numbers,
            alpha=0.0 if is_fallback else 0.5,
            limit=limit * 3,
            filters=search_filter,
            return_metadata=MetadataQuery(score=True)
        )
        
        for item in database_response.objects:
            text_content = item.properties.get("chunk_text", "")
            text_lower = text_content.lower()
            
            contains_skip_word = any(word in text_lower for word in skip_words)
            if contains_skip_word:
                continue 
                
            item_url = item.properties.get("page_url", "")
            
            good_results.append({
                "chunk_text": text_content,
                "page_url": item_url,
                "title": item.properties.get("title", ""),
                "score": item.metadata.score if item.metadata and getattr(item.metadata, 'score', None) is not None else 0.0
            })
            
            if len(good_results) >= limit:
                break
                
        db_client.close()
    except Exception as error:
        print(f"error in database: {error}")
        
    print("vector results:",good_results)
    for res in good_results:
        print("chunk text:", res["chunk_text"][:200])
        print("score:", res["score"])
        print("page:", res["page_url"])
        
    return good_results

def build_context(search_results):
    final_text_pieces = []
    total_characters = 0
    max_characters = 16000
    
    result_counter = 1
    for result in search_results[:20]:
        page_link = result.get("page_url", "")
        page_content = result.get("chunk_text", "")
        
        formatted_piece = f"[Source {result_counter}]\nURL: {page_link}\n\nContent:\n{page_content}\n\n---\n\n"
        
        if total_characters + len(formatted_piece) > max_characters:
            if result_counter == 1:
                formatted_piece = formatted_piece[:max_characters]
                final_text_pieces.append(formatted_piece)
            break
            
        final_text_pieces.append(formatted_piece)
        total_characters += len(formatted_piece)
        result_counter += 1
        
    combined_context = "".join(final_text_pieces).strip()
    if combined_context.endswith("---"):
        combined_context = combined_context[:-3].strip()
        print("combined text", combined_context)
    return combined_context
