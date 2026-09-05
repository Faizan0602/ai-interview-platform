import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api.js";

const difficulties = ["Easy", "Medium", "Hard", "Senior"];

function CreateInterview() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    jobTitle: "",
    jobDescription: "",
    difficulty: "Medium",
  });
  const [error, setError] = useState("");
  const [loadingText, setLoadingText] = useState("");

  const updateField = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (loadingText) {
      return;
    }

    setError("");
    setLoadingText("Creating Interview...");

    try {
      const title = form.jobTitle.trim();
      const jobDescription = form.jobDescription.trim();

      const { data: interview } = await api.post("/interviews", {
        title,
        role: title,
        difficulty: form.difficulty,
      });

      setLoadingText("Generating Questions...");

      await api.post(`/interviews/${interview.id}/generate-questions`, {
        count: 5,
        additional_context: jobDescription || null,
      });

      navigate(`/interviews/${interview.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create interview.");
    } finally {
      setLoadingText("");
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-zinc-950">Create Interview</h1>
        <p className="mt-1 text-sm text-zinc-500">Generate questions for a new interview</p>
      </div>

      {error ? (
        <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <form className="space-y-5 rounded-lg border border-zinc-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
        <div className="space-y-1.5">
          <label htmlFor="jobTitle">Job Title</label>
          <input
            id="jobTitle"
            name="jobTitle"
            type="text"
            value={form.jobTitle}
            onChange={updateField}
            minLength={3}
            maxLength={150}
            required
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="jobDescription">Job Description</label>
          <textarea
            id="jobDescription"
            name="jobDescription"
            value={form.jobDescription}
            onChange={updateField}
            rows="7"
            required
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="difficulty">Difficulty</label>
          <select
            id="difficulty"
            name="difficulty"
            value={form.difficulty}
            onChange={updateField}
          >
            {difficulties.map((difficulty) => (
              <option key={difficulty} value={difficulty}>
                {difficulty}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={Boolean(loadingText)}
          className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-zinc-400"
        >
          {loadingText || "Generate Questions"}
        </button>
      </form>
    </div>
  );
}

export default CreateInterview;
