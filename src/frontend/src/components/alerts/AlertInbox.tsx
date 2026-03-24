"use client";

import { useState, useEffect } from "react";
import { getAlerts, triageAlert, getAlertStats, type Alert, type AlertStats } from "@/lib/api";

const STATUSES = ["all", "new", "triaged", "confirmed", "dismissed", "escalated"];
const PRIORITIES = ["all", "critical", "high", "medium", "low", "info"];

function PriorityBadge({ priority }: { priority: string }) {
  const classes: Record<string, string> = {
    critical: "badge-critical",
    high: "badge-high",
    medium: "badge-medium",
    low: "badge-low",
    info: "badge-info",
  };
  return <span className={`badge ${classes[priority] || "badge-info"}`}>{priority}</span>;
}

function StatusBadge({ status }: { status: string }) {
  const classes: Record<string, string> = {
    new: "bg-blue-900/50 text-blue-300",
    triaged: "bg-yellow-900/50 text-yellow-300",
    confirmed: "bg-green-900/50 text-green-300",
    dismissed: "bg-gray-700 text-gray-400",
    escalated: "bg-red-900/50 text-red-300",
  };
  return <span className={`badge ${classes[status] || "badge-info"}`}>{status}</span>;
}

export default function AlertInbox() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [statusFilter, setStatusFilter] = useState("new");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const [alertData, statsData] = await Promise.all([
        getAlerts({
          status: statusFilter === "all" ? undefined : statusFilter,
          priority: priorityFilter === "all" ? undefined : priorityFilter,
        }),
        getAlertStats(),
      ]);
      setAlerts(alertData.items);
      setTotal(alertData.total);
      setStats(statsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, priorityFilter]);

  const handleTriage = async (id: string, status: string) => {
    try {
      await triageAlert(id, { status, feedback: status === "dismissed" ? "dismissed" : "confirmed" });
      fetchAlerts();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-100">Alert Inbox</h2>
        <p className="text-sm text-gray-500">
          Machine-generated signals requiring analyst review
        </p>
      </div>

      {/* Stats bar */}
      {stats && (
        <div className="mb-4 flex gap-3">
          {Object.entries(stats.by_status).map(([s, c]) => (
            <div key={s} className="card flex-1 text-center">
              <div className="text-2xl font-bold text-gray-200">{c}</div>
              <div className="text-xs text-gray-500">{s}</div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Status:</span>
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`rounded px-2 py-1 text-xs ${
                statusFilter === s
                  ? "bg-intel-600 text-white"
                  : "bg-gray-800 text-gray-400"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Priority:</span>
          {PRIORITIES.map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`rounded px-2 py-1 text-xs ${
                priorityFilter === p
                  ? "bg-intel-600 text-white"
                  : "bg-gray-800 text-gray-400"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Alert list */}
      <div className="text-sm text-gray-500 mb-2">{total} alerts</div>
      {loading ? (
        <div className="text-center text-gray-500 py-8">Loading...</div>
      ) : alerts.length === 0 ? (
        <div className="text-center text-gray-500 py-8">No alerts matching filters.</div>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div key={alert.id} className="card flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <PriorityBadge priority={alert.priority} />
                  <StatusBadge status={alert.status} />
                  <span className="badge badge-info">{alert.alert_type}</span>
                </div>
                <h3 className="font-medium text-gray-200">{alert.title}</h3>
                {alert.summary && (
                  <p className="text-sm text-gray-400 mt-1">{alert.summary}</p>
                )}
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(alert.created_at).toLocaleString()}
                </div>
              </div>
              {alert.status === "new" && (
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleTriage(alert.id, "confirmed")}
                    className="btn-primary text-xs"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => handleTriage(alert.id, "dismissed")}
                    className="btn-secondary text-xs"
                  >
                    Dismiss
                  </button>
                  <button
                    onClick={() => handleTriage(alert.id, "escalated")}
                    className="btn-danger text-xs"
                  >
                    Escalate
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
