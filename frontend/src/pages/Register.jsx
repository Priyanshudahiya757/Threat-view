import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FiShield, FiMail, FiLock, FiUser, FiBriefcase, FiEye, FiEyeOff, FiAlertCircle } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

function Register() {
  const { register } = useAuth()
  const navigate     = useNavigate()

  const [form, setForm] = useState({
    email: '', password: '', company_name: '', industry: '', role: 'analyst',
  })
  const [showPw,  setShowPw]  = useState(false)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) { setError('Password must be at least 8 characters'); return }
    setError(null)
    setLoading(true)
    try {
      await register({ ...form, email: form.email.trim().toLowerCase() })
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card auth-card--wide">
        {/* Brand */}
        <div className="auth-card__brand">
          <div className="auth-card__logo">
            <FiShield size={24} />
          </div>
          <h1 className="auth-card__title">ThreatView</h1>
          <p className="auth-card__subtitle">Create your operator account</p>
        </div>

        {error && (
          <div className="auth-error" role="alert">
            <FiAlertCircle size={15} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Email */}
          <div className="auth-field">
            <label htmlFor="reg-email" className="auth-label">Email</label>
            <div className="auth-input-wrap">
              <FiMail size={15} className="auth-input-icon" />
              <input
                id="reg-email"
                type="email"
                className="auth-input"
                placeholder="you@company.com"
                value={form.email}
                onChange={(e) => set('email', e.target.value)}
                autoComplete="email"
                required
                autoFocus
              />
            </div>
          </div>

          {/* Password */}
          <div className="auth-field">
            <label htmlFor="reg-password" className="auth-label">Password <span className="auth-label-hint">(min 8 chars)</span></label>
            <div className="auth-input-wrap">
              <FiLock size={15} className="auth-input-icon" />
              <input
                id="reg-password"
                type={showPw ? 'text' : 'password'}
                className="auth-input auth-input--has-toggle"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => set('password', e.target.value)}
                autoComplete="new-password"
                required
              />
              <button
                type="button"
                className="auth-input-toggle"
                onClick={() => setShowPw((v) => !v)}
                aria-label={showPw ? 'Hide password' : 'Show password'}
              >
                {showPw ? <FiEyeOff size={15} /> : <FiEye size={15} />}
              </button>
            </div>
          </div>

          {/* Company */}
          <div className="auth-field">
            <label htmlFor="reg-company" className="auth-label">Company Name</label>
            <div className="auth-input-wrap">
              <FiBriefcase size={15} className="auth-input-icon" />
              <input
                id="reg-company"
                type="text"
                className="auth-input"
                placeholder="Acme Corp"
                value={form.company_name}
                onChange={(e) => set('company_name', e.target.value)}
                required
              />
            </div>
          </div>

          {/* Industry + Role */}
          <div className="row g-2">
            <div className="col-6">
              <div className="auth-field mb-0">
                <label htmlFor="reg-industry" className="auth-label">Industry</label>
                <input
                  id="reg-industry"
                  type="text"
                  className="auth-input"
                  placeholder="Finance, Healthcare…"
                  value={form.industry}
                  onChange={(e) => set('industry', e.target.value)}
                />
              </div>
            </div>
            <div className="col-6">
              <div className="auth-field mb-0">
                <label htmlFor="reg-role" className="auth-label">Role</label>
                <select
                  id="reg-role"
                  className="auth-input auth-select"
                  value={form.role}
                  onChange={(e) => set('role', e.target.value)}
                >
                  <option value="admin">Admin</option>
                  <option value="analyst">Analyst</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            </div>
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : null}
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-footer-text">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
