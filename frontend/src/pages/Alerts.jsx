import { useState, useCallback } from 'react'
import {
  FiBell, FiShield, FiPlus, FiTrash2, FiEdit2,
  FiCheck, FiCheckSquare, FiFilter, FiRefreshCw,
} from 'react-icons/fi'
import { toast } from 'react-toastify'
import Modal from '../components/Modal'
import SeverityBadge from '../components/SeverityBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import { useAlertRules, useAlertEvents } from '../hooks/useAlerts'

// ── Constants ─────────────────────────────────────────────────────────────────

const RULE_TYPES = [
  { value: 'severity',       label: 'Severity' },
  { value: 'keyword',        label: 'Keyword' },
  { value: 'malware_family', label: 'Malware Family' },
  { value: 'country',        label: 'Country' },
  { value: 'ioc_type',       label: 'IOC Type' },
  { value: 'industry',       label: 'Industry' },
]

const SEVERITY_OPTIONS = ['critical', 'high', 'medium', 'low']
const IOC_TYPE_OPTIONS  = ['IP', 'Domain', 'URL', 'Hash', 'Email']

const EMPTY_FORM = {
  name: '',
  rule_type: 'severity',
  rule_value: '',
  notify_dashboard: true,
  notify_email: false,
  email: '',
  is_active: true,
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function relativeTime(value) {
  if (!value) return '—'
  const diffMs = Date.now() - new Date(value).getTime()
  const minutes = Math.round(diffMs / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.round(hours / 24)}d ago`
}

function RuleValueInput({ ruleType, value, onChange }) {
  if (ruleType === 'severity') {
    return (
      <select
        id="rule-value"
        className="form-select form-select-sm bg-dark text-light border-secondary"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
      >
        <option value="">Select severity…</option>
        {SEVERITY_OPTIONS.map((s) => (
          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
        ))}
      </select>
    )
  }
  if (ruleType === 'ioc_type') {
    return (
      <select
        id="rule-value"
        className="form-select form-select-sm bg-dark text-light border-secondary"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
      >
        <option value="">Select IOC type…</option>
        {IOC_TYPE_OPTIONS.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
    )
  }
  return (
    <input
      id="rule-value"
      type="text"
      className="form-control form-control-sm bg-dark text-light border-secondary"
      placeholder={
        ruleType === 'keyword'        ? 'e.g. mirai' :
        ruleType === 'malware_family' ? 'e.g. Emotet' :
        ruleType === 'country'        ? 'e.g. Russia' :
        ruleType === 'industry'       ? 'e.g. finance' : 'Value…'
      }
      value={value}
      onChange={(e) => onChange(e.target.value)}
      required
    />
  )
}

// ── Rule Form Modal ───────────────────────────────────────────────────────────

function RuleFormModal({ isOpen, onClose, onSave, initial }) {
  const [form, setForm] = useState(initial || EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  // sync when `initial` changes (edit vs create)
  useState(() => { setForm(initial || EMPTY_FORM) })

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  const handleSubmit = (e) => {
    e.preventDefault()
    setSaving(true)
    onSave(form)
      .then(() => { onClose(); setForm(EMPTY_FORM) })
      .catch((err) => toast.error(err.message || 'Failed to save rule'))
      .finally(() => setSaving(false))
  }

  return (
    <Modal title={initial ? 'Edit Alert Rule' : 'Create Alert Rule'} isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
        {/* Name */}
        <div>
          <label htmlFor="rule-name" className="form-label form-label-sm text-secondary mb-1">Rule Name</label>
          <input
            id="rule-name"
            type="text"
            className="form-control form-control-sm bg-dark text-light border-secondary"
            placeholder="e.g. High-severity alert"
            value={form.name}
            onChange={(e) => set('name', e.target.value)}
            required
          />
        </div>

        {/* Type + Value */}
        <div className="row g-2">
          <div className="col-5">
            <label htmlFor="rule-type" className="form-label form-label-sm text-secondary mb-1">Type</label>
            <select
              id="rule-type"
              className="form-select form-select-sm bg-dark text-light border-secondary"
              value={form.rule_type}
              onChange={(e) => set('rule_type', e.target.value)}
            >
              {RULE_TYPES.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div className="col-7">
            <label htmlFor="rule-value" className="form-label form-label-sm text-secondary mb-1">Match Value</label>
            <RuleValueInput
              ruleType={form.rule_type}
              value={form.rule_value}
              onChange={(v) => set('rule_value', v)}
            />
          </div>
        </div>

        {/* Notifications */}
        <div>
          <p className="form-label form-label-sm text-secondary mb-2">Notifications</p>
          <div className="d-flex flex-column gap-2">
            <div className="form-check form-switch mb-0">
              <input
                id="notify-dashboard"
                type="checkbox"
                className="form-check-input"
                checked={form.notify_dashboard}
                onChange={(e) => set('notify_dashboard', e.target.checked)}
              />
              <label htmlFor="notify-dashboard" className="form-check-label small">Dashboard notifications</label>
            </div>
            <div className="form-check form-switch mb-0">
              <input
                id="notify-email"
                type="checkbox"
                className="form-check-input"
                checked={form.notify_email}
                onChange={(e) => set('notify_email', e.target.checked)}
              />
              <label htmlFor="notify-email" className="form-check-label small">Email notifications</label>
            </div>
            {form.notify_email && (
              <input
                type="email"
                className="form-control form-control-sm bg-dark text-light border-secondary"
                placeholder="alert@yourdomain.com"
                value={form.email}
                onChange={(e) => set('email', e.target.value)}
              />
            )}
          </div>
        </div>

        {/* Active toggle */}
        <div className="form-check form-switch mb-0">
          <input
            id="is-active"
            type="checkbox"
            className="form-check-input"
            checked={form.is_active}
            onChange={(e) => set('is_active', e.target.checked)}
          />
          <label htmlFor="is-active" className="form-check-label small">Rule active</label>
        </div>

        <div className="d-flex gap-2 justify-content-end pt-1">
          <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-sm btn-primary" disabled={saving}>
            {saving ? <span className="spinner-border spinner-border-sm me-1" /> : null}
            {initial ? 'Save changes' : 'Create rule'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Rules Tab ─────────────────────────────────────────────────────────────────

function RulesTab() {
  const { rules, loading, error, refetch, add, edit, remove } = useAlertRules()
  const [modalOpen, setModalOpen]   = useState(false)
  const [editTarget, setEditTarget] = useState(null)

  const openCreate = () => { setEditTarget(null); setModalOpen(true) }
  const openEdit   = (rule) => { setEditTarget(rule); setModalOpen(true) }
  const closeModal = () => setModalOpen(false)

  const handleSave = useCallback(
    (form) => {
      const op = editTarget ? edit(editTarget.id, form) : add(form)
      return op.then(() => toast.success(editTarget ? 'Rule updated' : 'Rule created'))
    },
    [editTarget, add, edit]
  )

  const handleDelete = (rule) => {
    if (!window.confirm(`Delete rule "${rule.name}"?`)) return
    remove(rule.id)
      .then(() => toast.success('Rule deleted'))
      .catch((err) => toast.error(err.message || 'Failed to delete'))
  }

  if (loading) return <LoadingSpinner label="Loading rules…" />
  if (error)   return <ErrorState message={error.message} onRetry={refetch} />

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <p className="text-secondary small mb-0">{rules.length} rule{rules.length !== 1 ? 's' : ''} configured</p>
        <button className="btn btn-sm btn-primary d-flex align-items-center gap-1" onClick={openCreate}>
          <FiPlus size={14} /> New Rule
        </button>
      </div>

      {rules.length === 0 ? (
        <EmptyState message="No alert rules yet. Create one to start monitoring for threats." />
      ) : (
        <div className="alert-rules-list">
          {rules.map((rule) => (
            <div key={rule.id} className={`alert-rule-card ${!rule.is_active ? 'alert-rule-card--inactive' : ''}`}>
              <div className="alert-rule-card__left">
                <div className="d-flex align-items-center gap-2 mb-1">
                  <span className="alert-rule-card__name">{rule.name}</span>
                  {!rule.is_active && (
                    <span className="badge text-bg-secondary" style={{ fontSize: '0.65rem' }}>Inactive</span>
                  )}
                </div>
                <div className="d-flex align-items-center gap-2 flex-wrap">
                  <span className="alert-rule-card__chip alert-rule-card__chip--type">{rule.rule_type}</span>
                  <span className="alert-rule-card__chip alert-rule-card__chip--value">{rule.rule_value}</span>
                  {rule.notify_email && (
                    <span className="alert-rule-card__chip alert-rule-card__chip--email">📧 email</span>
                  )}
                </div>
              </div>
              <div className="alert-rule-card__actions">
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => openEdit(rule)}
                  title="Edit rule"
                >
                  <FiEdit2 size={13} />
                </button>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => handleDelete(rule)}
                  title="Delete rule"
                >
                  <FiTrash2 size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <RuleFormModal
        isOpen={modalOpen}
        onClose={closeModal}
        onSave={handleSave}
        initial={editTarget}
        key={editTarget?.id ?? 'new'}
      />
    </>
  )
}

// ── Events Tab ────────────────────────────────────────────────────────────────

function EventsTab() {
  const [page, setPage]           = useState(1)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const { data, loading, error, refetch, markRead, markAll } = useAlertEvents({ page, perPage: 20, unreadOnly })

  const handleMarkAll = () =>
    markAll().then(() => toast.success('All events marked as read')).catch((err) => toast.error(err.message))

  if (loading) return <LoadingSpinner label="Loading events…" />
  if (error)   return <ErrorState message={error.message} onRetry={refetch} />

  const items      = data?.items ?? []
  const totalPages = data?.total_pages ?? 1

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div className="d-flex align-items-center gap-2">
          <button
            className={`btn btn-sm ${unreadOnly ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => { setUnreadOnly((v) => !v); setPage(1) }}
          >
            <FiFilter size={13} className="me-1" />
            Unread only
          </button>
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-sm btn-outline-secondary" onClick={refetch} title="Refresh">
            <FiRefreshCw size={13} />
          </button>
          {items.length > 0 && (
            <button className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1" onClick={handleMarkAll}>
              <FiCheckSquare size={13} /> Mark all read
            </button>
          )}
        </div>
      </div>

      {items.length === 0 ? (
        <EmptyState message={unreadOnly ? 'No unread alerts.' : 'No alert events yet.'} />
      ) : (
        <div className="alert-events-list">
          {items.map((event) => (
            <div
              key={event.id}
              className={`alert-event-card alert-event-card--${event.severity} ${event.is_read ? 'alert-event-card--read' : ''}`}
            >
              <div className="alert-event-card__body">
                <div className="d-flex align-items-start gap-2 mb-1">
                  <p className="alert-event-card__title mb-0">{event.title}</p>
                  <SeverityBadge severity={event.severity} />
                </div>
                <p className="alert-event-card__message">{event.message}</p>
                <span className="alert-event-card__time">{relativeTime(event.created_at)}</span>
              </div>
              {!event.is_read && (
                <button
                  className="btn btn-sm btn-outline-secondary alert-event-card__read-btn"
                  onClick={() => markRead(event.id)}
                  title="Mark as read"
                >
                  <FiCheck size={13} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-3">
          <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      )}
    </>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'rules',  label: 'Alert Rules',  icon: FiShield },
  { id: 'events', label: 'Event Inbox',  icon: FiBell },
]

function Alerts() {
  const [activeTab, setActiveTab] = useState('rules')

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Alerts</h1>
          <p className="page__subtitle">Configure detection rules and review triggered alert events</p>
        </div>
      </div>

      {/* Tab bar */}
      <div className="alerts-tabs mb-4">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`alerts-tabs__tab ${activeTab === id ? 'alerts-tabs__tab--active' : ''}`}
            onClick={() => setActiveTab(id)}
          >
            <Icon size={15} />
            {label}
          </button>
        ))}
      </div>

      <div className="panel">
        {activeTab === 'rules'  && <RulesTab />}
        {activeTab === 'events' && <EventsTab />}
      </div>
    </div>
  )
}

export default Alerts
