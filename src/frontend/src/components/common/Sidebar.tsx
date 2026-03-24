"use client";

interface SidebarProps {
  activeView: string;
  onNavigate: (view: any) => void;
}

const navItems = [
  { id: "stream", label: "Live Stream", icon: "R" },
  { id: "alerts", label: "Alert Inbox", icon: "!" },
  { id: "cases", label: "Cases", icon: "C" },
  { id: "watchlists", label: "Watchlists", icon: "W" },
  { id: "briefs", label: "Daily Brief", icon: "B" },
  { id: "ingest", label: "Ingest", icon: "+" },
];

export default function Sidebar({ activeView, onNavigate }: SidebarProps) {
  return (
    <aside className="flex w-56 flex-col border-r border-gray-800 bg-gray-950">
      <div className="border-b border-gray-800 p-4">
        <h1 className="text-lg font-bold text-intel-400">ThreadMap</h1>
        <p className="text-xs text-gray-500">Intelligence OS v0.1</p>
      </div>
      <nav className="flex-1 p-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`mb-1 flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors ${
              activeView === item.id
                ? "bg-intel-900/50 text-intel-300"
                : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
            }`}
          >
            <span className="flex h-6 w-6 items-center justify-center rounded bg-gray-800 text-xs font-mono">
              {item.icon}
            </span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="border-t border-gray-800 p-4 text-xs text-gray-600">
        Event-native. Provenance-first.
      </div>
    </aside>
  );
}
