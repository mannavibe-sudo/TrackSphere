import { statusLabel } from "../lib/mockData";

const styles = {
  draft: "bg-slate2/10 text-slate2",
  loading: "bg-amber/15 text-amber-dark",
  dispatched: "bg-amber/15 text-amber-dark",
  in_transit: "bg-ink/10 text-ink",
  delivered: "bg-cargo/15 text-cargo",
  invoice_raised: "bg-cargo/15 text-cargo",
  payment_received: "bg-cargo-light/20 text-cargo",
  closed: "bg-ink text-white",
};

export default function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}
    >
      {statusLabel[status]}
    </span>
  );
}
