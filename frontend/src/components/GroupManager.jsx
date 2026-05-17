import { useState } from "react";
import { createGroup } from "../api/client";

export default function GroupManager({ onGroupCreated, isOptimizing }) {
  const [groupName, setGroupName] = useState("");
  const [error, setError] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    if (!groupName.trim()) {
      setError("Please enter a group name.");
      return;
    }

    setIsCreating(true);
    try {
      const group = await createGroup(groupName.trim());
      onGroupCreated(group);
      setGroupName("");
    } catch (err) {
      setError(err.message || "Failed to create group.");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Create a New Debt Group</h2>
      <p className="mt-2 text-sm text-slate-500">
        Create a new group to collect raw transactions and run the optimizer.
      </p>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Group Name</span>
          <input
            type="text"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            placeholder="Example: Family Settlement"
            className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
          />
        </label>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <button
          type="submit"
          disabled={isCreating || isOptimizing}
          className="inline-flex items-center justify-center rounded-2xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isCreating ? "Creating..." : isOptimizing ? "Please wait..." : "Create Group"}
        </button>
      </form>
    </section>
  );
}
