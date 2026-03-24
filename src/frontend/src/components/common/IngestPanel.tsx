"use client";

import { useState } from "react";
import { ingestUrl, ingestText, type IngestResponse } from "@/lib/api";

type IngestMode = "url" | "text" | "csv";

export default function IngestPanel() {
  const [mode, setMode] = useState<IngestMode>("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      let res: IngestResponse;
      if (mode === "url") {
        res = await ingestUrl({ url, title: title || undefined });
      } else {
        res = await ingestText({ text, title: title || undefined });
      }
      setResult(res);
      setUrl("");
      setText("");
      setTitle("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-100">Evidence Ingest</h2>
        <p className="text-sm text-gray-500">
          Submit URLs, text, screenshots, or data files as evidence
        </p>
      </div>

      {/* Mode tabs */}
      <div className="mb-4 flex gap-2">
        {(["url", "text", "csv"] as IngestMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`rounded px-3 py-1 text-sm ${
              mode === m ? "bg-intel-600 text-white" : "bg-gray-800 text-gray-400"
            }`}
          >
            {m.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="card max-w-2xl">
        <input
          type="text"
          placeholder="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mb-3 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
        />

        {mode === "url" ? (
          <input
            type="url"
            placeholder="https://..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="mb-3 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
          />
        ) : (
          <textarea
            placeholder={mode === "csv" ? "Paste CSV content..." : "Paste evidence text..."}
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            className="mb-3 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200 font-mono"
          />
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? "Ingesting..." : "Submit Evidence"}
        </button>

        {result && (
          <div className="mt-4 rounded bg-green-950/50 border border-green-800 p-3 text-sm text-green-300">
            {result.message}
          </div>
        )}
        {error && (
          <div className="mt-4 rounded bg-red-950/50 border border-red-800 p-3 text-sm text-red-300">
            {error}
          </div>
        )}
      </div>

      <div className="mt-8 card max-w-2xl border-gray-700 bg-gray-900/50">
        <h3 className="text-sm font-medium text-gray-400 mb-2">Supported Ingest Modes</h3>
        <ul className="text-xs text-gray-500 space-y-1">
          <li>URL — submit any public URL as evidence</li>
          <li>Text — paste free-form text (posts, transcripts, notes)</li>
          <li>CSV — upload structured data with text/url columns</li>
          <li>Phase 2: Screenshots, PDFs, JSON exports, media files</li>
        </ul>
      </div>
    </div>
  );
}
