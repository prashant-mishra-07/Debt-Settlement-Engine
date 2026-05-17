export default function DebtLedger({ title, transactions }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
          {transactions?.length ?? 0} items
        </span>
      </div>

      {transactions?.length > 0 ? (
        <div className="space-y-3">
          {transactions.map((item, index) => (
            <div
              key={`${item.from_user}-${item.to_user}-${index}`}
              className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
            >
              <p className="text-sm font-medium text-slate-900">
                {item.from_user} owes {item.to_user}
              </p>
              <p className="mt-1 text-sm text-slate-600">${item.amount.toFixed(2)}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
          No transactions to display.
        </div>
      )}
    </section>
  );
}
