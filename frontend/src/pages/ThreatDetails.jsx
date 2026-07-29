import PropTypes from 'prop-types'
import { useParams, useNavigate } from 'react-router-dom'
import { FiArrowLeft, FiCopy } from 'react-icons/fi'
import { toast } from 'react-toastify'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import SeverityBadge from '../components/SeverityBadge'
import IndicatorTypeBadge from '../components/IndicatorTypeBadge'
import { useThreatDetails } from '../hooks/useThreatDetails'
import { usePreferences } from '../context/PreferencesContext'

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

function DetailField({ label, value }) {
  return (
    <div className="col-6 col-md-3">
      <div className="detail-field">
        <p className="detail-field__label">{label}</p>
        <p className="detail-field__value">{value || '—'}</p>
      </div>
    </div>
  )
}

DetailField.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
}

function ThreatDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toastsEnabled } = usePreferences()
  const { data: threat, loading, error, refetch } = useThreatDetails(id)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(threat.indicator)
      if (toastsEnabled) toast.success('Indicator copied to clipboard')
    } catch {
      if (toastsEnabled) toast.error('Could not copy to clipboard')
    }
  }

  return (
    <div className="page">
      <button type="button" className="btn btn-sm btn-outline-light mb-3" onClick={() => navigate(-1)}>
        <FiArrowLeft className="me-1" /> Back
      </button>

      {loading && <LoadingSpinner label="Loading threat details..." />}
      {/* A 404 from the backend surfaces here with its own descriptive message. */}
      {!loading && error && <ErrorState message={error.message} onRetry={refetch} />}

      {!loading && !error && threat && (
        <div className="panel threat-details">
          <div className="threat-details__header">
            <div>
              <p className="threat-details__eyebrow">Indicator of Compromise</p>
              <h1 className="threat-details__indicator">{threat.indicator}</h1>
              <div className="d-flex gap-2 mt-2">
                <SeverityBadge severity={threat.severity} />
                <IndicatorTypeBadge type={threat.indicator_type} />
              </div>
            </div>
            <button type="button" className="btn btn-outline-light" onClick={handleCopy}>
              <FiCopy className="me-1" /> Copy
            </button>
          </div>

          <div className="row g-3 mt-1">
            <DetailField label="Category" value={threat.category} />
            <DetailField label="Source" value={threat.source} />
            <DetailField label="Country" value={threat.country} />
            <DetailField label="Confidence" value={threat.confidence != null ? `${threat.confidence} / 100` : null} />
            <DetailField label="First Seen" value={formatDate(threat.first_seen)} />
            <DetailField label="Last Seen" value={formatDate(threat.last_seen)} />
            <DetailField label="Ingested" value={formatDate(threat.created_at)} />
            <DetailField label="Updated" value={formatDate(threat.updated_at)} />
          </div>

          {threat.description && (
            <div className="mt-4">
              <h3 className="threat-details__section-title">Description</h3>
              <p className="threat-details__description">{threat.description}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ThreatDetails
