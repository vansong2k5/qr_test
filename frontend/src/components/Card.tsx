import { ReactNode } from 'react'

const Card = ({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) => (
  <section className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 shadow-sm">
    <header className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-4 py-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{title}</h2>
      {action}
    </header>
    <div className="p-4 text-sm text-slate-700 dark:text-slate-200">{children}</div>
  </section>
)

export default Card
