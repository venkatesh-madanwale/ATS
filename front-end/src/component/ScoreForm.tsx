import React, { useState } from "react";
import axios from "axios";
import "../css/ScoreForm.css";

const ScoreForm: React.FC = () => {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [useLLM, setUseLLM] = useState(true);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resume) {
      alert("Please upload a resume!");
      return;
    }

    const formData = new FormData();
    formData.append("job_title", jobTitle);
    formData.append("job_desc", jobDesc);
    formData.append("resume", resume);
    formData.append("use_llm", String(useLLM));

    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:8000/api/score/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResponse(res.data);
    } catch (error: any) {
      setResponse(error.response?.data || { error: "Request failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>ATS Resume Scorer</h1>
      <form onSubmit={handleSubmit}>
        <label>Job Title</label>
        <input
          type="text"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          required
          placeholder="Enter Job Title"
          />

        <label>Job Description</label>
        <textarea
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          required
          placeholder="Enter Job Description"
        />

        <label>Upload Resume (PDF)</label>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setResume(e.target.files?.[0] || null)}
          required
        />

        <div className="checkbox-row">
          <input
            type="checkbox"
            checked={useLLM}
            onChange={(e) => setUseLLM(e.target.checked)}
          />
          <span>Use LLM Model</span>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Scoring..." : "Submit"}
        </button>
      </form>

      {response && (
        <div className="response-container">
          <h2>📊 Scoring Results</h2>
          <div className="card">
            <h3>{response.job_title}</h3>
            <p><strong>Overall Score:</strong> {response.score.toFixed(2)}%</p>
          </div>

          <div className="card">
            <h3>Breakdown</h3>
            <ul>
              {Object.entries(response.breakdown).map(([k, v]) => (
                <li key={k}>
                  <span className="label">{k.replace("_", " ")}:</span> {String(v)}
                </li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h3>Matched Skills</h3>
            <div className="skills">
              {response.matched_skills.map((skill: string, i: number) => (
                <span key={i} className="skill-tag">{skill}</span>
              ))}
            </div>
          </div>

          <div className="card">
            <h3>Hygiene Checks</h3>
            <ul>
              {Object.entries(response.hygiene_checks).map(([k, v]) => (
                <li key={k}>
                  <span className="label">{k}:</span>{" "}
                  {v ? "✅ Passed" : "❌ Failed"}
                </li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h3>Notes</h3>
            <p>{response.notes}</p>
          </div>

          <div className="card">
            <h3>Metadata</h3>
            <p><strong>ID:</strong> {response.id}</p>
            <p><strong>Created At:</strong> {new Date(response.created_at).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScoreForm;
