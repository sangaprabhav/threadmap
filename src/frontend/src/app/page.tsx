"use client";

import { useState } from "react";
import Sidebar from "@/components/common/Sidebar";
import LiveStream from "@/components/stream/LiveStream";
import AlertInbox from "@/components/alerts/AlertInbox";
import CaseWorkspace from "@/components/cases/CaseWorkspace";
import WatchlistPanel from "@/components/watchlists/WatchlistPanel";
import DailyBrief from "@/components/briefs/DailyBrief";
import IngestPanel from "@/components/common/IngestPanel";

type View =
  | "stream"
  | "alerts"
  | "cases"
  | "watchlists"
  | "briefs"
  | "ingest";

export default function Home() {
  const [activeView, setActiveView] = useState<View>("stream");

  const views: Record<View, React.ReactNode> = {
    stream: <LiveStream />,
    alerts: <AlertInbox />,
    cases: <CaseWorkspace />,
    watchlists: <WatchlistPanel />,
    briefs: <DailyBrief />,
    ingest: <IngestPanel />,
  };

  return (
    <div className="flex h-screen">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <main className="flex-1 overflow-auto p-6">{views[activeView]}</main>
    </div>
  );
}
