from fastapi import APIRouter, HTTPException
from app.models.schemas import ExplainRequest, ExplainResponse
from app.services.gemini_service import model
from app.services.translate_service import translate_to_hindi
import json
import re

router = APIRouter(prefix="/api", tags=["explain"])

# Simple in-memory cache: {(topic, lang): ExplainResponse}
_explain_cache = {}

VALID_TOPICS = [
    "EVM", "NOTA", "manifesto", "voter_id",
    "booth", "election_commission", "mcc", "counting",
    "ink", "candidate", "constituency", "voting_process"
]

EXPLAIN_PROMPT_TEMPLATE = """Explain the Indian election topic "{topic}" in simple language using Desi Wedding (Shaadi) analogies.

Respond ONLY with a valid JSON object in this exact format:
{{
    "shaadi_analogy": "The desi wedding comparison (1-2 sentences)",
    "simple_explanation": "2-3 sentences plain language explanation",
    "action_step": "What the user should do next (1 sentence)",
    "fun_fact": "An interesting election fact (1 sentence)"
}}

Rules:
- Use wedding analogies (shaadi, mehndi, mandap, baraat, dulha/dulhan, etc.)
- Keep it fun and friendly like "Chunav Mitra"
- Make it easy for common people to understand
- Action step should be practical and actionable
- Fun fact should be surprising or interesting
"""


def parse_json_response(text: str) -> dict:
    """Safely parse JSON from Gemini response, handling markdown code blocks."""
    try:
        # Try direct parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try extracting just the JSON object with regex
    json_match = re.search(r'\{[\s\S]*?\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


@router.post("/explain", response_model=ExplainResponse)
async def explain_topic(req: ExplainRequest):
    """
    Explain an election topic with shaadi analogies.
    Returns structured explanation with analogy, steps, and fun fact.
    """
    topic = req.topic.strip()
    lang = req.lang if req.lang in ["hi", "en"] else "en"

    # Validate topic
    topic_upper = topic.upper()
    topic_lower = topic.lower()

    valid_topic = None
    for vt in VALID_TOPICS:
        if topic_upper == vt.upper() or topic_lower == vt.lower():
            valid_topic = vt
            break

    if not valid_topic:
        valid_topic = topic  # Use as-is if not in list

    # Check cache first
    cache_key = (valid_topic.lower(), lang)
    if cache_key in _explain_cache:
        cached = _explain_cache[cache_key]
        return ExplainResponse(
            topic=valid_topic,
            shaadi_analogy=cached.shaadi_analogy,
            simple_explanation=cached.simple_explanation,
            action_step=cached.action_step,
            fun_fact=cached.fun_fact,
            lang=lang
        )

    # Generate explanation using Gemini
    prompt = EXPLAIN_PROMPT_TEMPLATE.format(topic=valid_topic)

    try:
        response = model.generate_content(prompt)
        parsed = parse_json_response(response.text)

        if not parsed:
            # Fallback response if parsing fails
            parsed = {
                "shaadi_analogy": f"{valid_topic} is like the wedding venue where all the important decisions happen!",
                "simple_explanation": f"This is a key part of the election process that helps democracy function smoothly.",
                "action_step": "Check out the voter education section on ECI website for more details.",
                "fun_fact": "India is the world's largest democracy with over 900 million eligible voters!"
            }

        # Extract fields with fallbacks
        shaadi_analogy = parsed.get("shaadi_analogy", "")
        simple_explanation = parsed.get("simple_explanation", "")
        action_step = parsed.get("action_step", "")
        fun_fact = parsed.get("fun_fact", "")

        # Translate to Hindi if requested
        if lang == "hi":
            try:
                shaadi_analogy = translate_to_hindi(shaadi_analogy)
                simple_explanation = translate_to_hindi(simple_explanation)
                action_step = translate_to_hindi(action_step)
                fun_fact = translate_to_hindi(fun_fact)
            except Exception:
                pass  # Use original if translation fails

        # Create response
        explain_response = ExplainResponse(
            topic=valid_topic,
            shaadi_analogy=shaadi_analogy,
            simple_explanation=simple_explanation,
            action_step=action_step,
            fun_fact=fun_fact,
            lang=lang
        )

        # Cache the response
        _explain_cache[cache_key] = explain_response

        return explain_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )
