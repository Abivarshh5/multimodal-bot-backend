from app.services.vector_service import search_chunks, build_context
from app.services.groq_service import call_llm
from app.prompts.chat_prompt import CHAT_SYSTEM

def generate_rag_response(user_query: str, chat_history: list, website_url: str = None, website_id: int = None) -> dict:
    search_results = search_chunks(user_query, website_url=website_url)
    
    context_text = ""
    print("chunk count:", len(search_results))
    if search_results:
        print("found matching chunks in db")
        print("using only retrieved context")
        context_text = build_context(search_results)
    elif website_url:
        print("no chunks found")
        print("no hallucinating")
        context_text = "No relevant information found in the database for this query. You MUST politely state that you do not have information about this from our store and avoid making up an answer."
    else:
        print("no website provided, using normal chat mode")

    system_instructions = CHAT_SYSTEM

    if website_id:
        from app.services.branding_service import get_branding
        branding = get_branding(website_id)
        if branding:
            system_instructions += f"BRAND INFORMATION\n"
            system_instructions += f"- Store Name: {branding.get('company_name', 'Unknown')}\n"
            system_instructions += f"- Theme Color: {branding.get('primary_color', 'Unknown')}\n"
            system_instructions += "Use this brand information to act like the official assistant of this store.\n\n"

    if website_url:
        system_instructions += "DATASOURCE KNOWLEDGE\n"
        system_instructions += "Use the provided website knowledge below to answer the user's question.\n"
        system_instructions += "CRITICAL RULE FOR OUT-OF-DOMAIN/IRRELEVANT REQUESTS (INCLUDING CAMERA DESCRIPTIONS):\n"
        system_instructions += "First analyze and understand the detected product from the image or user input.\n"
        system_instructions += "If the product is not relevant to the available catalog/knowledge base (e.g., a shirt or kurti on a stationery website), briefly and naturally describe the detected product, politely say that you do not have enough information or matching catalog data for that item, and do not force unrelated recommendations. You MUST NOT append <FIND_PRODUCTS>.\n"
        system_instructions += "Example tone: 'Yeah, this looks like a stylish kurti with floral patterns... But it seems this product is outside our current stationery store catalog... Feel free to ask me about notebooks, pens, desk accessories, or other stationery products 😊'\n"
        system_instructions += "CRITICAL RULE FOR PRODUCT DISCOVERY (IN-DOMAIN ONLY):\n"
        system_instructions += "If the product is relevant to the available catalog/knowledge base (e.g., the user shows a dress/kurti to a clothing store, or a notebook to a stationery store), respond naturally, confidently, and enthusiastically. NEVER use negative phrasing like 'Unfortunately, I don't have enough information' or 'While we don't have an exact match'. Briefly describe the detected product in a friendly tone, enthusiastically state that you have found wonderful similar products in our collection, and append exactly <FIND_PRODUCTS> at the end so we can display the visual product cards.\n"
        system_instructions += "ADDITIONAL CONSTRAINTS:\n"
        system_instructions += "1. Never incorrectly reject products that belong to the catalog.\n"
        system_instructions += "2. Never mention internal logic, embeddings, vector DB, or knowledge-base checks to the user.\n"
        system_instructions += "3. Keep responses concise, friendly, and conversational.\n"
        system_instructions += "4. Avoid repetitive or robotic wording.\n"
        system_instructions += "5. If answering general questions (not product discovery), you MUST include the exact source link (URL) provided in the knowledge context.\n"
        system_instructions += "6. Do NOT use any markdown formatting (NO asterisks `**` or `*`, NO bold, NO italics, NO lists) in your response.\n"
        system_instructions += "7. Do not make up answers. You must still follow rules like using <OPEN_CAMERA> if needed.\n\n"
        system_instructions += "WEBSITE KNOWLEDGE:\n"
        system_instructions += context_text

    chat_messages = [{"role": "system", "content": system_instructions}]
    chat_messages.extend(chat_history)
    
    if not chat_history:
        chat_messages.append({"role": "user", "content": user_query})
        
    print("final rag context:")
    print(context_text[:500] if context_text else "none")
    print("final prompt sent to llm:")
    print(chat_messages)
        
    ai_answer = call_llm(chat_messages, max_tokens=150)
    
    print("checking if response matches retrieved data")
    print("final bot answer:")
    print(ai_answer)
    
    unique_links = []
    source_list = []
    
    for result in search_results:
        link = result.get("page_url", "")
        if link and link not in unique_links:
            unique_links.append(link)
            source_list.append({
                "title": result.get("title", "Website Page"),
                "page_url": link
            })
            
    return {
        "answer": ai_answer,
        "sources": source_list
    }
