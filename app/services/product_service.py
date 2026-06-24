import json
from app.services.vector_service import search_chunks, build_context
from app.prompts.product_prompt import DATA_SOURCE_PRODUCTS_SYSTEM, PRODUCTS_SYSTEM
from app.services.groq_service import call_llm

def find_products(description: str, website_url: str = None) -> dict:
    print("finding products for:")
    print(description)
    
    background_knowledge = ""
    if website_url:
        database_matches = search_chunks(description, limit=20, website_url=website_url)
        if database_matches:
            background_knowledge = "\n\nAvailable Products Context:\n" + build_context(database_matches)
        else:
            print("no matching products found in database")
            return {
                "message": "I couldn't find any information about this product in our store. Would you like to explore our other items?",
                "products": []
            }
            
    if website_url:
        ai_prompt = f"Find similar products for: {description}\n\n{background_knowledge}"
        ai_system_instructions = DATA_SOURCE_PRODUCTS_SYSTEM
    else:
        ai_prompt = f"Find similar products for: {description}\n\nGenerate similar hypothetical products because no website was provided."
        ai_system_instructions = PRODUCTS_SYSTEM
    
    messages = [
        {"role": "system", "content": ai_system_instructions}, 
        {"role": "user", "content": ai_prompt}
    ]
    
    print("product context:")
    print(background_knowledge[:500] if background_knowledge else "none")
    
    raw_ai_text = call_llm(messages, max_tokens=600, json_mode=True)
    
    try:
        clean_json_text = raw_ai_text.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(clean_json_text)
        print("generated products:")
        print(parsed_json)
    except Exception as error:
        print(f"Failed to read AI's JSON: {error}")
        parsed_json = {"message": "I couldn't find any matching products.", "products": []}
        
    return parsed_json
