import PropTypes from 'prop-types'
import LoadingSpinner from './LoadingSpinner'
import ErrorState from './ErrorState'
import EmptyState from './EmptyState'

function ChartCard({ title, subtitle, loading, error, isEmpty, headerRight, children }) {
  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div>
          <h3 className="chart-card__title">{title}</h3>
          {subtitle && <p className="chart-card__subtitle">{subtitle}</p>}
        </div>
        {headerRight && <div className="chart-card__header-right">{headerRight}</div>}
      </div>
      <div className="chart-card__body">
        {loading && <LoadingSpinner label="Loading chart..." />}
        {!loading && error && <ErrorState message={error.message} />}
        {!loading && !error && isEmpty && <EmptyState message="No data yet." />}
        {!loading && !error && !isEmpty && children}
      </div>
    </div>
  )
}

ChartCard.propTypes = {
  title:       PropTypes.string.isRequired,
  subtitle:    PropTypes.string,
  loading:     PropTypes.bool,
  error:       PropTypes.instanceOf(Error),
  isEmpty:     PropTypes.bool,
  headerRight: PropTypes.node,
  children:    PropTypes.node,
}

export default ChartCard
