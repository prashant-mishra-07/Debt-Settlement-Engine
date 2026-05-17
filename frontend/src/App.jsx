import { useEffect, useState } from "react";
import GroupManager from "./components/GroupManager";
import TransactionForm from "./components/TransactionForm";
import DebtLedger from "./components/DebtLedger";
import { getGroup, optimizeGroup } from "./api/client";

function App() {
  const [group, setGroup] = useState(null);
  const [rawTransactions, setRawTransactions] = useState([]);
  const [optimizedTransactions, setOptimizedTransactions] = useState([]);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!group) {
      setRawTransactions([]);
      setOptimizedTransactions([]);
      setOptimizationResult(null);
      return;
    }

    setRawTransactions(group.raw_transactions ?? []);
    setOptimizedTransactions(group.optimized_transactions ?? []);
  }, [group]);

  const refreshGroup = async () => {
    if (!group) return;
    setError(null);
    setLoading(true);

    try {
      const updatedGroup = await getGroup(group.group_id);
      setGroup(updatedGroup);
      setOptimizationResult(null);
    } catch (err) {
      setError(err.message || "Failed to refresh group.");
    } finally {
      setLoading(false);
    }
  };

  const handleGroupCreated = (newGroup) => {
    setGroup(newGroup);
    setRawTransactions(newGroup.raw_transactions ?? []);
    setOptimizedTransactions(newGroup.optimized_transactions ?? []);
    setOptimizationResult(null);
    setError(null);
  };

  const handleTransactionAdded = async () => {
    await refreshGroup();
  };

  const handleOptimize = async () => {
    if (!group || isOptimizing) return;

    setError(null);
    setIsOptimizing(true);

    try {
      const result = await optimizeGroup(group.group_id);
      setOptimizedTransactions(result.optimized_transactions ?? []);
      setOptimizationResult(result);
    } catch (err) {
      setError(
        err.message?.includes("C++ optimizer")
          ? "The optimization engine failed. Please try again or contact support."
          : err.message || "Optimization failed."
      );
    } finally {
      setIsOptimizing(false);
    }
  };

  const reductionSummary = () => {
    if (!optimizationResult) return null;
    const fromCount = optimizationResult.original_count ?? rawTransactions.length;
    const toCount = optimizationResult.optimized_count ?? optimizedTransactions.length;
    return `Reduced from ${fromCount} transactions to ${toCount} (${optimizationResult.reduction_percentage?.toFixed(1)}% reduction)`;
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-10 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-sky-600">Debt Settlement Engine</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                Frontend Dashboard
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                Create groups, add transactions, and run the C++ optimization engine with live database persistence.
              </p>
            </div>
            {group && (
              <div className="rounded-2xl bg-slate-50 px-6 py-4 text-sm text-slate-600 shadow-sm">
                <p className="font-medium text-slate-900">Current Group</p>
                <p>{group.name}</p>
                <p className="mt-1 text-slate-500">ID: {group.group_id}</p>
              </div>
            )}
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <div className="space-y-6">
            <GroupManager onGroupCreated={handleGroupCreated} isOptimizing={isOptimizing} />

            {group && (
              <TransactionForm
                groupId={group.group_id}
                onTransactionAdded={handleTransactionAdded}
              />
            )}
          </div>

          <div className="space-y-6">
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Optimization Controls</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Run the debt optimizer for the current selected group.
                  </p>
                </div>
                <button
                  type="button"
                  disabled={!group || rawTransactions.length === 0 || isOptimizing}
                  onClick={handleOptimize}
                  className="inline-flex items-center justify-center rounded-2xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
                >
                  {isOptimizing ? "Optimizing..." : "Run Optimization Engine"}
                </button>
              </div>

              {group && (
                <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-600">
                  <p>Raw transactions: {rawTransactions.length}</p>
                  <p className="mt-1">Optimized transactions: {optimizedTransactions.length}</p>
                  <p className="mt-1">Cached optimized state: {group.is_optimized ? "Yes" : "No"}</p>
                </div>
              )}

              {optimizationResult && (
                <div className="mt-4 rounded-2xl bg-slate-900 px-4 py-4 text-sm text-white">
                  <p className="font-medium">Optimization Results</p>
                  <p className="mt-2">{reductionSummary()}</p>
                </div>
              )}
            </section>

            {error && (
              <section className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700 shadow-sm">
                {error}
              </section>
            )}
          </div>
        </div>

        {group && (
          <div className="mt-8 grid gap-6 xl:grid-cols-2">
            <DebtLedger title="Raw Transactions" transactions={rawTransactions} />
            <DebtLedger title="Optimized Transactions" transactions={optimizedTransactions} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
