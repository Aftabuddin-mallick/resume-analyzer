"""Structured resume feedback from Gemini, with a rule-based fallback so the app never breaks."""
import json
import os
import re

import httpx

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


PROMPT = """You are an expert technical recruiter and resume coach.
Compare the RESUME to the JOB DESCRIPTION and give honest, specific feedback.

Return ONLY valid JSON (no markdown) with exactly this shape:
{{
  "summary": "2-3 sentence overall assessment",
  "strengths": ["up to 5 short strengths relevant to this job"],
  "weaknesses": ["up to 5 short gaps or weaknesses"],
  "suggestions": [
    {{"section": "Summary|Skills|Experience|Projects|Education|Formatting",
      "issue": "what is wrong or missing",
      "suggestion": "concrete action to fix it",
      "example": "a short example line the candidate could use"}}
  ],
  "rewritten_bullets": [
    {{"original": "a weak bullet copied from the resume", "improved": "stronger version with action verb and measurable result"}}
  ],
  "keywords_to_add": ["important job keywords missing from the resume"]
}}

Rules: 4-6 suggestions, 2-3 rewritten bullets. Never invent experience the candidate does not have;
for numbers use placeholders like [X%] when unknown.

Skills already detected as missing (for context): {missing}

JOB TITLE: {title}

JOB DESCRIPTION:
{jd}

RESUME:
{resume}
"""


def _clean_list(value, limit=8):
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()][:limit]


def _normalize(data: dict) -> dict:
    suggestions = []
    for s in data.get("suggestions", []) if isinstance(data.get("suggestions"), list) else []:
        if isinstance(s, dict):
            suggestions.append({
                "section": str(s.get("section", "General")),
                "issue": str(s.get("issue", "")),
                "suggestion": str(s.get("suggestion", "")),
                "example": str(s.get("example", "")),
            })
    bullets = []
    for b in data.get("rewritten_bullets", []) if isinstance(data.get("rewritten_bullets"), list) else []:
        if isinstance(b, dict) and b.get("improved"):
            bullets.append({"original": str(b.get("original", "")), "improved": str(b["improved"])})
    return {
        "summary": str(data.get("summary", "")),
        "strengths": _clean_list(data.get("strengths"), 5),
        "weaknesses": _clean_list(data.get("weaknesses"), 5),
        "suggestions": suggestions[:6],
        "rewritten_bullets": bullets[:3],
        "keywords_to_add": _clean_list(data.get("keywords_to_add"), 12),
    }


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _call_gemini(prompt: str) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"},
    }
    resp = httpx.post(url, params={"key": _api_key()}, json=body, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    text = payload["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json(text)


def fallback_feedback(score: float, matched: list[str], missing: list[str]) -> dict:
    if score >= 75:
        verdict = "Your resume is a strong match for this role."
    elif score >= 50:
        verdict = "Your resume is a decent match, but there are clear gaps to close."
    else:
        verdict = "Your resume needs significant tailoring for this role."
    suggestions = []
    if missing:
        suggestions.append({
            "section": "Skills",
            "issue": f"The job asks for skills not found in your resume: {', '.join(missing[:6])}.",
            "suggestion": "Add the ones you genuinely have to your Skills section and mention them in project or experience bullets.",
            "example": f"Built a feature using {missing[0]} that [result].",
        })
    suggestions.append({
        "section": "Experience",
        "issue": "Bullets may not show measurable impact.",
        "suggestion": "Start each bullet with an action verb and add a number (users, time saved, % improvement).",
        "example": "Reduced page load time by [X%] by introducing caching and lazy loading.",
    })
    suggestions.append({
        "section": "Summary",
        "issue": "A generic summary does not signal fit.",
        "suggestion": "Write a 2-line summary using the job title and 2-3 of its top keywords.",
        "example": "Software engineer with hands-on experience in [key skill] and [key skill], seeking to ...",
    })
    return {
        "summary": verdict + " (AI suggestions are unavailable right now, so these are rule-based tips.)",
        "strengths": [f"Matches required skill: {s}" for s in matched[:5]],
        "weaknesses": [f"Missing skill: {s}" for s in missing[:5]],
        "suggestions": suggestions,
        "rewritten_bullets": [],
        "keywords_to_add": missing[:12],
    }


def generate_feedback(resume: str, jd: str, title: str, score: float, matched: list[str], missing: list[str]):
    """Returns (feedback_dict, source) where source is 'gemini' or 'fallback'."""
    if not _api_key():
        return fallback_feedback(score, matched, missing), "fallback"
    prompt = PROMPT.format(
        missing=", ".join(missing) or "none",
        title=title or "Not provided",
        jd=jd[:6000],
        resume=resume[:12000],
    )
    try:
        data = _normalize(_call_gemini(prompt))
        if not data["suggestions"] and not data["summary"]:
            raise ValueError("empty response")
        return data, "gemini"
    except Exception as exc:  # network, quota, bad JSON ...
        print(f"[llm] Gemini failed, using fallback: {exc}")
        return fallback_feedback(score, matched, missing), "fallback"
