import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { ErrorBox, Spinner } from "../components/Bits.jsx";

export default function Analyze() {
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);

  function pick(f) {
    setError("");
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) return setError("Please choose a PDF file.");
    if (f.size > 5 * 1024 * 1024) return setError("PDF is too large. Maximum size is 5 MB.");
    setFile(f);
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!file) return setError("Upload your resume as a PDF first.");
    if (jd.trim().length < 30) return setError("Paste a longer job description (at least 30 characters).");
    setLoading(true);
    try {
      const result = await api.analyze(file, jd, title);
      navigate(`/analysis/${result.id}`);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="max-w-2xl text-3xl font-bold leading-tight sm:text-4xl">
        See how well your resume fits the job before you apply
      </h1>
      <p className="mt-3 max-w-xl text-ink/70">
        Upload your resume, paste the job description, and get a match score, the skills you are missing, and specific edits to make.
      </p>

      <form onSubmit={submit} className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="card flex flex-col">
          <h2 className="text-lg font-semibold">1. Your resume</h2>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); pick(e.dataTransfer.files?.[0]); }}
            className={`mt-4 flex flex-1 flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 py-10 text-center transition ${
              dragging ? "border-teal-600 bg-teal-50" : "border-ink/20 hover:border-ink/40"
            }`}
          >
            {file ? (
              <>
                <span className="font-semibold">{file.name}</span>
                <span className="mt-1 text-sm text-ink/60">{(file.size / 1024).toFixed(0)} KB. Click to replace.</span>
              </>
            ) : (
              <>
                <span className="font-semibold">Drop your PDF here or click to browse</span>
                <span className="mt-1 text-sm text-ink/60">Text-based PDF, up to 5 MB</span>
              </>
            )}
          </button>
          <input ref={inputRef} type="file" accept="application/pdf,.pdf" className="hidden" onChange={(e) => pick(e.target.files?.[0])} />
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold">2. The job</h2>
          <label className="mt-4 block text-sm font-semibold" htmlFor="title">Job title (optional)</label>
          <input id="title" className="input mt-1" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Backend Developer" maxLength={200} />
          <label className="mt-4 block text-sm font-semibold" htmlFor="jd">Job description</label>
          <textarea id="jd" className="input mt-1 h-48 resize-y" value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the full job description here" />
        </div>

        <div className="lg:col-span-2">
          <ErrorBox message={error} />
          <div className="mt-4 flex items-center gap-4">
            <button className="btn" disabled={loading}>
              {loading ? <Spinner label="Analyzing..." /> : "Analyze resume"}
            </button>
            {loading && <span className="text-sm text-ink/60">This can take up to a minute if the server is waking up.</span>}
          </div>
        </div>
      </form>
    </div>
  );
}
