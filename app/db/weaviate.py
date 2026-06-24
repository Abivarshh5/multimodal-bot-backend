import weaviate
from weaviate.classes.config import Configure, Property, DataType
from app.core.config import WEAVIATE_URL, WEAVIATE_API_KEY
from app.core.constants import WEAVIATE_COLLECTION_NAME

def get_weaviate_client():
    if WEAVIATE_URL and WEAVIATE_API_KEY:
        print("Weaviate connected")
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
            skip_init_checks=True
        )
    else:
        print("weaviate not connected")
        return weaviate.connect_to_local()

def ensure_collection(client):
    if not client.collections.exists(WEAVIATE_COLLECTION_NAME):
        client.collections.create(
            name=WEAVIATE_COLLECTION_NAME,
            properties=[
                Property(name="chunk_text", data_type=DataType.TEXT),
                Property(name="page_url", data_type=DataType.TEXT),
                Property(name="website_url", data_type=DataType.TEXT)
            ],
            vectorizer_config=None,
        )

def delete_chunks_for_website(client, website_url: str):
    try:
        collection = client.collections.get(WEAVIATE_COLLECTION_NAME)
        collection.data.delete_many(
            where=weaviate.classes.query.Filter.by_property("website_url").equal(website_url)
        )
        print("chunks deleted")
    except Exception as e:
        print(f"Error deleting chunks for website: {e}")

def delete_chunks_for_page(client, page_url: str):
    try:
        collection = client.collections.get(WEAVIATE_COLLECTION_NAME)
        collection.data.delete_many(
            where=weaviate.classes.query.Filter.by_property("page_url").equal(page_url)
        )
        print("chunks in pg deleted")
    except Exception as e:
        print(f"Error deleting chunks for page: {e}")

def store_chunks_batch(client, chunks, embeddings):
    collection = client.collections.get(WEAVIATE_COLLECTION_NAME)
    print("chunks stored function")
    with collection.batch.dynamic() as batch:
        for chunk, embedding in zip(chunks, embeddings):
            batch.add_object(
                properties={
                    "chunk_text": chunk["chunk_text"],
                    "page_url": chunk["page_url"],
                    "website_url": chunk["website_url"]
                },
                vector=embedding
            )
            print("chunks stored in weaviate")
