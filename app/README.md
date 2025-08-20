# ATS Django Backend (LLM-assisted scoring)

A Django + DRF API that scores a resume PDF against a job title and description and returns a 0..100 match score with a transparent breakdown.

## Suggested Python version
Prefer **Python 3.12** for best compatibility with `torch` (needed by `sentence-transformers`). On 3.13 you may need pre-release wheels or to build from source.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
# Install torch for your OS/Python from https://pytorch.org/get-started/locally/

python manage.py migrate
python manage.py runserver 8000
```

### API
POST /api/score/ (multipart/form-data)
- job_title (str)
- job_desc (str)
- resume (file: PDF)
- use_llm (bool, optional)
