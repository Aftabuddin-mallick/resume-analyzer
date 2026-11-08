export function scoreColor(score) {
  if (score >= 70) return "#0E9F8E";
  if (score >= 45) return "#D98E04";
  return "#C2412D";
}

export default function ScoreDial({ score = 0, size = 168, label = "match" }) {
  const stroke = 12;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  return (
    <div className="relative" style={{ width: size, height: size }} role="img" aria-label={`${pct} percent ${label}`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#14213D" strokeOpacity="0.1" strokeWidth={stroke} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={scoreColor(pct)} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c - (pct / 100) * c}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-bold">{Math.round(pct)}%</span>
        <span className="text-xs font-semibold text-ink/60">{label}</span>
      </div>
    </div>
  );
}
