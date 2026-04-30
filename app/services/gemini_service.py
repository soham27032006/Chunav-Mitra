import google.generativeai as genai
import re
from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

# ─── THE KILLER SHAADI SYSTEM PROMPT ─────────────────────────────────────────
SHAADI_SYSTEM_PROMPT = """
You are "Chunav Mitra" — India's friendliest election guide who explains
the entire election process using Desi Wedding (Shaadi) analogies.
You speak warm Hinglish when user writes Hindi, English when they write English.

══════════════════════════════════════════════
CORE SHAADI ANALOGIES — always use these:
══════════════════════════════════════════════

1. VOTER LIST / ELECTORAL ROLL = GUEST LIST (Mehman List)
→ "Shaadi mein entry sirf invited guests ko milti hai.
Agar aapka naam Electoral Roll (Guest List) mein nahi,
toh aap vote (shaadi attend) nahi kar sakte!"
→ Action: "Apna naam check karein → 'Voter Check' button dabao"

2. VOTER ID CARD = WEDDING INVITATION CARD
→ "Invitation card ke bina gate pe rok denge.
Voter ID = aapka official shaadi ka invite!"

3. POLLING BOOTH = MANDAP
→ "Mandap woh jagah hai jahan asli kaam hota hai.
Aapka Polling Booth = Aapka personal Mandap!"
→ Action: "Apna Mandap dhundho → 'Find My Booth' button"

4. INDELIBLE INK = MEHNDI
→ "Shaadi attend ki? Mehndi lagegi! Vote diya? Ink lagegi!
Yeh proof hai ki aap desh ki sabse badi shaadi mein the."

5. ELECTION COMMISSION (ECI) = WEDDING PLANNER
→ "Poori shaadi ka management ECI karta hai —
date, venue, guest list, rules — sab kuch!"

6. MANIFESTO = SHAGUN KA MENU
→ "Har party apna menu (vaade) dikhati hai.
Aapko decide karna hai kiska khana (policies) sabse achha hai."

7. VOTING = SHAGUN DENA
→ "Vote aapka sabse bada shagun hai — desh ko gift!
Aur yeh gift FREE hai, compulsory nahi — par zaroori zaroor hai!"

8. EVM MACHINE = MANGALSUTRA MOMENT
→ "EVM pe button dabana = mangalsutra pahnaana.
Ek baar decide karo, phir pehna do!"

9. CANDIDATE = DULHA/DULHAN
→ "Aapki constituency ke liye best match choose karo —
bilkul jaise shaadi mein rishta dekhte hain!"

10. MODEL CODE OF CONDUCT = SHAADI KE RULES
→ "Baraat mein bhi rules hote hain —
koi hungama nahi, koi late nahi, sab shanti se!"

══════════════════════════════════════════════
BEHAVIOR RULES:
══════════════════════════════════════════════
1. Keep answers SHORT — 3-5 sentences max (unless user asks for detail)
2. ALWAYS end with one action suggestion (check voter, find booth, see timeline)
3. Use the OPENING LINE on the very first message only
4. Never recommend any party or candidate — strictly neutral
5. If user asks something not election-related → gently bring back to elections
6. For VOTER CHECK queries → say "Apna naam check karo, 'Voter Check' feature use karo!"
7. For BOOTH queries → say "Apna Mandap dhundo, 'Find My Booth' use karo!"
8. For TIMELINE queries → share key dates with shaadi phase names
9. If user seems confused → ask ONE simple clarifying question
10. Always validate the user — "Bahut achha sawaal hai!"

══════════════════════════════════════════════
OPENING LINE (first message only):
══════════════════════════════════════════════
"Namaste! Main Chunav Mitra hoon 🗳️
Aap desh ki sabse badi shaadi ke sabse zaroori guest hain —
aapka vote hi sabse bada shagun hai desh ko!
Kya jaanna chahte hain aap aaj? Voter list check karni hai,
booth dhundna hai, ya election ka poora process samajhna hai?"
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SHAADI_SYSTEM_PROMPT
)

# Keyword weights for smarter intent classification
INTENT_KEYWORDS = {
    "voter_check": {
        "voter": 2.0, "name": 1.5, "list": 1.5, "roll": 2.0, "registered": 2.0,
        "naam": 2.0, "register": 1.5, "epic": 2.5, "card": 1.0, "id": 1.5,
        "check": 1.0, "verify": 1.0, "search": 1.0, "dhundo": 1.0, "find": 1.0
    },
    "booth_finder": {
        "booth": 2.0, "mandap": 3.0, "where": 1.5, "kahan": 2.0, "polling": 2.0,
        "station": 1.5, "center": 1.5, "location": 1.5, "place": 1.0, "address": 1.5,
        "near": 1.0, "nearby": 1.0, "closest": 1.0, "nearest": 1.5, "find": 1.0,
        "dhundo": 1.5, "pata": 1.0, "jaana": 1.0
    },
    "timeline": {
        "date": 2.0, "when": 2.0, "timeline": 2.5, "phase": 2.0, "kab": 2.0,
        "schedule": 2.0, "timetable": 2.0, "time": 1.5, "election day": 2.0,
        "voting day": 2.0, "counting": 1.5, "result": 1.5, "announcement": 1.0,
        "dates": 1.5, "kal": 1.0, "din": 1.0
    },
    "explain": {
        "what": 1.5, "how": 1.5, "why": 1.5, "explain": 2.5, "samjhao": 2.5,
        "batao": 1.5, "kya": 1.5, "kaise": 1.5, "kyun": 1.5, "meaning": 1.5,
        "matlab": 1.5, "process": 1.5, "procedure": 1.5, "tarika": 1.5,
        "evm": 2.5, "nota": 2.5, "manifesto": 2.5, "voter_id": 2.5,
        "commission": 2.0, "mcc": 2.5, "counting": 2.0, "ink": 1.5, "mehndi": 1.5
    }
}


def classify_intent(query: str) -> dict:
    """
    Classify query intent with confidence score using weighted keyword matching.
    Returns: {"intent": str, "confidence": float}
    """
    q = query.lower()
    words = re.findall(r'\b\w+\b', q)

    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0.0
        for word in words:
            if word in keywords:
                score += keywords[word]
        scores[intent] = score

    # Add general intent with base score
    scores["general"] = 0.5

    # Find highest scoring intent
    max_intent = max(scores, key=scores.get)
    max_score = scores[max_intent]
    total_score = sum(scores.values())

    # Calculate confidence as proportion of total score
    confidence = max_score / total_score if total_score > 0 else 0.0

    # If confidence is too low, default to general
    if confidence < 0.3:
        return {"intent": "general", "confidence": round(1.0 - confidence, 2)}

    return {"intent": max_intent, "confidence": round(confidence, 2)}


def ask_gemini(query: str, chat_history: list = None) -> str:
    """Send query to Gemini, return response string"""
    try:
        if chat_history and len(chat_history) > 0:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(query)
        else:
            response = model.generate_content(query)
        return response.text
    except Exception as e:
        return f"Oops! Kuch technical issue aa gaya. Please dobara try karein. ({str(e)})"


async def ask_gemini_stream(query: str, history: list = None):
    """
    Stream Gemini response chunks for FastAPI StreamingResponse.
    Yields each chunk as it arrives.
    """
    try:
        if history and len(history) > 0:
            chat = model.start_chat(history=history)
            response = await chat.send_message_async(query, stream=True)
        else:
            response = await model.generate_content_async(query, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"Oops! Kuch technical issue aa gaya. Please dobara try karein. ({str(e)})"


def summarize_history(history: list) -> str:
    """
    Summarize conversation history when it exceeds 10 messages.
    Calls Gemini to create a 2-sentence summary keeping key facts.
    """
    if not history or len(history) < 3:
        return ""

    # Format history for summary
    conversation = []
    for msg in history:
        role = msg.get("role", "user")
        parts = msg.get("parts", [""])
        text = parts[0] if parts else ""
        conversation.append(f"{role}: {text}")

    conversation_text = "\n".join(conversation)

    summary_prompt = f"""Summarize this conversation in exactly 2 sentences, keeping key facts about the user's election questions:

{conversation_text}

Summary:"""

    try:
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception:
        return "User is asking about Indian elections and voting process."
