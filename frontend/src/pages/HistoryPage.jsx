import { useState, useEffect } from 'react'
import './pages.css'

import { API_URL as API, UPLOADS_URL } from '../config';

const TYPE_ICONS = { design: '✦', upload: '📷', recommendation: '👗' }
const TYPE_LABELS = { design: 'Generated Design', upload: 'Photo Analysis', recommendation: 'Outfit Recommendation' }

function formatDate(iso) {
    if (!iso) return ''
    try {
        return new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    } catch { return iso }
}

export default function HistoryPage() {
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [filter, setFilter] = useState('all')

    useEffect(() => {
        fetch(`${API}/history`)
            .then(r => r.json())
            .then(data => { setHistory(data.items || []); setLoading(false) })
            .catch(e => { setError('Could not load history. Ensure backend is running.'); setLoading(false) })
    }, [])

    const filtered = filter === 'all' ? history : history.filter(h => h.type === filter)

    return (
        <div className="page">
            <div className="container">
                <div className="text-center" style={{ marginBottom: 16 }}>
                    <h1 className="section-title">📁 Design <span className="gold-text">History</span></h1>
                    <p className="section-subtitle">All your generated designs, uploads, and recommendations</p>
                </div>

                {/* Filter Tabs */}
                <div style={{ display: 'flex', gap: 8, marginBottom: 32, flexWrap: 'wrap' }}>
                    {['all', 'design', 'upload', 'recommendation'].map(f => (
                        <button key={f} className={`style-tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                            {f === 'all' ? 'All' : TYPE_LABELS[f]}
                        </button>
                    ))}
                </div>

                {loading && (
                    <div className="loading-state">
                        <div className="spinner pulse-glow" />
                        <p>Loading your history…</p>
                    </div>
                )}

                {error && (
                    <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 12, padding: '16px 20px', color: '#f87171' }}>
                        ⚠ {error}
                    </div>
                )}

                {!loading && !error && filtered.length === 0 && (
                    <div className="image-placeholder" style={{ padding: '80px 20px', textAlign: 'center', border: '1px dashed var(--border)', borderRadius: 24 }}>
                        <span style={{ fontSize: '3rem', opacity: 0.3 }}>📭</span>
                        <p style={{ color: 'var(--muted)', marginTop: 16 }}>No history yet. Start by generating a design or uploading a photo!</p>
                    </div>
                )}

                <div className="history-grid">
                    {filtered.map((item, i) => (
                        <div key={item.id} className="history-card fade-up" style={{ animationDelay: `${i * 0.05}s` }}>
                            {item.image_url ? (
                                <img className="history-card-img" src={item.image_url} alt={item.summary} loading="lazy" />
                            ) : (
                                <div className="history-card-img-placeholder">{TYPE_ICONS[item.type]}</div>
                            )}
                            <div className="history-card-body">
                                <div className="history-card-type">{TYPE_ICONS[item.type]} {TYPE_LABELS[item.type]}</div>
                                <div className="history-card-summary">{item.summary}</div>
                                <div className="history-card-date">{formatDate(item.created_at)}</div>
                            </div>
                        </div>
                    ))}
                </div>

                {!loading && filtered.length > 0 && (
                    <p style={{ textAlign: 'center', color: 'var(--muted)', marginTop: 40, fontSize: '0.85rem' }}>
                        Showing {filtered.length} item{filtered.length !== 1 ? 's' : ''}
                    </p>
                )}
            </div>
        </div>
    )
}
