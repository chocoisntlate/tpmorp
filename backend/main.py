from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
import json
from datetime import datetime

from retpmorp import invert_text


# Request schema
class InvertRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    random_word_reversal: float = Field(0.0, ge=0, le=1)
    random_language_swap: float = Field(0.0, ge=0, le=1)
    languages: Optional[List[str]] = Field(default=None)
    model: str = Field(default="llama2")


# Response schema
class InvertResponse(BaseModel):
    original: str
    inverted: str


# Initialize FastAPI app
app = FastAPI(title="OppositeGPT", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/invert", response_model=InvertResponse)
async def invert_endpoint(request: InvertRequest) -> InvertResponse:
    """
    Invert the semantic meaning of input text with optional transformations.
    """
    try:
        inverted = invert_text(
            prompt=request.prompt,
            random_word_reversal=request.random_word_reversal,
            random_language_swap=request.random_language_swap,
            languages=request.languages or [],
            model=request.model,
        )
        return InvertResponse(original=request.prompt, inverted=inverted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Simple in-memory chat history storage
chat_histories: Dict[str, List[Dict]] = {}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.

    Expected message format:
    {
        "message": "user message",
        "session_id": "optional-session-id",
        "model": "llama2"
    }
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                session_id = message_data.get("session_id", "default")
                model = message_data.get("model", "llama2")

                # Initialize chat history for new sessions
                if session_id not in chat_histories:
                    chat_histories[session_id] = []

                # Add user message to history
                chat_histories[session_id].append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                })

                # Send acknowledgment
                await websocket.send_json({
                    "type": "user_message_received",
                    "message": user_message,
                    "session_id": session_id
                })

                # Process with LLM (using invert_text for demo)
                try:
                    ai_response = invert_text(
                        prompt=user_message,
                        model=model
                    )

                    # Add AI response to history
                    chat_histories[session_id].append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })

                    # Send AI response
                    await websocket.send_json({
                        "type": "ai_response",
                        "message": ai_response,
                        "session_id": session_id,
                        "history_length": len(chat_histories[session_id])
                    })

                except Exception as llm_error:
                    await websocket.send_json({
                        "type": "error",
                        "error": f"LLM error: {str(llm_error)}"
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        if session_id:
            print(f"Client disconnected. Session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
