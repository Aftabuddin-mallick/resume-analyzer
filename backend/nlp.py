"""Skill extraction and match scoring (TF-IDF cosine similarity + skill coverage)."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills import PATTERNS


def extract_skills(text: str) -> list[str]:
    text = text or ""
    return [name for name, pattern in PATTERNS.items() if pattern.search(text)]


def tfidf_similarity(a: str, b: str) -> float:
    """Cosine similarity of TF-IDF vectors, 0..1."""
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        matrix = vec.fit_transform([a or "", b or ""])
        return float(cosine_similarity(matrix[0], matrix[1])[0][0])
    except ValueError:  # empty vocabulary
        return 0.0


def compute_match(resume_text: str, job_text: str) -> dict:
    """
    Final score = 60% skill coverage + 40% TF-IDF similarity.
    Raw TF-IDF between two different documents is rarely above 0.5, so it is
    rescaled (sim / 0.5, capped at 1) to keep the final score intuitive.
    """
    resume_skills = set(extract_skills(resume_text))
    job_skills = extract_skills(job_text)

    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    tfidf = tfidf_similarity(resume_text, job_text)
    tfidf_scaled = min(1.0, tfidf / 0.5)

    if job_skills:
        skill_score = len(matched) / len(job_skills)
        final = 0.6 * skill_score + 0.4 * tfidf_scaled
    else:
        skill_score = 0.0
        final = tfidf_scaled

    return {
        "match_score": round(final * 100, 1),
        "tfidf_score": round(tfidf_scaled * 100, 1),
        "skill_score": round(skill_score * 100, 1) if job_skills else 0.0,
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": sorted(resume_skills),
    }
