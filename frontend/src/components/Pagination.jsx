import PropTypes from 'prop-types'

function buildPageList(current, total) {
  const delta = 1
  const range = []
  for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i += 1) {
    range.push(i)
  }
  if (range[0] > 1) {
    if (range[0] > 2) range.unshift('...')
    range.unshift(1)
  }
  if (range[range.length - 1] < total) {
    if (range[range.length - 1] < total - 1) range.push('...')
    range.push(total)
  }
  return range
}

function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null

  const pages = buildPageList(page, totalPages)

  return (
    <nav aria-label="Pagination">
      <ul className="pagination pagination-dark justify-content-center mb-0">
        <li className={`page-item ${page <= 1 ? 'disabled' : ''}`}>
          <button type="button" className="page-link" onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
            Previous
          </button>
        </li>
        {pages.map((p, idx) =>
          p === '...' ? (
            // eslint-disable-next-line react/no-array-index-key
            <li key={`ellipsis-${idx}`} className="page-item disabled">
              <span className="page-link">…</span>
            </li>
          ) : (
            <li key={p} className={`page-item ${p === page ? 'active' : ''}`}>
              <button type="button" className="page-link" onClick={() => onPageChange(p)}>
                {p}
              </button>
            </li>
          )
        )}
        <li className={`page-item ${page >= totalPages ? 'disabled' : ''}`}>
          <button
            type="button"
            className="page-link"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
          >
            Next
          </button>
        </li>
      </ul>
    </nav>
  )
}

Pagination.propTypes = {
  page: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
}

export default Pagination
