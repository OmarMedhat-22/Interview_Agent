"""
Lambda-optimized version using direct HTTP calls instead of litellm
to avoid tiktoken wheel compatibility issues
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import httpx

app = FastAPI(title="Interview Answer Evaluation Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluationRequest(BaseModel):
    question: str
    answer: str
    job_description: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


class CriteriaBreakdown(BaseModel):
    relevance: int
    clarity: int
    depth: int
    impact: int
    job_alignment: Optional[int] = None


class EvaluationResponse(BaseModel):
    score: int
    criteria_breakdown: CriteriaBreakdown
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]


SYSTEM_PROMPT = """You are an expert interview coach. Evaluate the candidate's answer based on:
1. Relevance (0-25): How well does the answer address the question?
2. Clarity (0-20): Is the answer clear, well-structured, and easy to understand?
3. Depth (0-25): Does the answer provide sufficient detail and examples?
4. Impact (0-15): Does the answer demonstrate achievements and value?
5. Job Alignment (0-15): How well does the answer align with the job requirements?

Provide your response in this exact JSON format:
{
    "score": <total score 0-100>,
    "criteria_breakdown": {
        "relevance": <0-25>,
        "clarity": <0-20>,
        "depth": <0-25>,
        "impact": <0-15>,
        "job_alignment": <0-15>
    },
    "summary": "<brief evaluation summary>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}"""


def build_prompt(request: EvaluationRequest) -> str:
    prompt = f"Question: {request.question}\n\nCandidate's Answer: {request.answer}"
    if request.job_description:
        prompt += f"\n\nJob Description: {request.job_description}"
    return prompt


@app.get("/")
async def root():
    return {"message": "Interview Answer Evaluation Agent API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(request: EvaluationRequest):
    model = request.model or os.getenv("MODEL", "gemini-2.5-flash")
    
    # Determine provider and call appropriate API
    if "claude" in model.lower():
        return await call_claude(request, model)
    else:
        return await call_gemini(request, model)


async def call_gemini(request: EvaluationRequest, model: str):
    api_key = request.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
    
    # Clean model name
    model_name = model.replace("gemini/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    full_prompt = SYSTEM_PROMPT + "\n\n" + build_prompt(request)
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        
        data = response.json()
        result_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return parse_response(result_text)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


async def call_claude(request: EvaluationRequest, model: str):
    api_key = request.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")
    
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": SYSTEM_PROMPT + "\n\n" + build_prompt(request)}
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        
        data = response.json()
        result_text = data["content"][0]["text"].strip()
        return parse_response(result_text)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


def parse_response(result_text: str) -> EvaluationResponse:
    # Clean markdown code blocks if present
    if result_text.startswith("```"):
        lines = result_text.split("\n")
        result_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    
    try:
        result = json.loads(result_text)
        return EvaluationResponse(
            score=result["score"],
            criteria_breakdown=CriteriaBreakdown(**result["criteria_breakdown"]),
            summary=result["summary"],
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            improvement_suggestions=result.get("improvement_suggestions", [])
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}")


# AWS Lambda handler
from mangum import Mangum
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
