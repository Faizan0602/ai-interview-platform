import { NavLink, useNavigate } from "react-router-dom";

const navLinkClass = ({ isActive }) =>
  [
    "rounded-lg px-3 py-2 text-sm font-medium transition",
    isActive
      ? "bg-emerald-700 text-white"
      : "text-zinc-700 hover:bg-zinc-100 hover:text-zinc-950",
  ].join(" ");

function Layout({ children }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-lg font-semibold text-zinc-950">AI Interview Platform</p>
            <p className="text-sm text-zinc-500">MVP workspace</p>
          </div>

          <nav className="flex flex-wrap items-center gap-2">
            <NavLink to="/dashboard" className={navLinkClass}>
              Dashboard
            </NavLink>
            <NavLink to="/interviews/new" className={navLinkClass}>
              Create Interview
            </NavLink>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-zinc-300 px-3 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 hover:text-zinc-950"
            >
              Logout
            </button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
    </div>
  );
}

export default Layout;
