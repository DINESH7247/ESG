import { Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import Layout from './components/Layout'
import StatusBadge from './components/StatusBadge'
import { fetchAuditLogs, fetchRecord, fetchRecords, updateReview, uploadData } from './api'

function UploadPage() {
  const [sourceType, setSourceType] = useState('sap')
  const [tenantName, setTenantName] = useState('Northwind Energy')
  const [uploadedBy, setUploadedBy] = useState('A. Analyst')
  const [file, setFile] = useState(null)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const onSubmit = async (event) => {
    event.preventDefault()
    if (!file) {
      setError('Choose a CSV file before uploading.')
      return
    }
    setBusy(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_type', sourceType)
    formData.append('tenant_name', tenantName)
    formData.append('uploaded_by', uploadedBy)
    try {
      setSummary(await uploadData(formData))
    } catch (uploadError) {
      setError(uploadError?.response?.data?.detail || 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
      <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 shadow-soft backdrop-blur">
        <p className="text-xs uppercase tracking-[0.35em] text-mint/70">Source ingestion</p>
        <h2 className="mt-3 font-sans text-3xl font-semibold text-white">Upload enterprise CSV exports</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
          Use the SAP, utility, or travel source type to preserve raw rows, normalize them into the unified activity model, and flag suspicious data for analyst review.
        </p>

        <form onSubmit={onSubmit} className="mt-8 grid gap-4 md:grid-cols-2">
          <label className="space-y-2 text-sm text-slate-200">
            <span className="block text-xs uppercase tracking-[0.22em] text-slate-400">Source type</span>
            <select className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 outline-none" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="sap">SAP fuel + procurement</option>
              <option value="utility">Utility electricity</option>
              <option value="travel">Corporate travel</option>
            </select>
          </label>
          <label className="space-y-2 text-sm text-slate-200">
            <span className="block text-xs uppercase tracking-[0.22em] text-slate-400">Tenant</span>
            <input className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 outline-none" value={tenantName} onChange={(e) => setTenantName(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm text-slate-200">
            <span className="block text-xs uppercase tracking-[0.22em] text-slate-400">Uploaded by</span>
            <input className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 outline-none" value={uploadedBy} onChange={(e) => setUploadedBy(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm text-slate-200 md:col-span-2">
            <span className="block text-xs uppercase tracking-[0.22em] text-slate-400">CSV file</span>
            <input type="file" accept=".csv" className="w-full rounded-2xl border border-dashed border-white/15 bg-slate-950/60 px-4 py-3 file:mr-4 file:rounded-full file:border-0 file:bg-mint file:px-4 file:py-2 file:font-semibold file:text-slate-950" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <button disabled={busy} className="rounded-2xl bg-mint px-5 py-3 font-semibold text-slate-950 transition hover:brightness-110 disabled:opacity-60 md:col-span-2">
            {busy ? 'Uploading...' : 'Upload and normalize'}
          </button>
        </form>

        {error ? <p className="mt-4 rounded-2xl border border-rose/30 bg-rose/10 p-4 text-sm text-rose">{error}</p> : null}
      </div>

      <div className="space-y-4 rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-soft backdrop-blur">
        <h3 className="font-sans text-xl font-semibold">Processing summary</h3>
        {summary ? (
          <div className="space-y-3 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">{summary.rows_received} rows received</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">{summary.processed} processed</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">{summary.failed} failed</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs leading-5 text-slate-400">
              Sample results are limited to the first 10 rows so uploads stay readable in the UI.
            </div>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-slate-900 p-4 text-xs text-slate-200">{JSON.stringify(summary, null, 2)}</pre>
          </div>
        ) : (
          <p className="text-sm leading-6 text-slate-400">Upload a CSV to see the normalization summary, including failed rows and processing counts.</p>
        )}
      </div>
    </section>
  )
}

function ReviewQueuePage() {
  const navigate = useNavigate()
  const [status, setStatus] = useState('all')
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true)
    fetchRecords(status === 'all' ? {} : { status })
      .then((items) => {
        if (active) {
          setRecords(items)
          setError('')
        }
      })
      .catch(() => active && setError('Could not load review queue.'))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [status])

  const filters = [
    ['all', 'All'],
    ['pending', 'Pending'],
    ['approved', 'Approved'],
    ['anomalies', 'Anomalies'],
    ['failed', 'Failed'],
  ]

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/6 p-6 shadow-soft backdrop-blur">
      <div className="flex flex-col gap-3 border-b border-white/10 pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-mint/70">Analyst workflow</p>
          <h2 className="mt-3 font-sans text-3xl font-semibold text-white">Review queue</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {filters.map(([value, label]) => (
            <button
              key={value}
              onClick={() => setStatus(value)}
              className={`rounded-full border px-4 py-2 text-sm transition ${status === value ? 'border-mint/40 bg-mint/10 text-white' : 'border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/10'}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      {loading ? <p className="py-10 text-sm text-slate-400">Loading records...</p> : null}
      {error ? <p className="mt-4 rounded-2xl border border-rose/30 bg-rose/10 p-4 text-sm text-rose">{error}</p> : null}
      {!loading ? (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-y-3 text-left text-sm">
            <thead className="text-xs uppercase tracking-[0.24em] text-slate-400">
              <tr>
                <th className="px-4 py-2">Activity</th>
                <th className="px-4 py-2">Source</th>
                <th className="px-4 py-2">Quantity</th>
                <th className="px-4 py-2">CO2e</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id} className="rounded-2xl border border-white/10 bg-slate-950/60">
                  <td className="px-4 py-4">
                    <div className="font-medium text-white">{record.activity_type || record.source_type}</div>
                    <div className="text-xs text-slate-400">{record.tenant_name || 'Unknown tenant'}</div>
                  </td>
                  <td className="px-4 py-4 text-slate-300">
                    <div>{record.source_filename || record.source_reference}</div>
                    <div className="text-xs text-slate-500">{record.kind === 'failed_raw' ? 'Raw failure' : record.review_status}</div>
                  </td>
                  <td className="px-4 py-4 text-slate-300">{record.normalized_quantity || '—'} {record.normalized_unit || ''}</td>
                  <td className="px-4 py-4 text-slate-300">{record.co2e_kg || '—'}</td>
                  <td className="px-4 py-4"><StatusBadge value={record.review_status || 'failed'} anomalyFlag={record.anomaly_flag} /></td>
                  <td className="px-4 py-4">
                    <button onClick={() => navigate(`/records/${record.id}`)} className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-200 transition hover:bg-white/10">
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  )
}

function RecordDetailPage() {
  const { id } = useParams()
  const [record, setRecord] = useState(null)
  const [auditLogs, setAuditLogs] = useState([])
  const [form, setForm] = useState({})
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    fetchRecord(id)
      .then((data) => {
        if (!active) return
        setRecord(data)
        setForm({
          review_status: data.review_status || 'pending',
          facility: data.facility || '',
          vendor: data.vendor || '',
          cost_center: data.cost_center || '',
          anomaly_flag: Boolean(data.anomaly_flag),
          anomaly_reason: data.anomaly_reason || '',
          changed_by: 'analyst',
        })
        if (data.kind !== 'failed_raw') {
          fetchAuditLogs(data.id).then((logs) => active && setAuditLogs(logs)).catch(() => active && setAuditLogs([]))
        }
      })
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [id])

  const save = async () => {
    if (!record || record.kind === 'failed_raw') return
    const updated = await updateReview(record.id, form)
    setRecord(updated)
    setMessage('Record updated and audit log written.')
    const logs = await fetchAuditLogs(record.id)
    setAuditLogs(logs)
  }

  if (loading) {
    return <section className="rounded-[2rem] border border-white/10 bg-white/6 p-6 text-sm text-slate-400 shadow-soft backdrop-blur">Loading record...</section>
  }

  if (!record) {
    return <section className="rounded-[2rem] border border-white/10 bg-white/6 p-6 text-sm text-rose shadow-soft backdrop-blur">Record not found.</section>
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="space-y-6 rounded-[2rem] border border-white/10 bg-white/6 p-6 shadow-soft backdrop-blur">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-mint/70">Record detail</p>
          <h2 className="mt-3 font-sans text-3xl font-semibold text-white">{record.activity_type || 'Failed row'}</h2>
          <p className="mt-2 text-sm text-slate-400">{record.source_filename || record.source_reference}</p>
        </div>

        {record.kind === 'failed_raw' ? (
          <div className="space-y-4 rounded-2xl border border-rose/30 bg-rose/10 p-4 text-sm text-rose">
            <div>{record.error_message}</div>
            <pre className="overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-200">{JSON.stringify(record.raw_json, null, 2)}</pre>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {[
              ['activity_date', 'Activity date'],
              ['scope', 'Scope'],
              ['original_quantity', 'Original quantity'],
              ['original_unit', 'Original unit'],
              ['normalized_quantity', 'Normalized quantity'],
              ['normalized_unit', 'Normalized unit'],
              ['emission_factor', 'Emission factor'],
              ['co2e_kg', 'CO2e kg'],
            ].map(([field, label]) => (
              <div key={field} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</div>
                <div className="mt-2 text-sm text-slate-100">{String(record[field] ?? '—')}</div>
              </div>
            ))}
            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Raw source JSON</div>
              <pre className="mt-3 overflow-auto text-xs text-slate-200">{JSON.stringify(record.raw_json, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-6 rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-soft backdrop-blur">
        <div>
          <h3 className="font-sans text-xl font-semibold text-white">Review action</h3>
          <p className="mt-2 text-sm text-slate-400">Edit mappings, then approve or reject the record with a single review write.</p>
        </div>
        {record.kind !== 'failed_raw' ? (
          <div className="space-y-4">
            {['review_status', 'facility', 'vendor', 'cost_center', 'anomaly_reason', 'changed_by'].map((field) => (
              <label key={field} className="block space-y-2 text-sm text-slate-200">
                <span className="block text-xs uppercase tracking-[0.22em] text-slate-400">{field.replace('_', ' ')}</span>
                {field === 'review_status' ? (
                  <select className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 outline-none" value={form[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })}>
                    <option value="pending">pending</option>
                    <option value="approved">approved</option>
                    <option value="rejected">rejected</option>
                  </select>
                ) : (
                  <input className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 outline-none" value={form[field] || ''} onChange={(e) => setForm({ ...form, [field]: e.target.value })} />
                )}
              </label>
            ))}
            <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-200">
              <input type="checkbox" checked={Boolean(form.anomaly_flag)} onChange={(e) => setForm({ ...form, anomaly_flag: e.target.checked })} />
              Flag as anomaly
            </label>
            <div className="flex gap-3">
              <button onClick={save} className="rounded-2xl bg-mint px-5 py-3 font-semibold text-slate-950 transition hover:brightness-110">
                Save review
              </button>
            </div>
            {message ? <p className="rounded-2xl border border-mint/30 bg-mint/10 p-4 text-sm text-mint">{message}</p> : null}
          </div>
        ) : (
          <div className="rounded-2xl border border-sand/30 bg-sand/10 p-4 text-sm text-sand">
            Failed raw rows cannot be approved or rejected until they are re-uploaded successfully.
          </div>
        )}

        <div>
          <h3 className="font-sans text-xl font-semibold text-white">Audit history</h3>
          <div className="mt-3 space-y-3">
            {auditLogs.length ? auditLogs.map((log) => (
              <div key={log.id} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                <div className="flex items-center justify-between gap-4">
                  <span className="font-semibold text-white">{log.action}</span>
                  <span className="text-xs uppercase tracking-[0.2em] text-slate-500">{log.changed_by}</span>
                </div>
                <div className="mt-2 text-xs text-slate-500">{log.changed_at}</div>
              </div>
            )) : <p className="text-sm text-slate-500">No audit entries yet.</p>}
          </div>
        </div>
      </div>
    </section>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/review" element={<ReviewQueuePage />} />
        <Route path="/records/:id" element={<RecordDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
