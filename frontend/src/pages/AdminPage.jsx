import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './pages.css'

import { API_URL as API } from '../config';

function StatCard({ icon, label, value, color }) {
    return (
        <div className="card" style={{ textAlign: 'center', padding: '28px 20px' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: 12 }}>{icon}</div>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, fontFamily: 'Playfair Display, serif', color: color || 'var(--gold)', marginBottom: 6 }}>{value}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
        </div>
    )
}

export default function AdminPage() {
    const { user, token, logout, authFetch } = useAuth()
    const navigate = useNavigate()
    const [stats, setStats] = useState(null)
    const [users, setUsers] = useState([])
    const [activeTab, setActiveTab] = useState('overview')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!user || user.role !== 'admin') { navigate('/login'); return }
        loadData()
    }, [user])

    const loadData = async () => {
        setLoading(true)
        try {
            const [statsRes, usersRes] = await Promise.all([
                authFetch(`${API}/admin/stats`),
                authFetch(`${API}/admin/users`),
            ])
            const statsData = await statsRes.json()
            const usersData = await usersRes.json()
            setStats(statsData)
            setUsers(usersData.users || [])
        } catch { }
        setLoading(false)
    }

    const handleLogout = () => { logout(); navigate('/login') }

    const formatDate = iso => {
        if (!iso) return '—'
        try { return new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) } catch { return iso }
    }

    return (
        <div className="page">
            <div className="container">
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
                    <div>
                        <div className="badge badge-gold" style={{ marginBottom: 8 }}>🛡️ Admin Dashboard</div>
                        <h1 className="section-title">Welcome, <span className="gold-text">Admin</span></h1>
                    </div>
                    <div style={{ display: 'flex', gap: 12 }}>
                        <button className="btn-ghost" onClick={() => { navigate('/'); }}>← Back to App</button>
                        <button className="btn-secondary" onClick={handleLogout}>Logout</button>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="style-tabs" style={{ marginBottom: 32 }}>
                    {[['overview', '📊 Overview'], ['users', '👥 Users']].map(([id, label]) => (
                        <button key={id} className={`style-tab ${activeTab === id ? 'active' : ''}`} onClick={() => setActiveTab(id)}>
                            {label}
                        </button>
                    ))}
                </div>

                {loading ? (
                    <div className="loading-state"><div className="spinner pulse-glow" /><p>Loading dashboard…</p></div>
                ) : activeTab === 'overview' ? (
                    <>
                        <div className="grid-4" style={{ marginBottom: 40 }}>
                            <StatCard icon="👥" label="Registered Users" value={stats?.users ?? 0} color="var(--gold)" />
                            <StatCard icon="✦" label="Designs Generated" value={stats?.designs ?? 0} color="#60a5fa" />
                            <StatCard icon="📷" label="Photos Analyzed" value={stats?.uploads ?? 0} color="var(--rose)" />
                            <StatCard icon="👗" label="Recommendations" value={stats?.recommendations ?? 0} color="#4ade80" />
                        </div>
                        <div className="grid-2">
                            <div className="card">
                                <h3 style={{ fontFamily: 'Playfair Display, serif', marginBottom: 16, fontSize: '1.1rem' }}>🛍️ Product Catalog</h3>
                                <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--gold)', fontFamily: 'Playfair Display, serif' }}>{stats?.products}</div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: 8 }}>Fashion products in MongoDB with Budget / Mid-range / Premium tiers</p>
                            </div>
                            <div className="card">
                                <h3 style={{ fontFamily: 'Playfair Display, serif', marginBottom: 16, fontSize: '1.1rem' }}>⚡ System Status</h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                    {[['API Server', '✅ Online'], ['MongoDB', '✅ Connected'], ['AI Engine', '✅ Pollinations.ai'], ['Image Gen', '✅ flux model']].map(([k, v]) => (
                                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
                                            <span style={{ color: '#4ade80', fontWeight: 600 }}>{v}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </>
                ) : (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                            <h2 style={{ fontFamily: 'Playfair Display, serif', fontSize: '1.3rem' }}>Registered Users ({users.length})</h2>
                            <button className="btn-ghost" onClick={loadData}>↻ Refresh</button>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table className="admin-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Role</th>
                                        <th>Joined</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.length === 0 ? (
                                        <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>No users registered yet</td></tr>
                                    ) : users.map((u) => (
                                        <tr key={u.id}>
                                            <td>{u.name || '—'}</td>
                                            <td style={{ color: 'var(--text-secondary)' }}>{u.email}</td>
                                            <td><span className={`badge ${u.role === 'admin' ? 'badge-gold' : 'badge-blue'}`}>{u.role}</span></td>
                                            <td style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>{formatDate(u.created_at)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
