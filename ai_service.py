import json, os, re
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
def _json(text):
    text = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.S)
    if not match: raise ValueError("No JSON object found")
    return json.loads(match.group(0))
def _call(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY is missing. Add it to your environment or .env file.")
    try:
        from google import genai
        client = genai.Client(api_key=key)
        result = client.models.generate_content(model=MODEL_NAME, contents=prompt, config={"temperature": 0.2, "response_mime_type": "application/json"})
        return _json(result.text)
    except ImportError as exc: raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc
    except Exception as exc: raise RuntimeError(f"Gemini could not complete the analysis: {exc}") from exc
def analyze(lesson, questions, responses):
    from prompts import analysis_prompt
    return _call(analysis_prompt(lesson, questions, responses))
def improve(lesson, analysis, plan):
    from prompts import improvement_prompt
    return _call(improvement_prompt(lesson, analysis, plan))
