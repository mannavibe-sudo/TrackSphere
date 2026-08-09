import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Truck,
  Building2,
  Users,
  FileBarChart,
  Settings,
  Radio,
  Plus,
} from "lucide-react";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/records", label: "Records", icon: Truck },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/users", label: "Users", icon: Users },
  { to: "/reports", label: "Reports", icon: FileBarChart },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="hidden md:flex w-60 shrink-0 flex-col bg-ink text-paper/90">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-white/10">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-amber text-ink">
          <Radio size={18} strokeWidth={2.5} />
        </div>
        <div>
          <p className="font-display text-sm font-semibold tracking-tight text-white">
            TrackSphere
          </p>
          <p className="text-[10px] uppercase tracking-wider text-paper/50">
            Multi-company tracking
          </p>
        </div>
      </div>

      <div className="px-3 pt-4">
        <NavLink
          to="/records/new"
          className="flex items-center justify-center gap-1.5 rounded-md bg-amber px-3 py-2 text-sm font-medium text-ink hover:bg-amber-dark"
        >
          <Plus size={16} strokeWidth={2.5} />
          New Record
        </NavLink>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-white/10 text-white font-medium"
                  : "text-paper/70 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            <Icon size={17} strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-white/10 text-[11px] text-paper/40">
        v0.1 — Module 10 preview
      </div>
    </aside>
  );
}
