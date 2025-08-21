# Setup Instructions
Set up your development environment by following these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ATS.git
   cd ATS
   ```
2. Create a virtual environment for python:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
4. Install the required python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver 8000
   ```
6. Open your browser and navigate to `http://localhost:8000` to see the app in action.


# API testing on postman


## 1. Start your Django server

In your project folder:

```bash
python manage.py runserver 8000
```

It should run at `http://127.0.0.1:8000/`.

---

## 2. Open Postman

* Create a **New Request**.
* Set **Method** = `POST`.
* URL = `http://127.0.0.1:8000/api/score/`

---

## 3. Configure the Body

Click **Body → form-data**. Add these fields:

| Key         | Type | Value                                              |
| ----------- | ---- | -------------------------------------------------- |
| `job_title` | Text | `Senior Data Scientist`                            |
| `job_desc`  | Text | `We need 5+ years ML, Python, SQL, AWS, Docker...` |
| `resume`    | File | Choose a **PDF resume file** from your system      |
| `use_llm`   | Text | `false` (or `true` if you enabled LLM in settings) |

---

## 4. Send Request

Click **Send**.
If everything is set up, you’ll get a **JSON response** like:

```json
{
  "score": 78.5,
  "breakdown": {
    "semantic": 80,
    "skills": 85,
    "experience": 70,
    "title": 90,
    "hygiene": 68
  },
  "matched_skills": ["Python", "SQL", "AWS"],
  "llm_notes": null,
  "timestamp": "2025-08-20T10:45:32Z"
}
```

---

## 5. Save the Collection (Optional)

* In Postman, click **Save** → Name it `ATS API`.
* You can now reuse and share.

---

⚡ Tip: If you want to test multiple resumes quickly:

* Duplicate the request in Postman.
* Change only the **resume** field file.
* Compare scores side by side.

---