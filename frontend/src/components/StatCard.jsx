export default function StatCard({ label, value, sublabel, accent = "ink", icon: Icon }) {
  const accentClasses = {
    ink: "text-ink",
    amber: "text-amber-dark",
    cargo: "text-cargo",
    alert: "text-alert",
  };

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-4">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-slate2">
          {label}
        </p>
        {Icon && <Icon size={16} className={accentClasses[accent]} strokeWidth={2} />}
      </div>
      <p className={`mt-2 font-mono tabular text-2xl font-semibold ${accentClasses[accent]}`}>
        {value}
      </p>
      {sublabel && <p className="mt-1 text-xs text-slate2">{sublabel}</p>}
    </div>
  );
}
