import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { ErrorBox, formatDate, Spinner } from "../components/Bits.jsx";
import { scoreColor } from "../components/ScoreDial.jsx";

export default function History() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listAnalyses().then(setRows).catch((e) => setError(e.message));
  }, []);

  async function remove(id) {
    if (!window.confirm("Delete this analysis?")) return;
    try {
      await api.deleteAnalysis(id);
      setRows((r) => r.filter((x) => x.id !== id));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold">History</h1>
      <p className="mt-2 text-ink/70">Your past analyses, newest first.</p>
      <div className="mt-6 space-y-3">
        <ErrorBox message={error} />
        {!rows && !error && <Spinner label="Loading history..." />}
        {rows && rows.length === 0 && (
          <div className="card text-center">
            <p>No analyses yet.</p>
            <Link to="/" className="btn mt-4">Analyze your first resume</Link>
          </div>
        )}
        {rows?.map((r) => (
          <div key={r.id} className="card flex flex-wrap items-center gap-4 !p-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full font-display text-lg font-bold text-white" style={{ background: scoreColor(r.match_score) }}>
              {Math.round(r.match_score)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold">{r.job_title || "Untitled job"}</p>
              <p className="truncate text-sm text-ink/60">{r.filename} &middot; {formatDate(r.created_at)}</p>
              <p className="text-sm text-ink/60">{r.matched_count} skills matched, {r.missing_count} missing</p>
            </div>
            <div className="flex gap-2">
              <Link to={`/analysis/${r.id}`} className="btn-ghost">View</Link>
              <button onClick={() => remove(r.id)} className="btn-ghost">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
