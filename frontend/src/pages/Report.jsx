import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api.js";

function Report() {
  const { interviewId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadReport = async () => {
      try {
        const { data } = await api.get(`/interviews/${interviewId}/report`);
        setReport(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Unable to load report.");
      } finally {
        setIsLoading(false);
      }
    };

    loadReport();
  }, [interviewId]);

  if (isLoading) {
    return <p className="text-sm text-zinc-500">Loading Report...</p>;
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </div>
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const stats = [
    { label: "Total Questions", value: report.total_questions },
    { label: "Answered Questions", value: report.answered_questions },
    { label: "Feedback Generated", value: report.feedback_generated },
    { label: "Average Score", value: report.average_score },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-950">Interview Report</h1>
          <p className="mt-1 text-sm text-zinc-500">{report.interview_title}</p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
        >
          Back to Dashboard
        </button>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Role</p>
          <p className="mt-2 text-lg font-semibold text-zinc-950">{report.role}</p>
        </article>
        <article className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Difficulty</p>
          <p className="mt-2 text-lg font-semibold text-zinc-950">{report.difficulty}</p>
        </article>
        <article className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Interview ID</p>
          <p className="mt-2 break-all text-sm font-medium text-zinc-700">{report.interview_id}</p>
        </article>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <article key={stat.label} className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-zinc-500">{stat.label}</p>
            <p className="mt-2 text-3xl font-semibold text-zinc-950">{stat.value}</p>
          </article>
        ))}
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-zinc-950">Questions</h2>

        {report.questions.map((question, index) => (
          <article
            key={question.question_id}
            className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm"
          >
            <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-emerald-700">Question {index + 1}</p>
                <h3 className="mt-1 text-base font-semibold text-zinc-950">{question.question_text}</h3>
              </div>
              <div className="w-fit rounded-lg bg-zinc-100 px-3 py-1 text-sm font-semibold text-zinc-700">
                Score: {question.score ?? "Pending"}
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div>
                <p className="text-sm font-medium text-zinc-500">Answer</p>
                <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-zinc-800">
                  {question.answer_text || "Not answered yet."}
                </p>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-zinc-500">Strengths</p>
                  <p className="mt-1 text-sm leading-6 text-zinc-800">
                    {question.strengths || "Feedback pending."}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-500">Weaknesses</p>
                  <p className="mt-1 text-sm leading-6 text-zinc-800">
                    {question.weaknesses || "Feedback pending."}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-500">Suggestions</p>
                  <p className="mt-1 text-sm leading-6 text-zinc-800">
                    {question.suggestions || "Feedback pending."}
                  </p>
                </div>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

export default Report;
