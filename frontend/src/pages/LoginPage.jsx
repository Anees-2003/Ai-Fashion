import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

import { API_URL as API } from '../config';

export default function LoginPage() {
    const { login, user } = useAuth()
    const navigate = useNavigate()
    const [params] = useSearchParams()
    const [tab, setTab] = useState(params.get('tab') === 'register' ? 'register' : 'signin')
    const [form, setForm] = useState({ name: '', email: '', password: '' })
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    // Redirect if already logged in
    useEffect(() => {
        if (user) navigate(user.role === 'admin' ? '/admin' : '/design', { replace: true })
    }, [user, navigate])

    const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

    const handleSubmit = async e => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setSuccess('')

        const endpoints = {
            signin: { url: `${API}/auth/login`, body: { email: form.email, password: form.password } },
            register: { url: `${API}/auth/register`, body: { name: form.name, email: form.email, password: form.password } },
            admin: { url: `${API}/auth/admin/login`, body: { email: form.email, password: form.password } },
        }
        const { url, body } = endpoints[tab]

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Authentication failed.')

            if (tab === 'register') {
                setSuccess('Account created! A welcome email has been sent. Signing you in…')
                await new Promise(r => setTimeout(r, 1200))
                // Auto sign-in after register
                const loginRes = await fetch(`${API}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: form.email, password: form.password }),
                })
                const loginData = await loginRes.json()
                if (loginRes.ok) login(loginData.access_token, loginData.user)
            } else {
                login(data.access_token, data.user)
            }
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-bg" />
            <div className="auth-card fade-up">
                <div className="auth-logo">✦ AI Fashion</div>
                <div className="auth-logo-sub">Your AI-Powered Style Studio</div>

                {/* Tabs */}
                <div className="auth-tabs">
                    {[['signin', 'Sign In'], ['register', 'Register'], ['admin', 'Admin']].map(([t, l]) => (
                        <button key={t} className={`auth-tab ${tab === t ? 'active' : ''}`}
                            onClick={() => { setTab(t); setError(''); setSuccess('') }}>{l}</button>
                    ))}
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    {/* Name — register only */}
                    {tab === 'register' && (
                        <div>
                            <label className="auth-label">Full Name</label>
                            <input className="input-field" type="text" placeholder="Your name"
                                value={form.name} onChange={set('name')} required />
                        </div>
                    )}

                    {/* Email */}
                    <div>
                        <label className="auth-label">Email Address</label>
                        <input className="input-field" type="email" placeholder="you@example.com"
                            value={form.email} onChange={set('email')} required />
                    </div>

                    {/* Password */}
                    <div>
                        <label className="auth-label">Password</label>
                        <div className="input-wrap">
                            <input className="input-field" type={showPw ? 'text' : 'password'}
                                placeholder={tab === 'register' ? 'Min 6 characters' : '••••••••'}
                                value={form.password} onChange={set('password')} required />
                            <button type="button" className="input-eye" onClick={() => setShowPw(v => !v)}>
                                {showPw ? '🙈' : '👁️'}
                            </button>
                        </div>
                    </div>

                    {/* Errors / Success */}
                    {error && <div className="error-box">⚠ {error}</div>}
                    {success && (
                        <div style={{ background: 'rgba(74,200,120,0.1)', border: '1px solid rgba(74,200,120,0.3)', borderRadius: 12, padding: '12px 16px', color: '#4ec878', fontSize: '0.88rem' }}>
                            ✓ {success}
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary w-full" disabled={loading}
                        style={{ marginTop: 4, fontSize: '0.95rem' }}>
                        {loading ? '⏳ Please wait…' : tab === 'signin' ? 'Sign In' : tab === 'register' ? 'Create Account' : 'Admin Login'}
                    </button>
                </form>

                {/* Hints */}
                {tab === 'signin' && (
                    <p className="auth-hint">No account? <a onClick={() => setTab('register')}>Register free</a></p>
                )}
                {tab === 'register' && (
                    <p className="auth-hint">
                        Already have an account? <a onClick={() => setTab('signin')}>Sign in</a>
                        <br />By creating an account, you'll receive a welcome email with tips to get started.
                    </p>
                )}
                {tab === 'admin' && (
                    <p className="auth-hint">Admin login is restricted to authorized users only.</p>
                )}
            </div>
        </div>
    )
}
