"use client";

import { useState, useEffect } from "react";
import { getDailyBrief, type DailyBrief as DailyBriefType } from "@/lib/api";

export default function DailyBrief() {
  const [brief, setBrief] = useState<DailyBriefType | null>(null);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBrief = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDailyBrief(hours);
      setBrief(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrief();
  }, [hours]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Daily Intelligence Brief</h2>
          <p className="text-sm text-gray-500">
            Structured summary with provenance-linked evidence
          </p>
        </div>
        <div className="flex items-center gap-2">
          {[12, 24, 48, 72].map((h) => (
            <button
              key={h}
              onClick={() => setHours(h)}
              className={`rounded px-3 py-1 text-xs ${
                hours === h ? "bg-intel-600 text-white" : "bg-gray-800 text-gray-400"
              }`}
            >
              {h}h
            </button>
          ))}
          <button onClick={fetchBrief} className="btn-secondary text-xs">
            Regenerate
          </button>
        </div>
      </div>

      {error && (
        <div className="card mb-4 border-red-800 bg-red-950/50 text-red-300">{error}</div>
      )}

      {loading ? (
        <div className="text-gray-500 text-center py-12">Generating brief...</div>
      ) : brief ? (
        <div className="space-y-6">
          {/* Summary */}
          <div className="card">
            <h3 className="font-medium text-gray-200 mb-3">Overview</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-intel-400">
                  {brief.summary.total_content_items}
                </div>
                <div className="text-xs text-gray-500">Total Items</div>
              </div>
              {Object.entries(brief.summary.platform_breakdown).map(([platform, count]) => (
                <div key={platform} className="text-center">
                  <div className="text-2xl font-bold text-gray-300">{count}</div>
                  <div className="text-xs text-gray-500">{platform}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Alert summary */}
          {Object.keys(brief.summary.alert_summary).length > 0 && (
            <div className="card">
              <h3 className="font-medium text-gray-200 mb-3">Alert Summary</h3>
              <div className="flex gap-4">
                {Object.entries(brief.summary.alert_summary).map(([status, count]) => (
                  <div key={status} className="text-center">
                    <div className="text-xl font-bold text-gray-300">{count}</div>
                    <div className="text-xs text-gray-500">{status}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* High risk content */}
          {brief.high_risk_content.length > 0 && (
            <div className="card">
              <h3 className="font-medium text-red-300 mb-3">High Risk Content</h3>
              <div className="space-y-3">
                {brief.high_risk_content.map((item) => (
                  <div key={item.id} className="rounded bg-gray-800 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="badge badge-platform">{item.platform}</span>
                      <span className="badge badge-critical">
                        risk: {item.risk_score.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{item.text_preview}</p>
                    {item.source_url && (
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-intel-400 hover:underline mt-1 inline-block"
                      >
                        View source
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent alerts */}
          {brief.recent_alerts.length > 0 && (
            <div className="card">
              <h3 className="font-medium text-gray-200 mb-3">Recent Alerts</h3>
              <div className="space-y-2">
                {brief.recent_alerts.map((alert) => (
                  <div key={alert.id} className="flex items-center gap-3 rounded bg-gray-800 px-3 py-2">
                    <span className={`badge badge-${alert.priority}`}>{alert.priority}</span>
                    <span className="badge badge-info">{alert.type}</span>
                    <span className="text-sm text-gray-300 flex-1">{alert.title}</span>
                    <span className={`badge ${
                      alert.status === "new" ? "bg-blue-900/50 text-blue-300" : "bg-gray-700 text-gray-400"
                    }`}>
                      {alert.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Provenance */}
          <div className="card border-gray-700 bg-gray-900/50">
            <h3 className="text-xs font-medium text-gray-400 mb-2">Provenance</h3>
            <div className="text-xs text-gray-500 space-y-1">
              <div>
                Sources: {brief.provenance.data_sources.join(", ") || "none"}
              </div>
              <div>Method: {brief.provenance.generation_method}</div>
              <div>Generated: {new Date(brief.generated_at).toLocaleString()}</div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
