import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import MainLayout from './layouts/MainLayout'
import LoadingSpinner from './components/LoadingSpinner'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { SidebarProvider } from './context/SidebarContext'
import { PreferencesProvider } from './context/PreferencesContext'

const Dashboard     = lazy(() => import('./pages/Dashboard'))
const ThreatFeed    = lazy(() => import('./pages/ThreatFeed'))
const ThreatDetails = lazy(() => import('./pages/ThreatDetails'))
const SearchIOC     = lazy(() => import('./pages/SearchIOC'))
const Analytics     = lazy(() => import('./pages/Analytics'))
const AIDetection   = lazy(() => import('./pages/AIDetection'))
const Alerts        = lazy(() => import('./pages/Alerts'))
const BrandMonitor  = lazy(() => import('./pages/BrandMonitor'))
const Settings      = lazy(() => import('./pages/Settings'))
const NotFound      = lazy(() => import('./pages/NotFound'))
const Login         = lazy(() => import('./pages/Login'))
const Register      = lazy(() => import('./pages/Register'))

function App() {
  return (
    <PreferencesProvider>
      <BrowserRouter>
        <AuthProvider>
          <SidebarProvider>
            <Suspense fallback={<LoadingSpinner label="Loading…" />}>
              <Routes>
                {/* ── Public routes (no shell) ── */}
                <Route path="/login"    element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* ── Protected routes (inside MainLayout) ── */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Routes>
                          <Route path="/"              element={<Navigate to="/dashboard" replace />} />
                          <Route path="/dashboard"     element={<Dashboard />} />
                          <Route path="/threats"       element={<ThreatFeed />} />
                          <Route path="/threats/:id"   element={<ThreatDetails />} />
                          <Route path="/search"        element={<SearchIOC />} />
                          <Route path="/analytics"     element={<Analytics />} />
                          <Route path="/ai-detection"  element={<AIDetection />} />
                          <Route path="/alerts"        element={<Alerts />} />
                          <Route path="/brand-monitor" element={<BrandMonitor />} />
                          <Route path="/settings"      element={<Settings />} />
                          <Route path="*"              element={<NotFound />} />
                        </Routes>
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </Suspense>
            <ToastContainer theme="dark" position="top-right" autoClose={4000} newestOnTop />
          </SidebarProvider>
        </AuthProvider>
      </BrowserRouter>
    </PreferencesProvider>
  )
}

export default App
