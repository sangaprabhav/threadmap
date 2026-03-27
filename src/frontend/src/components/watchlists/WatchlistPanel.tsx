"use client";

import { useState, useEffect } from "react";
import {
  getWatchlists,
  createWatchlist,
  addWatchlistEntry,
  type Watchlist,
} from "@/lib/api";

export default function WatchlistPanel() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newType, setNewType] = useState("keyword");
  const [entryValue, setEntryValue] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchWatchlists = async () => {
    try {
      setLoading(true);
      const data = await getWatchlists();
      setWatchlists(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const wl = await createWatchlist({
        name: newName,
        description: newDesc,
        watch_type: newType,
      });
      setWatchlists([wl, ...watchlists]);
      setShowCreate(false);
      setNewName("");
      setNewDesc("");
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddEntry = async () => {
    if (!selectedId || !entryValue.trim()) return;
    try {
      await addWatchlistEntry(selectedId, { value: entryValue, entry_type: "keyword" });
      setEntryValue("");
      fetchWatchlists();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Watchlists</h2>
          <p className="text-sm text-gray-500">
            Monitor keywords, handles, domains, and patterns
          </p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          New Watchlist
        </button>
      </div>

      {showCreate && (
        <div className="card mb-4 border-intel-700">
          <h3 className="font-medium text-gray-200 mb-3">Create Watchlist</h3>
          <input
            type="text"
            placeholder="Watchlist name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="mb-2 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
          />
          <input
            type="text"
            placeholder="Description"
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            className="mb-2 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
          />
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="mb-3 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
          >
            <option value="keyword">Keyword</option>
            <option value="actor">Actor/Handle</option>
            <option value="domain">Domain</option>
            <option value="hashtag">Hashtag</option>
            <option value="entity">Entity</option>
          </select>
          <div className="flex gap-2">
            <button onClick={handleCreate} className="btn-primary text-xs">Create</button>
            <button onClick={() => setShowCreate(false)} className="btn-secondary text-xs">Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-gray-500 text-center py-8">Loading...</div>
      ) : watchlists.length === 0 ? (
        <div className="text-gray-500 text-center py-8">No watchlists yet.</div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {watchlists.map((wl) => (
            <div
              key={wl.id}
              className={`card cursor-pointer transition-colors ${
                selectedId === wl.id ? "border-intel-600" : "hover:border-gray-700"
              }`}
              onClick={() => setSelectedId(wl.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-200">{wl.name}</h3>
                <div className="flex gap-1">
                  <span className="badge badge-platform">{wl.watch_type}</span>
                  {wl.is_active && <span className="badge badge-low">active</span>}
                </div>
              </div>
              {wl.description && (
                <p className="text-sm text-gray-400 mb-2">{wl.description}</p>
              )}
              <div className="text-xs text-gray-500">
                {wl.entry_count} entries | {wl.alert_on_match ? "alerts on" : "alerts off"}
              </div>

              {selectedId === wl.id && (
                <div className="mt-3 border-t border-gray-800 pt-3">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={entryValue}
                      onChange={(e) => setEntryValue(e.target.value)}
                      placeholder="Add entry..."
                      className="flex-1 rounded bg-gray-800 border border-gray-700 px-2 py-1 text-xs text-gray-200"
                      onKeyDown={(e) => e.key === "Enter" && handleAddEntry()}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAddEntry();
                      }}
                      className="btn-primary text-xs"
                    >
                      Add
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
