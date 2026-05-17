import { useState } from "react";
import { addTransaction } from "../api/client";

export default function TransactionForm({ groupId, onTransactionAdded }) {
  const [fromUser, setFromUser] = useState("");
  const [toUser, setToUser] = useState("");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (!fromUser.trim() || !toUser.trim() || !amount) {
      setError("Please complete all fields before submitting.");
      return;
    }

    const transactionData = {
      from_user: fromUser.trim(),
      to_user: toUser.trim(),
      amount: Number(amount),
    };

    if (isNaN(transactionData.amount) || transactionData.amount <= 0) {
      setError("Amount must be a valid positive number.");
      return;
    }

    setIsSubmitting(true);
    try {
      await addTransaction(groupId, transactionData);
      setFromUser("");
      setToUser("");
      setAmount("");
      onTransactionAdded();
    } catch (err) {
      setError(err.message || "Failed to add transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Add a Transaction</h2>
      <p className="mt-2 text-sm text-slate-500">Add one debt record at a time for the selected group.</p>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 md:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Who Paid</span>
            <input
              value={fromUser}
              onChange={(e) => setFromUser(e.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              placeholder="Alice"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Who Owes</span>
            <input
              value={toUser}
              onChange={(e) => setToUser(e.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              placeholder="Bob"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Amount</span>
            <input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              type="number"
              min="0"
              step="0.01"
              className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              placeholder="100.00"
            />
          </label>
        </div>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isSubmitting ? "Adding..." : "Add Transaction"}
        </button>
      </form>
    </section>
  );
}
