import { IndianRupee, Truck, PackageCheck, Clock, Wallet, Scale } from "lucide-react";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import StatCard from "../components/StatCard";
import LifecycleRail from "../components/LifecycleRail";
import RevenueChart from "../components/RevenueChart";
import StatusBadge from "../components/StatusBadge";
import {
  summaryStats,
  lifecycleStages,
  recentRecords,
  formatINR,
} from "../lib/mockData";

export default function Dashboard() {
  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <TopNav />

        <main className="flex-1 space-y-6 p-6">
          <div>
            <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
            <p className="text-sm text-slate2">
              Overview across all your active consignments today.
            </p>
          </div>

          {/* Summary cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <StatCard
              label="Total Records"
              value={summaryStats.totalRecords.toLocaleString("en-IN")}
              icon={Truck}
            />
            <StatCard
              label="Active Trips"
              value={summaryStats.activeTrips}
              accent="amber"
              icon={Clock}
            />
            <StatCard
              label="Delivered"
              value={summaryStats.delivered.toLocaleString("en-IN")}
              accent="cargo"
              icon={PackageCheck}
            />
            <StatCard
              label="Pending Payments"
              value={summaryStats.pendingPayments}
              accent="alert"
              icon={Wallet}
            />
            <StatCard
              label="Total Revenue"
              value={formatINR(summaryStats.totalRevenue)}
              accent="amber"
              icon={IndianRupee}
            />
            <StatCard
              label="Weight Loss (MT)"
              value={summaryStats.weightLossMt}
              sublabel="This month"
              icon={Scale}
            />
          </div>

          {/* Signature lifecycle rail */}
          <LifecycleRail stages={lifecycleStages} />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Revenue chart */}
            <div className="rounded-lg border border-ink/10 bg-white p-5 lg:col-span-2">
              <h3 className="mb-1 font-display text-sm font-semibold text-ink">
                Revenue vs Transport Cost
              </h3>
              <p className="mb-2 text-xs text-slate2">Last 7 months, all companies</p>
              <RevenueChart />
            </div>

            {/* Profit & Loss card */}
            <div className="rounded-lg border border-ink/10 bg-ink p-5 text-white">
              <h3 className="mb-4 font-display text-sm font-semibold">
                Profit &amp; Loss
              </h3>
              <p className="font-mono tabular text-3xl font-semibold text-amber">
                {formatINR(summaryStats.profitLoss)}
              </p>
              <p className="mt-1 text-xs text-paper/60">Net margin this period</p>

              <div className="mt-5 space-y-3 border-t border-white/10 pt-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-paper/60">Margin</span>
                  <span className="font-mono tabular font-medium">
                    {summaryStats.margin}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-paper/60">Transport Cost</span>
                  <span className="font-mono tabular font-medium">
                    {formatINR(summaryStats.totalTransportCost)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-paper/60">Pending Deliveries</span>
                  <span className="font-mono tabular font-medium">
                    {summaryStats.pendingDeliveries}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent records table */}
          <div className="rounded-lg border border-ink/10 bg-white">
            <div className="flex items-center justify-between border-b border-ink/10 p-5">
              <h3 className="font-display text-sm font-semibold text-ink">
                Recent Activity
              </h3>
              <button className="text-xs font-medium text-amber-dark hover:underline">
                View all records
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-ink/10 text-xs uppercase tracking-wide text-slate2">
                    <th className="px-5 py-3 font-medium">LR No.</th>
                    <th className="px-5 py-3 font-medium">Truck No.</th>
                    <th className="px-5 py-3 font-medium">Transporter</th>
                    <th className="px-5 py-3 font-medium">Loading Location</th>
                    <th className="px-5 py-3 font-medium">Status</th>
                    <th className="px-5 py-3 font-medium text-right">Invoice Amt.</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRecords.map((r) => (
                    <tr
                      key={r.record_id}
                      className="border-b border-ink/5 last:border-0 hover:bg-paper/60"
                    >
                      <td className="px-5 py-3 font-mono tabular text-ink">{r.lr_no}</td>
                      <td className="px-5 py-3 font-mono tabular text-slate2">
                        {r.truck_number}
                      </td>
                      <td className="px-5 py-3">{r.transporter_name}</td>
                      <td className="px-5 py-3 text-slate2">{r.loading_location}</td>
                      <td className="px-5 py-3">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="px-5 py-3 text-right font-mono tabular text-ink">
                        {formatINR(r.invoice_amount_raised)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
