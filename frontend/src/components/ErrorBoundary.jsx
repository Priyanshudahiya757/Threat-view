import { Component } from 'react'
import PropTypes from 'prop-types'
import { FiAlertTriangle, FiRefreshCw } from 'react-icons/fi'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ThreatView ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ errorInfo })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: '#0a0e1a',
          color: '#e9ecf7',
          padding: '2rem',
          textAlign: 'center',
          fontFamily: 'sans-serif'
        }}>
          <div style={{
            backgroundColor: '#131a30',
            border: '1px solid #f4415c',
            borderRadius: '12px',
            padding: '2.5rem',
            maxWidth: '600px',
            width: '100%',
            boxShadow: '0 20px 40px rgba(0,0,0,0.5)'
          }}>
            <FiAlertTriangle size={48} style={{ color: '#f4415c', marginBottom: '1rem' }} />
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.75rem' }}>
              Something went wrong
            </h2>
            <p style={{ color: '#8891b3', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button
                onClick={() => {
                  localStorage.clear()
                  window.location.href = '/login'
                }}
                style={{
                  backgroundColor: '#4c6fff',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.6rem 1.25rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <FiRefreshCw /> Reset Session & Login
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ErrorBoundary
