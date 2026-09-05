import React from "react";
import { createRoot } from "react-dom/client";

import AppRoutes from "./routes/AppRoutes.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppRoutes />
  </React.StrictMode>
);
