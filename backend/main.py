from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
