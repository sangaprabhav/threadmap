"use client";

import { useState, useEffect } from "react";
import { getCases, createCase, updateCase, addCaseNote, type Case } from "@/lib/api";

export default function CaseWorkspace() {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [noteText, setNoteText] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const data = await getCases();
      setCases(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    try {
      const c = await createCase({ title: newTitle, description: newDesc });
      setCases([c, ...cases]);
      setShowCreate(false);
      setNewTitle("");
      setNewDesc("");
    } catch (e) {
      console.error(e);
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      const updated = await updateCase(id, { status });
      setCases(cases.map((c) => (c.id === id ? updated : c)));
      if (selectedCase?.id === id) setSelectedCase(updated);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddNote = async () => {
    if (!selectedCase || !noteText.trim()) return;
    try {
      const updated = await addCaseNote(selectedCase.id, { text: noteText });
      setSelectedCase(updated);
      setCases(cases.map((c) => (c.id === updated.id ? updated : c)));
      setNoteText("");
    } catch (e) {
      console.error(e);
    }
  };

  const statusColors: Record<string, string> = {
    open: "badge-info",
    in_progress: "badge-medium",
    review: "badge-high",
    closed: "badge-low",
    archived: "bg-gray-700 text-gray-400",
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Case Workspace</h2>
          <p className="text-sm text-gray-500">Analyst-owned investigations</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          New Case
        </button>
      </div>

      {/* Create modal */}
      {showCreate && (
        <div className="card mb-4 border-intel-700">
          <h3 className="font-medium text-gray-200 mb-3">Create Investigation</h3>
          <input
            type="text"
            placeholder="Case title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="mb-2 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
          />
          <textarea
            placeholder="Description"
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            className="mb-3 w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
            rows={3}
          />
          <div className="flex gap-2">
            <button onClick={handleCreate} className="btn-primary text-xs">Create</button>
            <button onClick={() => setShowCreate(false)} className="btn-secondary text-xs">Cancel</button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        {/* Case list */}
        <div className="col-span-1 space-y-2">
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : cases.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No cases yet.</div>
          ) : (
            cases.map((c) => (
              <div
                key={c.id}
                onClick={() => setSelectedCase(c)}
                className={`card cursor-pointer transition-colors ${
                  selectedCase?.id === c.id ? "border-intel-600" : "hover:border-gray-700"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`badge ${statusColors[c.status] || "badge-info"}`}>
                    {c.status}
                  </span>
                  <span className={`badge badge-${c.priority === "critical" ? "critical" : c.priority}`}>
                    {c.priority}
                  </span>
                </div>
                <h3 className="font-medium text-gray-200 text-sm">{c.title}</h3>
                <div className="text-xs text-gray-500 mt-1">
                  Updated {new Date(c.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Case detail */}
        <div className="col-span-2">
          {selectedCase ? (
            <div className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-200">{selectedCase.title}</h3>
                  {selectedCase.description && (
                    <p className="text-sm text-gray-400 mt-1">{selectedCase.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  {["open", "in_progress", "review", "closed"].map((s) => (
                    <button
                      key={s}
                      onClick={() => handleStatusChange(selectedCase.id, s)}
                      className={`rounded px-2 py-1 text-xs ${
                        selectedCase.status === s
                          ? "bg-intel-600 text-white"
                          : "bg-gray-800 text-gray-400"
                      }`}
                    >
                      {s.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>

              {selectedCase.tags && selectedCase.tags.length > 0 && (
                <div className="mb-4 flex gap-1">
                  {selectedCase.tags.map((t) => (
                    <span key={t} className="rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-400">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {/* Notes */}
              <div className="border-t border-gray-800 pt-4">
                <h4 className="text-sm font-medium text-gray-300 mb-3">Investigation Notes</h4>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Add a note..."
                    className="flex-1 rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-200"
                    onKeyDown={(e) => e.key === "Enter" && handleAddNote()}
                  />
                  <button onClick={handleAddNote} className="btn-primary text-xs">
                    Add
                  </button>
                </div>
                <div className="text-xs text-gray-500">
                  Created {new Date(selectedCase.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              Select a case or create a new investigation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
