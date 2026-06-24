import groq
from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.core.config import GROQ_API_KEY
from app.core.constants import TEXT_MODEL, VISION_MODEL

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=20),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(groq.InternalServerError)
)
def call_llm(messages, max_tokens=150, json_mode=False):
    client = Groq(api_key=GROQ_API_KEY)
    kwargs = {
        "model": TEXT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=20),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(groq.InternalServerError)
)
def describe_frame(frame_b64: str) -> str:
    prompt = (
        "You are an expert product identification assistant. "
        "Analyze the image to identify the primary product being displayed or showcased in the frame. "
        "CRITICAL PRIORITY RULE: "
        "1. FOREGROUND OBJECTS HELD IN HAND: If a person is holding a specific item up in their hand or presenting it towards the camera (such as a watch, jewelry, phone, bottle, or gadget), this object is the absolute main focus. You MUST identify and describe this item in detail, completely ignoring the person's background clothing or sleeves. "
        "2. CLOTHING & APPAREL: Only if the person is NOT holding any object up to the camera, and is instead standing or sitting to showcase their outfit, then you should identify and describe their clothing (dress, kurti, shirt, etc.) as the primary product. "
        "Describe the identified product in 1-2 concise sentences, including relevant details like color, material, pattern, and notable design elements useful for shopping recommendations. "
        "Do not guess unknown information. If a feature is unclear, simply omit it. "
        "Examples: "
        "'An elegant wristwatch with a white dial, rose gold bezel, and beige leather strap.' "
        "'A vibrant red floral printed summer dress with a v-neckline.' "
        "If no clear product, person, or object is visible in the frame at all, respond exactly with: 'no product detected'."
    )
    
    print("sending frame to groq vision")
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}},
                {"type": "text", "text": prompt}
            ]
        }],
        max_tokens=100
    )
    ans = response.choices[0].message.content.strip()
    print("vision response:")
    print(ans)
    return ans
