from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


app = FastAPI(
    title="Sally Beauty AI LinkedIn Content Studio",
    description="AutoGen-style multi-agent microservice for LinkedIn content automation.",
    version="2.0.0"
)


class LinkedInRequest(BaseModel):
    brand: str = Field(..., example="Sally Beauty")
    industry: str = Field(..., example="Beauty Retail")
    topic: str = Field(..., example="AI-driven personalization in beauty retail")
    audience: str = Field(..., example="Retail Executives, Beauty Professionals, Technology Leaders")
    tone: str = Field(..., example="professional and welcoming")
    content_pillar: str = Field(
        default="Digital Transformation",
        example="Digital Transformation"
    )
    call_to_action: str = Field(
        default="Explore how innovation is shaping the future of beauty retail.",
        example="Explore how innovation is shaping the future of beauty retail."
    )
    dry_run: bool = Field(default=True, example=True)
    min_confidence: float = Field(default=0.75, example=0.75)
    destination: str = Field(default="Google Drive", example="Google Drive")


class AgentOutput(BaseModel):
    agent_name: str
    role: str
    output: Dict[str, Any]


class LinkedInResponse(BaseModel):
    status: str
    generated_at: str
    brand: str
    topic: str
    agent_trace: List[AgentOutput]
    ideas: List[str]
    draft_post: str
    hashtags: List[str]
    confidence_score: float
    approval_required: bool
    routing_recommendation: str
    dry_run: bool
    destination: str
    final_post_preview: str
    log_summary: Dict[str, Any]


@app.get("/")
def root():
    return {
        "status": "running",
        "project": "Sally Beauty AI LinkedIn Content Studio",
        "version": "2.0.0",
        "architecture": "AutoGen-style multi-agent FastAPI microservice"
    }


def idea_agent(request: LinkedInRequest) -> Dict[str, Any]:
    """
    Simulates an AutoGen-style idea generation agent.
    """

    ideas = [
        f"How {request.topic} is transforming {request.industry}",
        f"Why {request.industry} leaders should pay attention to {request.content_pillar}",
        f"How {request.brand} can inspire more confident customer experiences through innovation",
        f"What beauty retail teams can learn from AI-powered personalization",
        f"How data-driven experiences are reshaping the future of beauty commerce"
    ]

    return {
        "ideas": ideas,
        "selected_idea": ideas[0],
        "reasoning": "Selected the first idea because it connects the topic, industry, and business value clearly."
    }


def draft_agent(request: LinkedInRequest, selected_idea: str) -> Dict[str, Any]:
    """
    Simulates an AutoGen-style drafting agent.
    """

    draft_post = f"""
At {request.brand}, innovation is not just about technology. It is about creating more meaningful, personalized, and welcoming experiences.

{request.topic} is opening new possibilities for {request.industry} teams to better understand customers, improve engagement, and deliver experiences that feel more relevant.

For {request.audience}, this shift represents an opportunity to connect data, creativity, and service in a way that strengthens both customer confidence and business outcomes.

As the industry continues to evolve, brands that combine responsible technology with a clear customer purpose will be better positioned to grow.

{request.call_to_action}
""".strip()

    return {
        "draft_post": draft_post,
        "selected_idea": selected_idea,
        "tone_used": request.tone,
        "content_pillar": request.content_pillar
    }


def hashtag_agent(request: LinkedInRequest) -> Dict[str, Any]:
    """
    Simulates an AutoGen-style hashtag generation agent.
    """

    hashtags = [
        "#SallyBeauty",
        "#BeautyRetail",
        "#RetailTechnology",
        "#AI",
        "#DigitalTransformation",
        "#CustomerExperience",
        "#Innovation"
    ]

    if "personalization" in request.topic.lower():
        hashtags.append("#Personalization")

    if "data" in request.topic.lower():
        hashtags.append("#DataDriven")

    return {
        "hashtags": hashtags,
        "hashtag_count": len(hashtags)
    }


def guardrail_agent(
    request: LinkedInRequest,
    draft_post: str,
    hashtags: List[str]
) -> Dict[str, Any]:
    """
    Simulates approval and confidence scoring.
    """

    base_score = 0.82

    if request.brand.lower() in draft_post.lower():
        base_score += 0.03

    if request.topic.lower().split()[0] in draft_post.lower():
        base_score += 0.03

    if len(hashtags) >= 4:
        base_score += 0.02

    confidence_score = round(min(base_score, 0.96), 2)

    approval_required = confidence_score < request.min_confidence

    policy_notes = [
        "No sensitive customer data included.",
        "No unsupported financial or medical claims included.",
        "Post is suitable for professional LinkedIn review.",
        "Human approval recommended before live publishing."
    ]

    return {
        "confidence_score": confidence_score,
        "approval_required": approval_required,
        "min_confidence": request.min_confidence,
        "policy_notes": policy_notes
    }


def routing_agent(
    request: LinkedInRequest,
    approval_required: bool
) -> Dict[str, Any]:
    """
    Simulates routing logic for n8n approval gate.
    """

    if request.dry_run:
        routing_recommendation = "Route to review destination because dry_run is enabled."
        route = "review"
    elif approval_required:
        routing_recommendation = "Route to approval queue because confidence is below threshold."
        route = "approval_required"
    else:
        routing_recommendation = "Ready for publishing workflow."
        route = "publish_ready"

    return {
        "route": route,
        "routing_recommendation": routing_recommendation,
        "destination": request.destination,
        "dry_run": request.dry_run
    }


@app.post("/linkedin", response_model=LinkedInResponse)
def generate_linkedin_content(request: LinkedInRequest):

    generated_at = datetime.utcnow().isoformat() + "Z"

    # Agent 1: Idea generation
    idea_result = idea_agent(request)

    # Agent 2: Draft generation
    draft_result = draft_agent(
        request=request,
        selected_idea=idea_result["selected_idea"]
    )

    # Agent 3: Hashtag generation
    hashtag_result = hashtag_agent(request)

    # Agent 4: Guardrail and confidence scoring
    guardrail_result = guardrail_agent(
        request=request,
        draft_post=draft_result["draft_post"],
        hashtags=hashtag_result["hashtags"]
    )

    # Agent 5: Routing recommendation
    routing_result = routing_agent(
        request=request,
        approval_required=guardrail_result["approval_required"]
    )

    final_post_preview = (
        draft_result["draft_post"]
        + "\n\n"
        + " ".join(hashtag_result["hashtags"])
    )

    agent_trace = [
        AgentOutput(
            agent_name="Idea Agent",
            role="Generates multiple LinkedIn post ideas.",
            output=idea_result
        ),
        AgentOutput(
            agent_name="Draft Agent",
            role="Creates the LinkedIn draft post.",
            output=draft_result
        ),
        AgentOutput(
            agent_name="Hashtag Agent",
            role="Generates relevant hashtags.",
            output=hashtag_result
        ),
        AgentOutput(
            agent_name="Guardrail Agent",
            role="Scores confidence and determines approval requirement.",
            output=guardrail_result
        ),
        AgentOutput(
            agent_name="Routing Agent",
            role="Determines dry-run, review, or publishing route.",
            output=routing_result
        )
    ]

    log_summary = {
        "generated_at": generated_at,
        "brand": request.brand,
        "industry": request.industry,
        "topic": request.topic,
        "confidence_score": guardrail_result["confidence_score"],
        "approval_required": guardrail_result["approval_required"],
        "dry_run": request.dry_run,
        "destination": request.destination,
        "route": routing_result["route"]
    }

    return LinkedInResponse(
        status="success",
        generated_at=generated_at,
        brand=request.brand,
        topic=request.topic,
        agent_trace=agent_trace,
        ideas=idea_result["ideas"],
        draft_post=draft_result["draft_post"],
        hashtags=hashtag_result["hashtags"],
        confidence_score=guardrail_result["confidence_score"],
        approval_required=guardrail_result["approval_required"],
        routing_recommendation=routing_result["routing_recommendation"],
        dry_run=request.dry_run,
        destination=request.destination,
        final_post_preview=final_post_preview,
        log_summary=log_summary
    )