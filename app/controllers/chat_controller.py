from app.services.rag_service import generate_rag_response
from app.models.requests import ChatRequest
from app.utils.formatters import format_chat_history

def handle_chat(request: ChatRequest) -> dict:
    try:
        chat_history = format_chat_history(request.messages)
        user_query = chat_history[-1]["content"] if chat_history else ""
        
        print("chat request received")
        print("user query:", user_query)
        print("website url:", request.website_url)
        print("website id:", request.website_id)
        
        rag_response = generate_rag_response(
            user_query, 
            chat_history, 
            website_url=request.website_url,
            website_id=request.website_id
        )
        ai_reply_text = rag_response["answer"]
        information_sources = rag_response.get("sources", [])

        should_open_camera = "<OPEN_CAMERA>" in ai_reply_text
        should_find_products = "<FIND_PRODUCTS>" in ai_reply_text
        
        clean_reply_text = ai_reply_text.replace("<OPEN_CAMERA>", "").replace("<FIND_PRODUCTS>", "").replace("**", "").strip()
        print("ai-reply - ",ai_reply_text)
        print("info sources - ",information_sources)

        return {
            "reply": clean_reply_text,
            "open_camera": should_open_camera,
            "find_products": should_find_products,
            "sources": information_sources
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "reply": f"Backend error: {str(e)}",
            "open_camera": False,
            "find_products": False,
            "sources": []
        }
