import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useNavigate, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import './App.css'

import LandingPage from './pages/LandingPage'
import DesignPage from './pages/DesignPage'
import UploadPage from './pages/UploadPage'
import HistoryPage from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import AdminPage from './pages/AdminPage'

/* ─── Protected Route ─────────────────────────── */
function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

/* ─── Navbar ──────────────────────────────────── */
function Navbar() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', fn)
    return () => window.removeEventListener('scroll', fn)
  }, [])

  const initials = user?.name?.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || '?'

  return (
    <>
      <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="nav-inner">
          <span className="nav-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            ✦ AI <span>Fashion</span>
          </span>

          <ul className="nav-links">
            <li><NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''} end>Home</NavLink></li>
            <li><NavLink to="/design" className={({ isActive }) => isActive ? 'active' : ''}>Design</NavLink></li>
            <li><NavLink to="/upload" className={({ isActive }) => isActive ? 'active' : ''}>Stylist</NavLink></li>
            <li><NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>History</NavLink></li>
            {user?.role === 'admin' && <li><NavLink to="/admin" className="nav-admin-link">🛡 Admin</NavLink></li>}
          </ul>

          <div className="nav-right">
            {user ? (
              <>
                <div className="nav-avatar" title={user.name}>{initials}</div>
                <span className="nav-username">{user.name?.split(' ')[0]}</span>
                <div className="nav-divider" />
                <button className="btn btn-ghost" style={{ padding: '7px 16px', fontSize: '0.83rem' }}
                  onClick={logout}>Log out</button>
              </>
            ) : (
              <>
                <button className="btn btn-ghost" style={{ padding: '7px 16px', fontSize: '0.83rem' }}
                  onClick={() => navigate('/login')}>Sign in</button>
                <button className="btn btn-primary" style={{ padding: '8px 20px', fontSize: '0.83rem' }}
                  onClick={() => navigate('/login?tab=register')}>Get Started</button>
              </>
            )}
          </div>

          <button className="nav-ham" onClick={() => setOpen(o => !o)} aria-label="Menu">
            <span /><span /><span />
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      <div className={`nav-mobile ${open ? 'open' : ''}`}>
        {[['/', 'Home'], ['/design', '✦ Design Generator'], ['/upload', '📷 Photo Stylist'], ['/history', '📖 History']].map(([to, label]) => (
          <NavLink key={to} to={to} onClick={() => setOpen(false)}>{label}</NavLink>
        ))}
        {user?.role === 'admin' && <NavLink to="/admin" onClick={() => setOpen(false)}>🛡 Admin Panel</NavLink>}
        <div className="divider" style={{ margin: '8px 0' }} />
        {user ? (
          <button className="btn btn-secondary w-full" onClick={() => { logout(); setOpen(false) }}>Log out</button>
        ) : (
          <button className="btn btn-primary w-full" onClick={() => { navigate('/login'); setOpen(false) }}>Sign in / Register</button>
        )}
      </div>
    </>
  )
}

/* ─── App ─────────────────────────────────────── */
export default function App() {
  return (
    <AuthProvider>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/design" element={<DesignPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin" element={
          <ProtectedRoute adminOnly>
            <AdminPage />
          </ProtectedRoute>
        } />
      </Routes>
    </AuthProvider>
  )
}
