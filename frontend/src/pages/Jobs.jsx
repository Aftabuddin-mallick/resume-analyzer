import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api.js";
import { Chips, ErrorBox, Spinner } from "../components/Bits.jsx";
import { scoreColor } from "../components/ScoreDial.jsx";

const empty = { title: "", company: "", location: "", url: "", description: "" };

export default function Jobs() {
  const [params, setParams] = useSearchParams();
  const analysisId = params.get("analysis") || "";
  const [jobs, setJobs] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [ranked, setRanked] = useState(null);
  const [ranking, setRanking] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const loadJobs = () => api.listJobs().then(setJobs).catch((e) => setError(e.message));

  useEffect(() => {
    loadJobs();
    api.listAnalyses().then(setAnalyses).catch(() => {});
  }, []);

  useEffect(() => {
    setRanked(null);
    if (!analysisId) return;
    setRanking(true);
    setError("");
    api.rankJobs(analysisId)
      .then(setRanked)
      .catch((e) => setError(e.message))
      .finally(() => setRanking(false));
  }, [analysisId]);

  async function addJob(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await api.createJob(form);
      setForm(empty);
      setShowForm(false);
      await loadJobs();
      if (analysisId) setParams({ analysis: analysisId }); // keep selection
      if (analysisId) api.rankJobs(analysisId).then(setRanked).catch(() => {});
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function removeJob(id) {
    if (!window.confirm("Delete this job?")) return;
    try {
      await api.deleteJob(id);
      setJobs((j) => j.filter((x) => x.id !== id));
      setRanked((r) => (r ? r.filter((x) => x.id !== id) : r));
    } catch (e) {
      setError(e.message);
    }
  }

  const list = ranked || jobs;
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Jobs</h1>
          <p className="mt-2 max-w-xl text-ink/70">Pick one of your analyzed resumes to rank these jobs by fit.</p>
        </div>
        <button className="btn" onClick={() => setShowForm((s) => !s)}>{showForm ? "Close form" : "Add a job"}</button>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <label htmlFor="resume" className="text-sm font-semibold">Rank for resume</label>
        <select id="resume" className="input !w-auto min-w-[16rem]" value={analysisId} onChange={(e) => setParams(e.target.value ? { analysis: e.target.value } : {})}>
          <option value="">No ranking (show all jobs)</option>
          {analyses.map((a) => (
            <option key={a.id} value={a.id}>#{a.id} {a.filename} {a.job_title ? `(${a.job_title})` : ""}</option>
          ))}
        </select>
        {ranking && <Spinner label="Ranking..." />}
      </div>
      {analyses.length === 0 && jobs && (
        <p className="mt-2 text-sm text-ink/60">Analyze a resume first to enable ranking.</p>
      )}

      {showForm && (
        <form onSubmit={addJob} className="card mt-6 grid gap-4 md:grid-cols-2">
          <div><label className="text-sm font-semibold">Title</label><input required className="input mt-1" value={form.title} onChange={set("title")} /></div>
          <div><label className="text-sm font-semibold">Company</label><input className="input mt-1" value={form.company} onChange={set("company")} /></div>
          <div><label className="text-sm font-semibold">Location</label><input className="input mt-1" value={form.location} onChange={set("location")} /></div>
          <div><label className="text-sm font-semibold">Link</label><input className="input mt-1" type="url" placeholder="https://" value={form.url} onChange={set("url")} /></div>
          <div className="md:col-span-2">
            <label className="text-sm font-semibold">Description</label>
            <textarea required minLength={30} className="input mt-1 h-32" value={form.description} onChange={set("description")} />
          </div>
          <div className="md:col-span-2"><button className="btn" disabled={saving}>{saving ? <Spinner label="Saving..." /> : "Save job"}</button></div>
        </form>
      )}

      <div className="mt-6 space-y-3">
        <ErrorBox message={error} />
        {!list && !error && <Spinner label="Loading jobs..." />}
        {list && list.length === 0 && <div className="card text-center">No jobs yet. Add one to get started.</div>}
        {list?.map((j, i) => (
          <div key={j.id} className="card !p-4">
            <div className="flex flex-wrap items-start gap-4">
              {ranked && (
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full font-display text-lg font-bold text-white" style={{ background: scoreColor(j.match_score) }} title={`Rank ${i + 1}`}>
                  {Math.round(j.match_score)}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="font-semibold">{j.title}</p>
                <p className="text-sm text-ink/60">{[j.company, j.location].filter(Boolean).join(" · ")}</p>
                {ranked && (
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div><p className="mb-1 text-xs font-semibold text-ink/60">You have</p><Chips items={j.matched_skills} tone="good" /></div>
                    <div><p className="mb-1 text-xs font-semibold text-ink/60">You lack</p><Chips items={j.missing_skills} tone="warn" /></div>
                  </div>
                )}
                {!ranked && <p className="mt-2 line-clamp-2 text-sm text-ink/70">{j.description}</p>}
              </div>
              <div className="flex gap-2">
                {j.url && <a className="btn-ghost" href={j.url} target="_blank" rel="noreferrer">Open</a>}
                <button className="btn-ghost" onClick={() => removeJob(j.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
