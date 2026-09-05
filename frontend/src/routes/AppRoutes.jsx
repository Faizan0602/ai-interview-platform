import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "../components/Layout.jsx";
import CreateInterview from "../pages/CreateInterview.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import InterviewRunner from "../pages/InterviewRunner.jsx";
import Login from "../pages/Login.jsx";
import Register from "../pages/Register.jsx";
import Report from "../pages/Report.jsx";

function ProtectedRoute({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  return localStorage.getItem("token") ? <Navigate to="/dashboard" replace /> : children;
}

function ProtectedPage({ children }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedPage>
              <Dashboard />
            </ProtectedPage>
          }
        />
        <Route
          path="/interviews/new"
          element={
            <ProtectedPage>
              <CreateInterview />
            </ProtectedPage>
          }
        />
        <Route
          path="/interviews/:interviewId"
          element={
            <ProtectedPage>
              <InterviewRunner />
            </ProtectedPage>
          }
        />
        <Route
          path="/reports/:interviewId"
          element={
            <ProtectedPage>
              <Report />
            </ProtectedPage>
          }
        />
        <Route
          path="/interviews/:interviewId/report"
          element={
            <ProtectedPage>
              <Report />
            </ProtectedPage>
          }
        />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
