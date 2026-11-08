import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import ScoreDial from "../components/ScoreDial.jsx";
import { Chips, ErrorBox, formatDate, Spinner } from "../components/Bits.jsx";

function Section({ title, children }) {
  return (
    <section className="card">
      <h2 className="mb-3 text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function BulletList({ items }) {
  if (!items?.length) return <p className="text-sm text-ink/50">Nothing to show.</p>;
  return (
    <ul className="list-disc space-y-1.5 pl-5 text-sm">
      {items.map((t, i) => <li key={i}>{t}</li>)}
    </ul>
  );
}

export default function Result() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    setError("");
    api.getAnalysis(id).then(setData).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Spinner label="Loading analysis..." />;
  const fb = data.feedback || {};

  return (
    <div className="space-y-6">
      <div className="card flex flex-col items-center gap-6 sm:flex-row">
        <ScoreDial score={data.match_score} />
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{data.job_title || "Resume analysis"}</h1>
          <p className="text-sm text-ink/60">{data.filename} &middot; {formatDate(data.created_at)}</p>
          {fb.summary && <p className="mt-3 max-w-prose">{fb.summary}</p>}
          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            <span>Skill coverage: <strong>{Math.round(data.skill_score)}%</strong></span>
            <span>Text similarity: <strong>{Math.round(data.tfidf_score)}%</strong></span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link to={`/jobs?analysis=${data.id}`} className="btn">Rank jobs for this resume</Link>
            <Link to="/" className="btn-ghost">New analysis</Link>
          </div>
        </div>
      </div>

      {data.ai_source === "fallback" && (
        <p className="rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-700">
          AI suggestions are not available (no API key set or the AI service did not respond), so basic tips are shown.
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Skills you have"><Chips items={data.matched_skills} tone="good" /></Section>
        <Section title="Skills to add"><Chips items={data.missing_skills} tone="warn" /></Section>
        <Section title="Strengths"><BulletList items={fb.strengths} /></Section>
        <Section title="Gaps"><BulletList items={fb.weaknesses} /></Section>
      </div>

      {fb.suggestions?.length > 0 && (
        <Section title="Suggested improvements">
          <div className="space-y-4">
            {fb.suggestions.map((s, i) => (
              <div key={i} className="rounded-lg bg-paper p-4">
                <p className="text-sm font-semibold">{s.section}</p>
                <p className="mt-1 text-sm text-ink/70">{s.issue}</p>
                <p className="mt-2 text-sm">{s.suggestion}</p>
                {s.example && <p className="mt-2 border-l-4 border-teal-600 pl-3 text-sm italic">{s.example}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}

      {fb.rewritten_bullets?.length > 0 && (
        <Section title="Stronger bullet points">
          <div className="space-y-4">
            {fb.rewritten_bullets.map((b, i) => (
              <div key={i} className="grid gap-3 text-sm md:grid-cols-2">
                <p className="rounded-lg bg-red-50 p-3 text-red-900">{b.original}</p>
                <p className="rounded-lg bg-teal-50 p-3 text-teal-700">{b.improved}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {fb.keywords_to_add?.length > 0 && (
        <Section title="Keywords to work in"><Chips items={fb.keywords_to_add} tone="warn" /></Section>
      )}
    </div>
  );
}
