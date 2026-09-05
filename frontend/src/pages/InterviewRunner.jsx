import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api.js";

function InterviewRunner() {
  const { interviewId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerText, setAnswerText] = useState("");
  const [answerId, setAnswerId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [loadingText, setLoadingText] = useState("");

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const { data } = await api.get(`/questions/interview/${interviewId}`);
        setQuestions(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Unable to load interview questions.");
      } finally {
        setIsLoading(false);
      }
    };

    loadQuestions();
  }, [interviewId]);

  const currentQuestion = questions[currentIndex];
  const isLastQuestion = currentIndex === questions.length - 1;

  const progressLabel = useMemo(() => {
    if (!questions.length) {
      return "Question 0 of 0";
    }

    return `Question ${currentIndex + 1} of ${questions.length}`;
  }, [currentIndex, questions.length]);

  const submitAnswer = async (event) => {
    event.preventDefault();

    if (loadingText) {
      return;
    }

    const trimmedAnswer = answerText.trim();
    if (!trimmedAnswer || !currentQuestion) {
      setError("Answer text cannot be empty.");
      return;
    }

    setError("");
    setLoadingText("Submitting Answer...");

    try {
      let submittedAnswerId = answerId;

      if (!submittedAnswerId) {
        const { data: answer } = await api.post("/answers", {
          question_id: currentQuestion.id,
          answer_text: trimmedAnswer,
        });
        submittedAnswerId = answer.id;
        setAnswerId(submittedAnswerId);
      }

      setLoadingText("Generating Feedback...");

      const { data: generatedFeedback } = await api.post(`/feedback/${submittedAnswerId}`);
      setFeedback(generatedFeedback);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to submit answer.");
    } finally {
      setLoadingText("");
    }
  };

  const goToNextQuestion = () => {
    if (isLastQuestion) {
      navigate(`/reports/${interviewId}`);
      return;
    }

    setCurrentIndex((index) => index + 1);
    setAnswerText("");
    setAnswerId(null);
    setFeedback(null);
    setError("");
  };

  if (isLoading) {
    return <p className="text-sm text-zinc-500">Loading questions...</p>;
  }

  if (!questions.length) {
    return (
      <div className="space-y-4">
        {error ? (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </div>
        ) : (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            No questions found for this interview.
          </div>
        )}
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

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-950">Interview Runner</h1>
          <p className="mt-1 text-sm font-medium text-emerald-700">{progressLabel}</p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="w-fit rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
        >
          Exit
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="mb-5">
          <p className="text-sm font-semibold text-zinc-500">{currentQuestion.question_type}</p>
          <h2 className="mt-2 text-xl font-semibold leading-8 text-zinc-950">
            {currentQuestion.question_text}
          </h2>
        </div>

        <form className="space-y-4" onSubmit={submitAnswer}>
          <div className="space-y-1.5">
            <label htmlFor="answerText">Answer</label>
            <textarea
              id="answerText"
              name="answerText"
              value={answerText}
              onChange={(event) => setAnswerText(event.target.value)}
              rows="9"
              disabled={Boolean(feedback) || Boolean(loadingText)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={Boolean(feedback) || Boolean(loadingText)}
            className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-zinc-400"
          >
            {loadingText || "Submit Answer"}
          </button>
        </form>
      </section>

      {feedback ? (
        <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-zinc-950">Feedback</h2>
              <p className="mt-1 text-sm text-zinc-500">AI evaluation for this answer</p>
            </div>
            <div className="w-fit rounded-lg bg-zinc-100 px-3 py-1 text-sm font-semibold text-zinc-700">
              Score: {feedback.score}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm font-medium text-zinc-500">Strengths</p>
              <p className="mt-1 text-sm leading-6 text-zinc-800">{feedback.strengths}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-500">Weaknesses</p>
              <p className="mt-1 text-sm leading-6 text-zinc-800">{feedback.weaknesses}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-500">Suggestions</p>
              <p className="mt-1 text-sm leading-6 text-zinc-800">{feedback.suggestions}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={goToNextQuestion}
            className="mt-5 rounded-lg bg-indigo-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-800"
          >
            {isLastQuestion ? "View Report" : "Next Question"}
          </button>
        </section>
      ) : null}
    </div>
  );
}

export default InterviewRunner;
