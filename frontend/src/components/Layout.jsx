import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Upload' },
  { to: '/review', label: 'Review Queue' },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl gap-8 px-4 py-6 lg:px-8">
        <aside className="hidden w-72 flex-col justify-between rounded-3xl border border-white/10 bg-white/5 p-6 shadow-soft backdrop-blur lg:flex">
          <div>
            <div className="mb-10">
              <p className="text-xs uppercase tracking-[0.35em] text-mint/70">Enterprise ESG</p>
              <h1 className="mt-3 font-sans text-3xl font-semibold text-white">Review Console</h1>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Ingest source files, normalize records, and sign off with a traceable audit trail.
              </p>
            </div>
            <nav className="space-y-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `block rounded-2xl border px-4 py-3 text-sm transition ${
                      isActive
                        ? 'border-mint/40 bg-mint/10 text-white'
                        : 'border-white/5 bg-white/0 text-slate-300 hover:border-white/10 hover:bg-white/5'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="rounded-2xl border border-sand/20 bg-sand/10 p-4 text-sm text-sand">
            Prototype scope: CSV uploads, normalized activity records, analyst review, and audit logs.
          </div>
        </aside>
        <main className="flex-1">
          <div className="mb-6 flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4 shadow-soft backdrop-blur lg:hidden">
            <div>
              <p className="text-[11px] uppercase tracking-[0.3em] text-mint/70">Enterprise ESG</p>
              <h1 className="font-sans text-xl font-semibold">Review Console</h1>
            </div>
            <div className="flex gap-3 text-sm">
              {navItems.map((item) => (
                <NavLink key={item.to} to={item.to} className="rounded-full border border-white/10 px-3 py-2 text-slate-200">
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>
          {children}
        </main>
      </div>
    </div>
  )
}
