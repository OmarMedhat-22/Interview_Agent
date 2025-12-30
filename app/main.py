from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import json
import litellm

load_dotenv()

# Disable telemetry and token counting to avoid network issues
litellm.telemetry = False
litellm.drop_params = True

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
    model: Optional[str] = None  # Override default model
    api_key: Optional[str] = None  # Override default API key


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


SYSTEM_PROMPT = """You are an Interview Answer Evaluation Agent that evaluates candidate interview answers using concise reasoning and structured scoring.

Evaluation Criteria:
- Relevance (25%): Directly answers the question
- Clarity & Structure (20%): Logical, concise, easy to follow
- Depth & Evidence (25%): Uses examples, results, or concrete reasoning
- Impact & Professionalism (15%): Demonstrates value, ownership, confidence
- Job Alignment (15%): Matches required skills (only if job_description exists)

If job_description is not provided, redistribute its weight proportionally.

Scoring: 0-100 (90-100 Excellent, 75-89 Good, 60-74 Average, 40-59 Weak, 0-39 Very weak)

Return ONLY valid JSON:
{"score": 0, "criteria_breakdown": {"relevance": 0, "clarity": 0, "depth": 0, "impact": 0, "job_alignment": null}, "summary": "", "strengths": [], "weaknesses": [], "improvement_suggestions": []}

No markdown, no explanation. Only valid JSON."""


def build_prompt(request: EvaluationRequest) -> str:
    content = "Evaluate:\nQuestion: " + request.question + "\nAnswer: " + request.answer
    if request.job_description:
        content += "\nJob Description: " + request.job_description
    else:
        content += "\nJob Description: Not provided"
    return content


@app.get("/")
async def root():
    return {"message": "Interview Answer Evaluation Agent API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "default_model": os.getenv("MODEL", "gemini/gemini-2.0-flash"),
        "gemini_models": [
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.5-pro",
            "gemini/gemini-2.0-flash",
            "gemini/gemini-2.0-flash-lite",
        ],
        "claude_models": [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
        ]
    }


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(request: EvaluationRequest):
    # Use request model/api_key if provided, otherwise use env defaults
    model = request.model or os.getenv("MODEL", "gemini/gemini-2.0-flash")
    
    # Set API key based on provider
    if request.api_key:
        if "claude" in model.lower() or request.api_key.startswith("sk-ant"):
            os.environ["ANTHROPIC_API_KEY"] = request.api_key
        else:
            os.environ["GEMINI_API_KEY"] = request.api_key
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(request)}
    ]
    
    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=1024
        )
        
        result_text = response.choices[0].message.content.strip()
        
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
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
        raise HTTPException(status_code=500, detail="Failed to parse LLM response: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Evaluation failed: " + str(e))


# AWS Lambda handler
from mangum import Mangum
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
