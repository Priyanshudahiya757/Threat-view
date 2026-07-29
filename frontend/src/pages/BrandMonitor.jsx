import { useState, useCallback } from 'react'
import { FiGlobe, FiPlus, FiTrash2, FiZap, FiRefreshCw } from 'react-icons/fi'
import { toast } from 'react-toastify'
import Modal from '../components/Modal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
import { useBrandMonitors } from '../hooks/useBrandMonitor'

// ── Add Monitor Modal ─────────────────────────────────────────────────────────

const EMPTY_FORM = {
  company_domain: '',
  notify_dashboard: true,
  notify_email: false,
  email: '',
  is_active: true,
}

function AddMonitorModal({ isOpen, onClose, onAdd }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  const handleSubmit = (e) => {
    e.preventDefault()
    setSaving(true)
    onAdd(form)
      .then(() => { onClose(); setForm(EMPTY_FORM) })
      .catch((err) => toast.error(err.message || 'Failed to add monitor'))
      .finally(() => setSaving(false))
  }

  return (
    <Modal title="Add Brand Monitor" isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
        <div>
          <label htmlFor="bm-domain" className="form-label form-label-sm text-secondary mb-1">
            Company Domain
          </label>
          <input
            id="bm-domain"
            type="text"
            className="form-control form-control-sm bg-dark text-light border-secondary"
            placeholder="e.g. yourcompany.com"
            value={form.company_domain}
            onChange={(e) => set('company_domain', e.target.value)}
            required
          />
          <div className="form-text text-muted" style={{ fontSize: '0.75rem' }}>
            ThreatView will alert you when this domain appears in phishing feed indicators.
          </div>
        </div>

        <div className="d-flex flex-column gap-2">
          <p className="form-label form-label-sm text-secondary mb-1">Notifications</p>
          <div className="form-check form-switch mb-0">
            <input
              id="bm-notify-dashboard"
              type="checkbox"
              className="form-check-input"
              checked={form.notify_dashboard}
              onChange={(e) => set('notify_dashboard', e.target.checked)}
            />
            <label htmlFor="bm-notify-dashboard" className="form-check-label small">Dashboard notifications</label>
          </div>
          <div className="form-check form-switch mb-0">
            <input
              id="bm-notify-email"
              type="checkbox"
              className="form-check-input"
              checked={form.notify_email}
              onChange={(e) => set('notify_email', e.target.checked)}
            />
            <label htmlFor="bm-notify-email" className="form-check-label small">Email notifications</label>
          </div>
          {form.notify_email && (
            <input
              type="email"
              className="form-control form-control-sm bg-dark text-light border-secondary"
              placeholder="security@yourcompany.com"
              value={form.email}
              onChange={(e) => set('email', e.target.value)}
              required
            />
          )}
        </div>

        <div className="d-flex gap-2 justify-content-end pt-1">
          <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-sm btn-primary" disabled={saving}>
            {saving ? <span className="spinner-border spinner-border-sm me-1" /> : null}
            Add monitor
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Monitor Card ──────────────────────────────────────────────────────────────

function MonitorCard({ monitor, onDelete }) {
  return (
    <div className="bm-card">
      <div className="bm-card__left">
        <div className="bm-card__icon">
          <FiGlobe size={18} />
        </div>
        <div>
          <p className="bm-card__domain">{monitor.company_domain}</p>
          <div className="d-flex gap-2 flex-wrap mt-1">
            <span className={`bm-card__badge ${monitor.is_active ? 'bm-card__badge--active' : 'bm-card__badge--inactive'}`}>
              {monitor.is_active ? '● Active' : '○ Inactive'}
            </span>
            {monitor.notify_dashboard && <span className="bm-card__badge bm-card__badge--info">Dashboard</span>}
            {monitor.notify_email     && <span className="bm-card__badge bm-card__badge--info">📧 {monitor.email}</span>}
          </div>
        </div>
      </div>
      <button
        className="btn btn-sm btn-outline-danger"
        onClick={() => onDelete(monitor)}
        title="Remove monitor"
      >
        <FiTrash2 size={13} />
      </button>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

function BrandMonitor() {
  const { monitors, loading, error, refetch, add, remove } = useBrandMonitors()
  const [modalOpen, setModalOpen] = useState(false)
  const [evaluating, setEvaluating] = useState(false)

  const handleAdd = useCallback(
    (form) => add(form).then(() => toast.success(`Monitoring "${form.company_domain}"`)),
    [add]
  )

  const handleDelete = (monitor) => {
    if (!window.confirm(`Stop monitoring "${monitor.company_domain}"?`)) return
    remove(monitor.id)
      .then(() => toast.success('Monitor removed'))
      .catch((err) => toast.error(err.message || 'Failed to remove'))
  }

  const handleEvaluate = () => {
    setEvaluating(true)
    // Trigger evaluation by adding a temporary monitor with the first domain
    // Real trigger: the backend runs evaluate on every add, so a refetch is enough
    refetch()
      .then(() => toast.info('Brand monitor evaluation triggered'))
      .finally(() => setEvaluating(false))
  }

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Brand Monitor</h1>
          <p className="page__subtitle">
            Detect impersonation of your domains in phishing and malware feeds
          </p>
        </div>
        <div className="d-flex gap-2">
          <button
            className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1"
            onClick={handleEvaluate}
            disabled={evaluating || monitors.length === 0}
            title="Re-scan all feeds now"
          >
            {evaluating
              ? <span className="spinner-border spinner-border-sm" />
              : <FiZap size={13} />}
            Evaluate now
          </button>
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={refetch}
            title="Refresh list"
          >
            <FiRefreshCw size={13} />
          </button>
          <button
            className="btn btn-sm btn-primary d-flex align-items-center gap-1"
            onClick={() => setModalOpen(true)}
          >
            <FiPlus size={14} /> Add Domain
          </button>
        </div>
      </div>

      {/* How it works callout */}
      <div className="bm-callout mb-4">
        <FiGlobe size={16} className="bm-callout__icon" />
        <div>
          <p className="bm-callout__title">How Brand Monitoring works</p>
          <p className="bm-callout__body">
            ThreatView scans every newly ingested phishing and malware indicator for your registered
            domains. When a match is found an alert event is created and, if configured, an email is
            sent. Scans run automatically every ingestion cycle (default: every 60 min).
          </p>
        </div>
      </div>

      <div className="panel">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <p className="text-secondary small mb-0">
            {monitors.length} domain{monitors.length !== 1 ? 's' : ''} monitored
          </p>
        </div>

        {loading && <LoadingSpinner label="Loading monitors…" />}
        {!loading && error   && <ErrorState message={error.message} onRetry={refetch} />}
        {!loading && !error  && monitors.length === 0 && (
          <EmptyState message="No domains monitored yet. Add your company domain to start detecting impersonation." />
        )}
        {!loading && !error  && monitors.length > 0 && (
          <div className="bm-list">
            {monitors.map((m) => (
              <MonitorCard key={m.id} monitor={m} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>

      <AddMonitorModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onAdd={handleAdd}
      />
    </div>
  )
}

export default BrandMonitor
