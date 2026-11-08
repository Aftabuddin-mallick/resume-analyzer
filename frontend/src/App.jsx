import { NavLink, Route, Routes } from "react-router-dom";
import Analyze from "./pages/Analyze.jsx";
import Result from "./pages/Result.jsx";
import History from "./pages/History.jsx";
import Jobs from "./pages/Jobs.jsx";

const link = ({ isActive }) =>
  `rounded-md px-3 py-2 text-sm font-semibold transition ${
    isActive ? "bg-white text-ink" : "text-white/75 hover:text-white"
  }`;

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="bg-ink">
        <nav className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-3">
          <NavLink to="/" className="font-display text-lg font-bold text-white">
            Resume Analyzer
          </NavLink>
          <div className="flex gap-1">
            <NavLink to="/" end className={link}>Analyze</NavLink>
            <NavLink to="/history" className={link}>History</NavLink>
            <NavLink to="/jobs" className={link}>Jobs</NavLink>
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Analyze />} />
          <Route path="/analysis/:id" element={<Result />} />
          <Route path="/history" element={<History />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="*" element={<p className="py-20 text-center">Page not found.</p>} />
        </Routes>
      </main>
    </div>
  );
}
