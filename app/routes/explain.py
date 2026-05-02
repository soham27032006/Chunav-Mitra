"""
Module: explain.py
Description: Dictionary and topic explanation routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import re

from fastapi import APIRouter, HTTPException

from app.models.schemas import ExplainRequest, ExplainResponse
from app.services import gemini_service
from app.services.translate_service import translate_to_hindi
from app.utils.cache import cache
from app.utils.logger import get_logger
from app.utils.validators import validate_language, validate_topic

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["explain"])

TOPIC_ALIASES = {
    "evm": "EVM",
    "nota": "NOTA",
    "manifesto": "Manifesto",
    "voter id": "Voter ID",
    "voter_id": "Voter ID",
    "booth": "Booth",
    "election commission": "Election Commission",
    "election_commission": "Election Commission",
    "model code": "Model Code",
    "mcc": "Model Code",
    "vote counting": "Vote Counting",
    "counting": "Vote Counting",
}

LOCAL_EXPLAINERS = {
    "EVM": {
        "shaadi_analogy": {
            "en": "EVM is like the final decision button at the wedding mandap where the shagun reaches the right place directly.",
            "hi": "ईवीएम शादी के मंडप के उस अंतिम निर्णय बटन की तरह है जहाँ शगुन सीधे सही जगह पहुँचता है।",
        },
        "simple_explanation": {
            "en": "EVM stands for Electronic Voting Machine. This is the machine on which a voter securely casts a vote.",
            "hi": "ईवीएम का पूरा नाम इलेक्ट्रॉनिक वोटिंग मशीन है। इसी मशीन पर मतदाता सुरक्षित रूप से अपना वोट डालता है।",
        },
        "action_step": {
            "en": "Before voting, carefully check the candidate list and party symbol before pressing the button.",
            "hi": "वोट देने से पहले उम्मीदवारों की सूची और पार्टी चिन्ह ध्यान से देखकर ही बटन दबाइए।",
        },
        "fun_fact": {
            "en": "EVMs have made counting in India much faster and more consistent.",
            "hi": "ईवीएम ने भारत में मतगणना को काफी तेज और अधिक एकसमान बनाया है।",
        },
    },
    "NOTA": {
        "shaadi_analogy": {
            "en": "NOTA is like a guest saying that none of the dishes made them happy.",
            "hi": "नोटा उस मेहमान की तरह है जो कहता है कि उसे किसी भी डिश से खुशी नहीं हुई।",
        },
        "simple_explanation": {
            "en": "NOTA means None Of The Above. A voter can use this option when they do not want to choose any candidate.",
            "hi": "नोटा का मतलब 'इनमें से कोई नहीं' होता है। जब मतदाता किसी भी उम्मीदवार को चुनना नहीं चाहता, तब वह इस विकल्प का उपयोग कर सकता है।",
        },
        "action_step": {
            "en": "Choose NOTA only after reviewing all the candidates.",
            "hi": "सभी उम्मीदवारों को देखने के बाद ही नोटा चुनिए।",
        },
        "fun_fact": {
            "en": "NOTA gives voters a democratic rejection option, but it does not become the winning candidate itself.",
            "hi": "नोटा मतदाता को असहमति जताने का लोकतांत्रिक विकल्प देता है, लेकिन यह स्वयं विजेता उम्मीदवार नहीं बनता।",
        },
    },
    "Manifesto": {
        "shaadi_analogy": {
            "en": "A manifesto is like a wedding menu card where all promises are written in advance.",
            "hi": "मैनिफेस्टो शादी के मेन्यू कार्ड की तरह होता है जहाँ सारे वादे पहले से लिखे होते हैं।",
        },
        "simple_explanation": {
            "en": "A manifesto is a promise document of a political party. It explains which policies and work the party wants to bring if it wins.",
            "hi": "मैनिफेस्टो किसी राजनीतिक पार्टी का वादा-पत्र होता है। इसमें बताया जाता है कि जीतने पर पार्टी कौन-सी नीतियाँ और काम लाना चाहती है।",
        },
        "action_step": {
            "en": "Compare the manifestos of different parties before voting.",
            "hi": "वोट देने से पहले अलग-अलग पार्टियों के मैनिफेस्टो की तुलना कीजिए।",
        },
        "fun_fact": {
            "en": "A manifesto is not a legal contract, but it is very useful for understanding a party's priorities.",
            "hi": "मैनिफेस्टो कोई कानूनी अनुबंध नहीं होता, लेकिन पार्टी की प्राथमिकताएँ समझने के लिए यह बहुत उपयोगी होता है।",
        },
    },
    "Voter ID": {
        "shaadi_analogy": {
            "en": "A Voter ID is like a wedding invitation card, but your entry is confirmed only when your name is also on the guest list.",
            "hi": "वोटर आईडी शादी के निमंत्रण पत्र की तरह है, लेकिन आपकी एंट्री तभी पक्की होती है जब आपका नाम गेस्ट लिस्ट में भी हो।",
        },
        "simple_explanation": {
            "en": "A Voter ID is useful as identity proof in the voting process. Final eligibility depends on your name being present in the electoral roll.",
            "hi": "वोटर आईडी मतदान प्रक्रिया में पहचान-पत्र के रूप में काम आती है। अंतिम पात्रता इस बात पर निर्भर करती है कि आपका नाम मतदाता सूची में दर्ज है या नहीं।",
        },
        "action_step": {
            "en": "Before voting day, check your name in the voter list and keep a valid ID ready.",
            "hi": "मतदान दिवस से पहले मतदाता सूची में अपना नाम जाँच लीजिए और एक वैध पहचान पत्र तैयार रखिए।",
        },
        "fun_fact": {
            "en": "The Election Commission accepts several approved identity documents, not just the Voter ID card.",
            "hi": "चुनाव आयोग सिर्फ वोटर आईडी ही नहीं, बल्कि कई स्वीकृत पहचान पत्र भी स्वीकार करता है।",
        },
    },
    "Booth": {
        "shaadi_analogy": {
            "en": "A polling booth is your mandap, where the most important ceremony takes place.",
            "hi": "पोलिंग बूथ आपका मंडप है, जहाँ पूरी रस्म का सबसे महत्वपूर्ण काम होता है।",
        },
        "simple_explanation": {
            "en": "A polling booth is the place where you physically go to cast your vote. Each voter gets a specific booth based on the area.",
            "hi": "पोलिंग बूथ वह जगह है जहाँ आप जाकर अपना वोट डालते हैं। हर मतदाता को उसके क्षेत्र के आधार पर एक निश्चित बूथ दिया जाता है।",
        },
        "action_step": {
            "en": "Confirm your assigned booth before voting day.",
            "hi": "मतदान दिवस से पहले अपना निर्धारित बूथ पक्का कर लीजिए।",
        },
        "fun_fact": {
            "en": "Election officers, voter lists, and the full voting setup are carefully managed at each booth.",
            "hi": "हर बूथ पर चुनाव अधिकारी, मतदाता सूची और पूरी मतदान व्यवस्था को सावधानी से संभाला जाता है।",
        },
    },
    "Election Commission": {
        "shaadi_analogy": {
            "en": "The Election Commission is like the full wedding planner who makes sure every ritual follows the rules and timing.",
            "hi": "चुनाव आयोग पूरी शादी के प्लानर की तरह है, जो सुनिश्चित करता है कि हर रस्म नियम और समय के हिसाब से हो।",
        },
        "simple_explanation": {
            "en": "The Election Commission of India is an independent constitutional body that conducts elections and monitors the fairness of the process.",
            "hi": "भारत का चुनाव आयोग एक स्वतंत्र संवैधानिक संस्था है, जो चुनाव कराती है और पूरी प्रक्रिया की निष्पक्षता पर नज़र रखती है।",
        },
        "action_step": {
            "en": "Follow official Election Commission sources for authentic election-related updates.",
            "hi": "चुनाव से जुड़ी सही जानकारी के लिए चुनाव आयोग के आधिकारिक स्रोतों को फॉलो कीजिए।",
        },
        "fun_fact": {
            "en": "The Election Commission coordinates one of the world's largest democratic exercises.",
            "hi": "चुनाव आयोग दुनिया की सबसे बड़ी लोकतांत्रिक प्रक्रियाओं में से एक का समन्वय करता है।",
        },
    },
    "Model Code": {
        "shaadi_analogy": {
            "en": "The Model Code of Conduct is like wedding house rules so that no one crosses the line during the function.",
            "hi": "आदर्श आचार संहिता शादी के घर के नियमों जैसी होती है, ताकि कोई भी समारोह में हद पार न करे।",
        },
        "simple_explanation": {
            "en": "Once elections are announced, parties and candidates must follow certain campaign behavior rules. These rules are called the Model Code of Conduct.",
            "hi": "चुनाव घोषित होते ही पार्टियों और उम्मीदवारों पर कुछ प्रचार-संबंधी आचरण नियम लागू हो जाते हैं। इन्हीं नियमों को आदर्श आचार संहिता कहा जाता है।",
        },
        "action_step": {
            "en": "If you see a clear rule violation, report it through the official complaint channel.",
            "hi": "अगर आपको साफ़ नियम उल्लंघन दिखे, तो उसकी शिकायत आधिकारिक माध्यम से कीजिए।",
        },
        "fun_fact": {
            "en": "The MCC is not a separate statute, yet it plays a strong practical role in maintaining fair elections.",
            "hi": "आदर्श आचार संहिता कोई अलग कानून नहीं है, फिर भी निष्पक्ष चुनाव बनाए रखने में इसकी बहुत महत्वपूर्ण व्यावहारिक भूमिका है।",
        },
    },
    "Vote Counting": {
        "shaadi_analogy": {
            "en": "Vote counting is like opening the wedding gift counter where every packet is counted carefully so the final result is correct.",
            "hi": "मतगणना शादी के गिफ्ट काउंटर को खोलने जैसी होती है, जहाँ हर पैकेट को ध्यान से गिना जाता है ताकि अंतिम नतीजा सही निकले।",
        },
        "simple_explanation": {
            "en": "On counting day, the votes cast are counted under official rules and the result is declared.",
            "hi": "मतगणना के दिन डाले गए वोटों को आधिकारिक नियमों के अनुसार गिना जाता है और परिणाम घोषित किया जाता है।",
        },
        "action_step": {
            "en": "On counting day, follow only official result sources or trusted updates.",
            "hi": "मतगणना के दिन सिर्फ आधिकारिक परिणाम स्रोतों या भरोसेमंद अपडेट्स को ही फॉलो कीजिए।",
        },
        "fun_fact": {
            "en": "The counting process systematically handles both postal ballots and EVM rounds in sequence.",
            "hi": "मतगणना प्रक्रिया में डाक मतपत्रों और ईवीएम राउंड्स दोनों को क्रमबद्ध तरीके से संभाला जाता है।",
        },
    },
}

EXPLAIN_PROMPT_TEMPLATE = """Explain the Indian election topic "{topic}" in simple language using Desi Wedding (Shaadi) analogies.

Respond only with valid JSON in this format:
{{
  "shaadi_analogy": "string",
  "simple_explanation": "string",
  "action_step": "string",
  "fun_fact": "string"
}}
"""


def parse_json_response(text: str) -> dict[str, str] | None:
    """Parse JSON from a model response with markdown-tolerant extraction."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _to_native_hindi(value: str) -> str:
    """Translate a string to Hindi when it is not already Devanagari-heavy."""
    if re.search(r"[\u0900-\u097F]", value):
        return value
    return translate_to_hindi(value)


def _resolve_localized_field(
    payload: dict[str, str | dict[str, str]],
    field_name: str,
    lang: str,
) -> str:
    """Resolve a localized field from a payload."""
    raw_value = payload.get(field_name, "")
    if isinstance(raw_value, dict):
        return raw_value.get(lang) or raw_value.get("en", "")
    return raw_value


def build_explain_response(
    topic: str,
    lang: str,
    payload: dict[str, str | dict[str, str]],
) -> ExplainResponse:
    """Build a normalized explain response from a payload dictionary."""
    shaadi_analogy = _resolve_localized_field(payload, "shaadi_analogy", lang)
    simple_explanation = _resolve_localized_field(payload, "simple_explanation", lang)
    action_step = _resolve_localized_field(payload, "action_step", lang)
    fun_fact = _resolve_localized_field(payload, "fun_fact", lang)

    if lang == "hi":
        shaadi_analogy = _to_native_hindi(shaadi_analogy)
        simple_explanation = _to_native_hindi(simple_explanation)
        action_step = _to_native_hindi(action_step)
        fun_fact = _to_native_hindi(fun_fact)

    return ExplainResponse(
        topic=topic,
        shaadi_analogy=shaadi_analogy,
        simple_explanation=simple_explanation,
        action_step=action_step,
        fun_fact=fun_fact,
        lang=lang,  # type: ignore[arg-type]
    )


def build_generic_fallback(topic: str) -> dict[str, str]:
    """Build a deterministic fallback explanation."""
    return {
        "shaadi_analogy": f"{topic} shaadi ke us important ritual ki tarah hai jahan order aur clarity bahut zaroori hoti hai.",
        "simple_explanation": f"{topic} election process ka ek important hissa hai jo system ko smoothly chalane mein madad karta hai.",
        "action_step": "Is topic ko samajhne ke liye official Election Commission resources bhi dekh sakte hain.",
        "fun_fact": "India ka election system itna large scale par chalta hai ki har concept ka apna important role hota hai.",
    }


@router.post("/explain", response_model=ExplainResponse)
async def explain_topic(req: ExplainRequest) -> ExplainResponse:
    """Explain an election topic using shaadi analogies."""
    try:
        requested_topic = validate_topic(req.topic)
        lang = validate_language(req.lang)
        normalized_topic = TOPIC_ALIASES.get(requested_topic.lower(), requested_topic)
        cache_key = cache.make_key("explain", normalized_topic, lang)
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        local_payload = LOCAL_EXPLAINERS.get(normalized_topic)
        if local_payload:
            response = build_explain_response(normalized_topic, lang, local_payload)
            cache.set(cache_key, response, ttl_seconds=86400)
            return response

        prompt = EXPLAIN_PROMPT_TEMPLATE.format(topic=normalized_topic)
        model_text = gemini_service.ask_gemini(prompt)
        parsed = parse_json_response(model_text) or build_generic_fallback(normalized_topic)
        response = build_explain_response(normalized_topic, lang, parsed)
        cache.set(cache_key, response, ttl_seconds=86400)
        return response
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error in explain endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
