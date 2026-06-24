from fastapi import WebSocket
from app.services.groq_service import describe_frame

async def handle_websocket_connection(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            frame_base64 = await websocket.receive_text()
            print("frame received")
            description = describe_frame(frame_base64)
            await websocket.send_text(description)
    except Exception as e:
        print(f"WebSocket closed: {e}")
