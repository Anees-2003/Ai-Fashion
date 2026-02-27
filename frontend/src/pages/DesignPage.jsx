import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './pages.css'

import { API_URL as API } from '../config';

const CHIPS = [
    'Royal blue silk evening gown',
    'Minimalist beige linen co-ord',
    'Ivory bridal lehenga with zardozi',
    'Black power suit with gold buttons',
    'Bohemian floral maxi dress',
    'Red velvet cocktail dress',
    'Dusty rose crop top with palazzo',
    'Traditional Banarasi silk saree',
]

function ProductCard({ p }) {
    const [imgOk, setImgOk] = useState(true)
    return (
        <a href={p.purchase_link} target="_blank" rel="noopener noreferrer" className="product-card">
            <div className="product-img-wrap">
                {imgOk ? (
                    <img src={p.image_url} alt={p.name} loading="lazy"
                        onError={() => setImgOk(false)} />
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', fontSize: '2rem', color: 'var(--muted)' }}>👗</div>
                )}
            </div>
            <div className="product-card-body">
                <div className="product-name">{p.name}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                    <span className="product-price">{p.price_range}</span>
                    <span className="badge badge-gold">{p.price_label}</span>
                </div>
                <div style={{ marginTop: 8 }}>
                    <span className="badge badge-blue" style={{ fontSize: '0.68rem' }}>{p.category}</span>
                </div>
            </div>
        </a>
    )
}

export default function DesignPage() {
    const { user, authFetch } = useAuth()
    const [params] = useSearchParams()
    const navigate = useNavigate()
    const [prompt, setPrompt] = useState(params.get('prompt') || '')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const [imgError, setImgError] = useState(false)

    // Auto-generate if prompt in URL
    useEffect(() => {
        const p = params.get('prompt')
        if (p) { setPrompt(p); generate(p) }
    }, [])

    const generate = async (overridePrompt) => {
        const p = overridePrompt ?? prompt
        if (!p.trim()) return
        setLoading(true)
        setError('')
        setResult(null)
        setImgError(false)

        try {
            const res = await fetch(`${API}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: p, user_id: user?.id || 'anonymous' }),
            })
            if (!res.ok) {
                const d = await res.json().catch(() => ({}))
                throw new Error(d.detail || `Server error ${res.status}`)
            }
            const data = await res.json()
            setResult(data)
        } catch (e) {
            setError(e.message || 'Generation failed. Check that the backend is running.')
        } finally {
            setLoading(false)
        }
    }

    // Relative path — Vite proxy forwards /uploads/ to FastAPI at localhost:8000
    const imgSrc = result?.generated_image_url || null

    return (
        <div className="page">
            <div className="container">
                {/* Header */}
                <div className="text-center" style={{ marginBottom: 40 }}>
                    <p className="section-eyebrow">AI Design Generator</p>
                    <h1 className="section-title">
                        Describe Your<br /><em className="gold-text">Dream Outfit</em>
                    </h1>
                    <p className="section-subtitle" style={{ marginTop: 12 }}>
                        Type any fashion idea and our AI will generate a stunning design for you instantly.
                    </p>
                </div>

                {/* Prompt Input */}
                <div className="design-input-wrap">
                    <textarea
                        className="input-field design-textarea"
                        placeholder="e.g. Ivory bridal lehenga with intricate gold zardozi embroidery and sheer dupatta…"
                        value={prompt}
                        onChange={e => setPrompt(e.target.value)}
                        rows={3}
                        onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), generate())}
                    />
                    <button className="btn btn-primary design-generate-btn"
                        onClick={() => generate()} disabled={loading || !prompt.trim()}>
                        {loading ? '⏳ Generating…' : '✦ Generate Design'}
                    </button>
                </div>

                {/* Chips */}
                <div className="chip-row" style={{ marginBottom: 48 }}>
                    {CHIPS.map(c => (
                        <button key={c} className="chip" onClick={() => { setPrompt(c); generate(c) }}>{c}</button>
                    ))}
                </div>

                {/* Error */}
                {error && <div className="error-box" style={{ marginBottom: 24 }}>⚠ {error}</div>}

                {/* Result */}
                {(loading || result) && (
                    <div className="design-result-grid">
                        {/* Left: image */}
                        <div>
                            <div className="generated-image-wrap">
                                {loading ? (
                                    <div style={{ padding: 16, height: '100%' }}>
                                        <div className="skeleton skeleton-img" style={{ height: '100%', aspectRatio: 'auto' }} />
                                        <p style={{ textAlign: 'center', marginTop: 16, fontSize: '0.82rem', color: 'var(--muted)' }}>
                                            🎨 AI is rendering your design… (15–30 sec)
                                        </p>
                                    </div>
                                ) : result && (
                                    <>
                                        {imgError ? (
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: 32, textAlign: 'center', minHeight: 300 }}>
                                                <div style={{ fontSize: '3rem' }}>🖼️</div>
                                                <p style={{ color: 'var(--text-2)', fontSize: '0.9rem' }}>Design generated — image failed to display.</p>
                                                <a href={imgSrc} target="_blank" rel="noopener noreferrer" className="btn btn-primary">↗ Open Full Image</a>
                                            </div>
                                        ) : (
                                            <img src={imgSrc} alt="Generated Fashion Design"
                                                style={{
                                                    width: '100%', height: '100%', objectFit: 'cover',
                                                    animation: 'fadeIn 0.7s ease',
                                                    display: 'block',
                                                }}
                                                onError={() => setImgError(true)} />
                                        )}
                                    </>
                                )}
                            </div>

                            {result && (
                                <a href={imgSrc} target="_blank" rel="noopener noreferrer"
                                    className="btn btn-secondary w-full" style={{ marginTop: 12, justifyContent: 'center' }}>
                                    ↗ Open Full Resolution
                                </a>
                            )}
                        </div>

                        {/* Right: style info + products */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                            {loading ? (
                                <div className="card" style={{ height: 200 }}>
                                    <div className="skeleton skeleton-line w-60" /><div className="skeleton skeleton-line w-80" /><div className="skeleton skeleton-line w-40" />
                                </div>
                            ) : result?.style_tags && (
                                <>
                                    <div className="card card-gold">
                                        <p style={{ fontSize: '0.75rem', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 16 }}>Style Attributes</p>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                            {[
                                                ['Category', result.style_tags.category],
                                                ['Fabric', result.style_tags.fabric],
                                                ['Occasion', result.style_tags.occasion],
                                            ].map(([k, v]) => (
                                                <div key={k}>
                                                    <span style={{ color: 'var(--muted)', fontSize: '0.78rem' }}>{k}</span>
                                                    <p style={{ color: 'var(--text)', fontWeight: 600, fontSize: '0.92rem' }}>{v}</p>
                                                </div>
                                            ))}
                                            <div>
                                                <span style={{ color: 'var(--muted)', fontSize: '0.78rem' }}>Color Palette</span>
                                                <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                                                    {result.style_tags.colors?.map((c, i) => (
                                                        <div key={i} style={{ width: 28, height: 28, borderRadius: '50%', background: c, border: '2px solid var(--border)', title: c }} />
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Suggested Products */}
                                    {result.suggested_products?.length > 0 && (
                                        <div>
                                            <p style={{ fontWeight: 600, marginBottom: 16, fontSize: '0.9rem', color: 'var(--text-2)' }}>
                                                🛍️ Shop Similar Styles
                                            </p>
                                            <div className="grid-2">
                                                {result.suggested_products.map((p, i) => <ProductCard key={i} p={p} />)}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* Empty state */}
                {!loading && !result && !error && (
                    <div className="design-empty">
                        <div style={{ fontSize: '4rem', opacity: 0.15 }}>✦</div>
                        <p style={{ color: 'var(--muted)', marginTop: 12 }}>Your AI-generated design will appear here</p>
                    </div>
                )}
            </div>
        </div>
    )
}
