import { Search, Bell, ChevronDown } from "lucide-react";
import { currentUser } from "../lib/mockData";

export default function TopNav() {
  return (
    <header className="flex items-center justify-between border-b border-ink/10 bg-white px-6 py-3">
      <div className="relative w-full max-w-md">
        <Search
          size={16}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate2"
        />
        <input
          type="text"
          placeholder="Search LR no., truck no., invoice..."
          className="w-full rounded-md border border-ink/10 bg-paper py-2 pl-9 pr-3 text-sm font-mono placeholder:font-body placeholder:text-slate2/70 focus:border-amber focus:outline-none"
        />
      </div>

      <div className="flex items-center gap-4">
        <button
          aria-label="Notifications"
          className="relative rounded-md p-2 text-slate2 hover:bg-paper"
        >
          <Bell size={18} />
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-alert" />
        </button>
        <div className="flex items-center gap-2 border-l border-ink/10 pl-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-xs font-semibold text-white">
            {currentUser.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-sm font-medium leading-tight">{currentUser.name}</p>
            <p className="text-xs text-slate2 leading-tight">{currentUser.company}</p>
          </div>
          <ChevronDown size={14} className="text-slate2" />
        </div>
      </div>
    </header>
  );
}
