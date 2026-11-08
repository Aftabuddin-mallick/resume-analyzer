export function Spinner({ label }) {
  return (
    <span className="inline-flex items-center gap-2">
      <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeOpacity="0.25" strokeWidth="4" />
        <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      </svg>
      {label}
    </span>
  );
}

export function ErrorBox({ message }) {
  if (!message) return null;
  return (
    <div role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800 ring-1 ring-red-200">
      {message}
    </div>
  );
}

export function Chips({ items, tone }) {
  const styles = tone === "good" ? "bg-teal-50 text-teal-700" : "bg-amber-50 text-amber-700";
  if (!items?.length) return <p className="text-sm text-ink/50">None</p>;
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((s) => (
        <span key={s} className={`chip ${styles}`}>{s}</span>
      ))}
    </div>
  );
}

export function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d) ? "" : d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}
