import re, yaml
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict
import pdfplumber
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+\d{1,3}[-\s]?)?\d{3,4}[-\s]?\d{3}[-\s]?\d{3,4}")
YEARS_RE = re.compile(r"(\d+)\s*\+?\s*(years|year|yrs|yr)", re.I)
SENIORITY_TERMS = ["intern","junior","jr","associate","mid","senior","sr","lead","staff","principal","manager","head","director"]

@dataclass
class ScoreBreakdown:
    semantic_similarity: float
    skill_overlap: float
    experience_alignment: float
    title_alignment: float
    hygiene: float
    def total(self)->float:
        return round(self.semantic_similarity+self.skill_overlap+self.experience_alignment+self.title_alignment+self.hygiene,2)

def read_pdf_text(path:str)->str:
    chunks=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            chunks.append(p.extract_text() or "")
    return "\n".join(chunks).strip()

def normalize(t:str)->str:
    import re
    return re.sub(r"\s+"," ",t.lower()).strip()

def extract_years(t:str)->Optional[int]:
    m = YEARS_RE.findall(t or "")
    ys = [int(x[0]) for x in m] if m else []
    return max(ys) if ys else None

def find_seniority(t:str)->Optional[str]:
    n=normalize(t or "")
    found=[s for s in SENIORITY_TERMS if re.search(rf"\\b{s}\\b", n)]
    return found[-1] if found else None

def load_skills(path:str)->List[str]:
    with open(path,"r",encoding="utf-8") as f:
        data=yaml.safe_load(f)
    skills=[]
    for arr in data.get("skills",{}).values():
        skills.extend(arr)
    return sorted(set(skills))

def fuzzy_contains(hay:str, needle:str, threshold:int=88)->bool:
    import re
    if re.search(rf"\\b{re.escape(needle)}\\b", hay):
        return True
    return fuzz.partial_ratio(needle, hay) >= threshold

def score_skills(resume_text:str, jd_text:str, skills_list:List[str])->Tuple[int,int,List[str]]:
    nr=normalize(resume_text); nj=normalize(jd_text)
    jd_skills=[s for s in skills_list if fuzzy_contains(nj, s, threshold=90)]
    matched=[s for s in jd_skills if fuzzy_contains(nr, s, threshold=85)]
    return len(matched), len(jd_skills), matched

def semantic_similarity_score(emb_model:SentenceTransformer, a:str, b:str, max_pts:float)->float:
    emb = emb_model.encode([a,b], normalize_embeddings=True)
    sim = float(cosine_similarity([emb[0]],[emb[1]])[0][0])
    return max(0.0, min(max_pts, (sim+1)/2*max_pts))

def experience_score(jd:str, cv:str, max_pts:float)->float:
    jy = extract_years(jd) or 0
    cy = extract_years(cv) or 0
    if jy==0: return round(max_pts*0.8,2)
    ratio = min(1.0, cy/jy) if jy else 1.0
    return round(max_pts*ratio,2)

def title_alignment_score(title:str, cv_text:str, max_pts:float)->float:
    jd = find_seniority(title) or ""
    cv = find_seniority(cv_text) or ""
    if not jd: return round(max_pts*0.8, 2)
    if jd==cv: return max_pts
    near={"senior":{"lead","staff","principal","sr"},
          "jr":{"junior","associate"},
          "junior":{"jr","associate"},
          "lead":{"senior","staff","principal"}}
    if cv in near.get(jd,set()): return round(max_pts*0.7,2)
    return round(max_pts*0.3,2)

def hygiene_score(cv_text:str, max_pts:float)->tuple[float, Dict[str,bool]]:
    email_ok=bool(EMAIL_RE.search(cv_text))
    phone_ok=bool(PHONE_RE.search(cv_text))
    readable=len(cv_text.strip())>200
    checks={"email":email_ok,"phone":phone_ok,"readable_text":readable}
    pts=0.0
    pts+=max_pts*0.3 if email_ok else 0.0
    pts+=max_pts*0.3 if phone_ok else 0.0
    pts+=max_pts*0.4 if readable else 0.0
    return round(pts,2), checks

def compute_score(job_title:str, jd_text:str, resume_path:str, skills_path:str, weights:dict, use_llm:bool=False, llm_model_name:str="google/flan-t5-small")->dict:
    resume_text = read_pdf_text(resume_path)
    skills = load_skills(skills_path)
    emb_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    sem_pts = semantic_similarity_score(emb_model, jd_text, resume_text, weights["semantic"])
    matched_count, jd_skill_count, matched = score_skills(resume_text, jd_text, skills)
    skill_ratio = (matched_count / jd_skill_count) if jd_skill_count else 1.0
    skill_pts = round(weights["skills"] * min(1.0, skill_ratio), 2)
    exp_pts = experience_score(jd_text, resume_text, weights["experience"])
    title_pts = title_alignment_score(job_title, resume_text, weights["title"])
    hyg_pts, hyg_checks = hygiene_score(resume_text, weights["hygiene"])

    breakdown = ScoreBreakdown(sem_pts, skill_pts, exp_pts, title_pts, hyg_pts)

    notes = ""
    if use_llm:
        try:
            from transformers import pipeline
            prompt = f"""You are an ATS assistant. Summarize strengths and gaps in 4-6 bullets.
Job Title: {job_title}
JD: {jd_text[:2000]}
Resume: {resume_text[:2000]}
Matched skills: {", ".join(matched[:30])}
Scores: {breakdown.total()} total
"""
            gen = pipeline("text2text-generation", model=llm_model_name, max_new_tokens=220)
            notes = gen(prompt)[0]["generated_text"].strip()
        except Exception as e:
            notes = f"LLM summary unavailable: {e}"

    return {
        "matched_skills": matched,
        "hygiene_checks": hyg_checks,
        "breakdown": asdict(breakdown),
        "score": breakdown.total(),
        "notes": notes,
    }