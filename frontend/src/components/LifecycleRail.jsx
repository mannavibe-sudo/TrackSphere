import { statusLabel } from "../lib/mockData";

// The signature visual for TrackSphere: records move along a physical rail
// from Draft to Closed, exactly like a consignment moves through a yard.
// Segment width is proportional to how many records sit at that stage.
export default function LifecycleRail({ stages }) {
  const total = stages.reduce((sum, s) => sum + s.count, 0);

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-5">
      <div className="mb-4 flex items-baseline justify-between">
        <h3 className="font-display text-sm font-semibold text-ink">
          Consignment Lifecycle
        </h3>
        <span className="font-mono tabular text-xs text-slate2">
          {total.toLocaleString("en-IN")} active + closed
        </span>
      </div>

      {/* The rail */}
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-paper">
        {stages.map((stage, i) => {
          const pct = Math.max((stage.count / total) * 100, 2);
          const isClosed = stage.key === "closed";
          return (
            <div
              key={stage.key}
              style={{ width: `${pct}%` }}
              className={`h-full ${i > 0 ? "border-l border-white" : ""} ${
                isClosed
                  ? "bg-cargo"
                  : stage.key === "payment_received"
                  ? "bg-cargo-light"
                  : "bg-amber"
              }`}
              title={`${statusLabel[stage.key]}: ${stage.count}`}
            />
          );
        })}
      </div>

      {/* Stage labels */}
      <div className="mt-4 grid grid-cols-4 gap-3 sm:grid-cols-8">
        {stages.map((stage) => (
          <div key={stage.key} className="min-w-0">
            <p className="truncate text-[11px] uppercase tracking-wide text-slate2">
              {statusLabel[stage.key]}
            </p>
            <p className="font-mono tabular text-sm font-semibold text-ink">
              {stage.count}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
