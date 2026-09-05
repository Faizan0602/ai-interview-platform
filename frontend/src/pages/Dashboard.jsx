import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api.js";

const formatDate = (value) =>
  value
    ? new Intl.DateTimeFormat(undefined, {
        year: "numeric",
        month: "short",
        day: "2-digit",
      }).format(new Date(value))
    : "-";

function Dashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const { data } = await api.get("/dashboard");
        setDashboard(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Unable to load dashboard.");
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const stats = [
    { label: "Total Interviews", value: dashboard?.total_interviews ?? 0, accent: "border-emerald-600" },
    { label: "Total Answers", value: dashboard?.total_answers ?? 0, accent: "border-indigo-600" },
    { label: "Total Feedbacks", value: dashboard?.total_feedbacks ?? 0, accent: "border-amber-500" },
    { label: "Average Score", value: dashboard?.average_score ?? 0, accent: "border-rose-500" },
  ];

  if (isLoading) {
    return <p className="text-sm text-zinc-500">Loading Dashboard...</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-950">Dashboard</h1>
          <p className="mt-1 text-sm text-zinc-500">Interview activity and recent reports</p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/interviews/new")}
          className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800"
        >
          Create Interview
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <article
            key={stat.label}
            className={`rounded-lg border border-zinc-200 border-l-4 ${stat.accent} bg-white p-4 shadow-sm`}
          >
            <p className="text-sm font-medium text-zinc-500">{stat.label}</p>
            <p className="mt-2 text-3xl font-semibold text-zinc-950">{stat.value}</p>
          </article>
        ))}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-950">Recent Interviews</h2>
        </div>

        <div className="overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-zinc-200 text-left text-sm">
              <thead className="bg-zinc-100 text-xs uppercase text-zinc-500">
                <tr>
                  <th className="px-4 py-3 font-semibold">Title</th>
                  <th className="px-4 py-3 font-semibold">Role</th>
                  <th className="px-4 py-3 font-semibold">Difficulty</th>
                  <th className="px-4 py-3 font-semibold">Created At</th>
                  <th className="px-4 py-3 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {dashboard?.recent_interviews?.length ? (
                  dashboard.recent_interviews.map((interview) => (
                    <tr key={interview.interview_id} className="align-top">
                      <td className="px-4 py-3 font-medium text-zinc-950">{interview.title}</td>
                      <td className="px-4 py-3 text-zinc-600">{interview.role}</td>
                      <td className="px-4 py-3 text-zinc-600">{interview.difficulty}</td>
                      <td className="px-4 py-3 text-zinc-600">{formatDate(interview.created_at)}</td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          onClick={() => navigate(`/interviews/${interview.interview_id}/report`)}
                          className="rounded-lg border border-indigo-200 px-3 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-50"
                        >
                          View Report
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-4 py-6 text-center text-zinc-500" colSpan="5">
                      No interviews found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
