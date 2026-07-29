import { toast } from 'react-toastify'
import { useApiHealth } from '../hooks/useApiHealth'
import { usePreferences } from '../context/PreferencesContext'

function Settings() {
  const apiStatus = useApiHealth()
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
  const { pageSize, setPageSize, toastsEnabled, setToastsEnabled } = usePreferences()

  const handlePreviewToast = () => {
    if (toastsEnabled) {
      toast.info('This is what a ThreatView notification looks like.')
    }
  }

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Settings</h1>
          <p className="page__subtitle">Connection status and local display preferences</p>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-lg-6">
          <div className="panel">
            <h3 className="panel__title mb-3">API Connection</h3>
            <dl className="settings-meta">
              <dt>Backend URL</dt>
              <dd>
                <code>{apiUrl}</code>
              </dd>
              <dt>Status</dt>
              <dd className={`settings-status settings-status--${apiStatus}`}>{apiStatus}</dd>
            </dl>
            <p className="text-secondary small mb-0">
              Set <code>VITE_API_URL</code> in your <code>.env</code> file to point this dashboard at a different
              backend.
            </p>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="panel">
            <h3 className="panel__title mb-3">Display Preferences</h3>
            <p className="text-secondary small">Stored locally in your browser — not synced to the server.</p>

            <div className="mb-3">
              <label className="form-label" htmlFor="page-size">
                Default table page size
              </label>
              <select
                id="page-size"
                className="form-select bg-dark text-light border-secondary"
                value={pageSize}
                onChange={(e) => setPageSize(Number(e.target.value))}
              >
                {[10, 20, 50, 100].map((size) => (
                  <option key={size} value={size}>
                    {size} rows
                  </option>
                ))}
              </select>
            </div>

            <div className="form-check form-switch mb-3">
              <input
                className="form-check-input"
                type="checkbox"
                role="switch"
                id="toasts-enabled"
                checked={toastsEnabled}
                onChange={(e) => setToastsEnabled(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="toasts-enabled">
                Enable toast notifications
              </label>
            </div>

            <button type="button" className="btn btn-outline-light btn-sm" onClick={handlePreviewToast}>
              Preview notification
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
