"use client";

import { useState, useEffect } from "react";
import { getStream, type ContentItem } from "@/lib/api";

const PLATFORMS = ["all", "bluesky", "x", "reddit", "youtube", "rss", "manual"];

function PlatformBadge({ platform }: { platform: string | null }) {
  const colors: Record<string, string> = {
    bluesky: "bg-blue-900/50 text-blue-300",
    x: "bg-gray-700 text-gray-200",
    reddit: "bg-orange-900/50 text-orange-300",
    youtube: "bg-red-900/50 text-red-300",
    rss: "bg-amber-900/50 text-amber-300",
    manual: "bg-purple-900/50 text-purple-300",
  };
  return (
    <span className={`badge ${colors[platform || ""] || "badge-info"}`}>
      {platform || "unknown"}
    </span>
  );
}

function RiskBadge({ score }: { score: number | null }) {
  if (!score || score < 0.1) return null;
  const level =
    score >= 0.7 ? "critical" : score >= 0.5 ? "high" : score >= 0.3 ? "medium" : "low";
  return <span className={`badge badge-${level}`}>risk: {score.toFixed(2)}</span>;
}

function ContentCard({ item }: { item: ContentItem }) {
  const text = item.text || item.title || "(no text)";
  const preview = text.length > 300 ? text.slice(0, 300) + "..." : text;

  return (
    <div className="card mb-3 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="mb-2 flex items-center gap-2">
            <PlatformBadge platform={item.platform} />
            <span className="badge badge-info">{item.content_type}</span>
            <RiskBadge score={item.risk_score} />
            {item.language && (
              <span className="text-xs text-gray-500">{item.language}</span>
            )}
          </div>
          {item.title && (
            <h3 className="mb-1 font-medium text-gray-200">{item.title}</h3>
          )}
          <p className="text-sm text-gray-400 leading-relaxed">{preview}</p>
          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
            {item.source_url && (
              <a
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-intel-400 underline"
              >
                source
              </a>
            )}
            {item.observed_at && (
              <span>{new Date(item.observed_at).toLocaleString()}</span>
            )}
            {item.like_count != null && <span>{item.like_count} likes</span>}
            {item.reply_count != null && <span>{item.reply_count} replies</span>}
          </div>
          {item.topics && item.topics.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {item.topics.map((t) => (
                <span key={t} className="rounded bg-gray-800 px-1.5 py-0.5 text-xs text-gray-400">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LiveStream() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [platform, setPlatform] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStream = async () => {
    try {
      setLoading(true);
      const data = await getStream(50, platform === "all" ? undefined : platform);
      setItems(data);
      setError(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStream();
    const interval = setInterval(fetchStream, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, [platform]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Live Event Stream</h2>
          <p className="text-sm text-gray-500">
            Real-time intelligence feed across all sources
          </p>
        </div>
        <div className="flex items-center gap-2">
          {PLATFORMS.map((p) => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                platform === p
                  ? "bg-intel-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-gray-200"
              }`}
            >
              {p}
            </button>
          ))}
          <button onClick={fetchStream} className="btn-secondary text-xs">
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="card mb-4 border-red-800 bg-red-950/50 text-red-300">
          {error}
        </div>
      )}

      {loading && items.length === 0 ? (
        <div className="text-center text-gray-500 py-12">Loading stream...</div>
      ) : items.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          No content yet. Start collectors or ingest evidence.
        </div>
      ) : (
        <div>
          {items.map((item) => (
            <ContentCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
