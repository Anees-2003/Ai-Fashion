import { useState, useRef, useEffect } from 'react'
import './pages.css'

import { API_URL as API, UPLOADS_URL } from '../config';
const OCCASIONS = ['casual', 'formal', 'wedding', 'party', 'festive', 'sport']
const GENDERS = ['neutral', 'female', 'male']
const STYLE_TABS = ['Casual', 'Formal', 'Festive']

/* ─── Preview Image with retry support ───────────────────
   Images are generated locally — load instantly.
   Retry logic kept in case of any transient server error.
──────────────────────────────────────────────────────── */
function PreviewImage({ src }) {
    const [failed, setFailed] = useState(false)
    const [retryKey, setRetryKey] = useState(0)
    const [retries, setRetries] = useState(0)

    const MAX_RETRIES = 3

    // Reset when src changes
    useEffect(() => {
        setFailed(false); setRetryKey(0); setRetries(0)
    }, [src])

    const handleError = () => {
        if (retries < MAX_RETRIES) {
            const next = retries + 1
            setRetries(next)
            // Brief delay then remount the img element
            setTimeout(() => setRetryKey(k => k + 1), 2000)
        } else {
            setFailed(true)
        }
    }

    if (!src) return null

    return (
        <div className="preview-image-wrap" style={{ minHeight: 250, position: 'relative' }}>
            {failed ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: '48px 24px', textAlign: 'center' }}>
                    <div style={{ fontSize: '3rem' }}>🖼️</div>
                    <p style={{ color: 'var(--text-2)', fontSize: '0.9rem' }}>
                        Preview failed to load.<br />
                        <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Try getting recommendations again.</span>
                    </p>
                    <button className="btn btn-secondary" style={{ fontSize: '0.85rem' }}
                        onClick={() => { setFailed(false); setRetries(0); setRetryKey(k => k + 1) }}>
                        ↺ Try Again
                    </button>
                </div>
            ) : (
                <img
                    key={retryKey}
                    src={src}
                    alt="AI Outfit Preview"
                    style={{
                        width: '100%',
                        display: 'block',
                        position: 'relative',
                        zIndex: 2,
                        animation: 'fadeIn 0.6s ease',
                    }}
                    onError={handleError}
                />
            )}
        </div>
    )
}

export default function UploadPage() {
    const fileRef = useRef()
    const [preview, setPreview] = useState(null)
    const [file, setFile] = useState(null)
    const [dragOver, setDragOver] = useState(false)
    const [uploading, setUploading] = useState(false)
    const placeholderImg = uploadResult ? `${UPLOADS_URL}/${uploadResult.filename}` : '/images/placeholder.svg'(null)
    const [occasion, setOccasion] = useState('casual')
    const [gender, setGender] = useState('neutral')
    const [recLoading, setRecLoading] = useState(false)
    const [recResult, setRecResult] = useState(null)
    const [activeTab, setActiveTab] = useState('Casual')
    const [error, setError] = useState('')

    const handleFile = f => {
        if (!f || !f.type.startsWith('image/')) return
        setFile(f); setPreview(URL.createObjectURL(f))
        setUploadResult(null); setRecResult(null); setError('')
    }

    const uploadPhoto = async () => {
        if (!file) return
        setUploading(true); setError(''); setRecResult(null)
        try {
            const form = new FormData()
            form.append('file', file)
            const res = await fetch(`${API}/upload`, { method: 'POST', body: form })
            if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
            setUploadResult(await res.json())
        } catch (e) { setError(e.message) }
        finally { setUploading(false) }
    }

    const getRecommendations = async () => {
        if (!uploadResult) return
        setRecLoading(true); setError('')
        try {
            const res = await fetch(`${API}/recommend?upload_id=${uploadResult.upload_id}&occasion=${occasion}&gender=${gender}`)
            if (!res.ok) throw new Error(`Rec failed: ${res.status}`)
            setRecResult(await res.json())
        } catch (e) { setError(e.message) }
        finally { setRecLoading(false) }
    }

    // Relative path — Vite proxy forwards /uploads/ to FastAPI at localhost:8000
    const previewSrc = recResult?.generated_preview_url || null

    const styleRecs = recResult ? { Casual: recResult.casual_recommendation, Formal: recResult.formal_recommendation, Festive: recResult.festive_recommendation } : {}

    return (
        <div className="page">
            <div className="container">
                <div className="text-center" style={{ marginBottom: 40 }}>
                    <p className="section-eyebrow">AI Photo Stylist</p>
                    <h1 className="section-title">
                        Your Perfect Outfit,<br /><em className="gold-text">AI Recommended</em>
                    </h1>
                    <p className="section-subtitle" style={{ marginTop: 12 }}>
                        Upload your photo — AI analyses your body type, skin tone, and crafts outfit recommendations just for you.
                    </p>
                </div>

                <div className="upload-layout">
                    {/* ─── LEFT: Upload + Controls ─── */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                        {/* Drop zone */}
                        <div className={`upload-zone ${dragOver ? 'drag-over' : ''} ${preview ? 'has-preview' : ''}`}
                            onClick={() => fileRef.current.click()}
                            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}>
                            <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }}
                                onChange={e => handleFile(e.target.files[0])} />
                            {preview ? (
                                <img src={preview} alt="Uploaded" className="upload-preview" />
                            ) : (
                                <>
                                    <span className="upload-icon">📷</span>
                                    <p style={{ fontWeight: 600, marginBottom: 4 }}>Drop your photo here</p>
                                    <p style={{ color: 'var(--text-2)', fontSize: '0.85rem' }}>or click to browse · JPG, PNG, WEBP</p>
                                </>
                            )}
                        </div>

                        {/* Occasion + Gender selectors */}
                        <div style={{ display: 'flex', gap: 12 }}>
                            {[['Occasion', 'occasion', OCCASIONS, occasion, setOccasion],
                            ['Gender', 'gender', GENDERS, gender, setGender]].map(([label, key, opts, val, setter]) => (
                                <div key={key} style={{ flex: 1 }}>
                                    <label className="auth-label">{label}</label>
                                    <select className="input-field" value={val} onChange={e => setter(e.target.value)}>
                                        {opts.map(o => <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
                                    </select>
                                </div>
                            ))}
                        </div>

                        <button className="btn btn-primary w-full" onClick={uploadPhoto} disabled={!file || uploading}>
                            {uploading ? '⏳ Analysing…' : '🔍 Analyse My Photo'}
                        </button>

                        {uploadResult && (
                            <button className="btn btn-secondary w-full" onClick={getRecommendations} disabled={recLoading}>
                                {recLoading ? '⏳ Generating Recommendations…' : '✦ Get Outfit Recommendations'}
                            </button>
                        )}

                        {error && <div className="error-box">⚠ {error}</div>}

                        {/* Analysis Card */}
                        {uploadResult && (
                            <div className="card card-gold fade-up">
                                <p className="section-eyebrow" style={{ marginBottom: 16 }}>Analysis Results</p>
                                <div className="skin-tone-display">
                                    <div className="skin-swatch" style={{ background: uploadResult.skin_tone_hex }} />
                                    <div>
                                        <div style={{ fontWeight: 600 }}>{uploadResult.skin_tone}</div>
                                        <div style={{ color: 'var(--muted)', fontSize: '0.78rem' }}>Skin Tone</div>
                                    </div>
                                </div>
                                <div style={{ marginBottom: 12 }}>
                                    <span className="badge badge-blue">{uploadResult.body_type}</span>
                                </div>
                                <p style={{ fontSize: '0.88rem', color: 'var(--text-2)', lineHeight: 1.7, marginBottom: 14 }}>
                                    {uploadResult.analysis_result}
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                                    Recommended Colors
                                </p>
                                <div className="color-row">
                                    {uploadResult.recommended_colors?.map((c, i) => (
                                        <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                                            <div style={{ width: 28, height: 28, borderRadius: '50%', background: `hsl(${i * 42 + 20},52%,52%)`, border: '2px solid var(--border)' }} />
                                            <span style={{ fontSize: '0.62rem', color: 'var(--muted)', textAlign: 'center', maxWidth: 56 }}>{c}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ─── RIGHT: Recommendations ─── */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {recLoading && (
                            <div className="loading-state">
                                <div className="spinner" />
                                <p>Generating your personalized recommendations…</p>
                                <p style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>AI is also creating an outfit preview for you</p>
                            </div>
                        )}

                        {recResult && (
                            <>
                                {/* AI Preview Image */}
                                <div>
                                    <p style={{ fontWeight: 600, marginBottom: 12, fontSize: '0.9rem', color: 'var(--text-2)' }}>
                                        🎨 AI Generated Outfit Preview
                                    </p>
                                    <PreviewImage src={previewSrc} />
                                </div>

                                {/* Color Palette */}
                                <div className="card">
                                    <p style={{ fontWeight: 600, marginBottom: 14, fontSize: '0.9rem' }}>🎨 Your Color Palette</p>
                                    <div className="color-row">
                                        {recResult.color_palette?.map((c, i) => (
                                            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                                                <div style={{ width: 38, height: 38, borderRadius: '50%', background: `hsl(${i * 55 + 10},58%,${48 + i * 4}%)`, border: '2px solid var(--border-gold)' }} />
                                                <span style={{ fontSize: '0.65rem', color: 'var(--muted)', textAlign: 'center', maxWidth: 60 }}>{c}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Suggested Outfits */}
                                <div>
                                    <p style={{ fontWeight: 600, marginBottom: 14, fontSize: '0.9rem', color: 'var(--text-2)' }}>👗 Suggested Outfits</p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                        {recResult.suggested_outfits?.map((o, i) => (
                                            <div key={i} className="rec-outfit-card">
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                                                    <span style={{ fontWeight: 600, fontSize: '0.92rem' }}>#{o.rank} {o.outfit}</span>
                                                    <span className="badge badge-gold" style={{ fontSize: '0.68rem', flexShrink: 0 }}>{o.color}</span>
                                                </div>
                                                <p style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: 6 }}>{o.reason}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Virtual Styling Guide */}
                                <div className="card">
                                    <p style={{ fontWeight: 600, marginBottom: 14, fontSize: '0.9rem' }}>✦ Virtual Styling Guide</p>
                                    <div className="style-tabs">
                                        {STYLE_TABS.map(t => (
                                            <button key={t} className={`style-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>{t}</button>
                                        ))}
                                    </div>
                                    <div className="style-rec-text">{styleRecs[activeTab]}</div>
                                </div>
                            </>
                        )}

                        {!recResult && !recLoading && (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 20px', border: '1px dashed var(--border)', borderRadius: 24, textAlign: 'center', gap: 12 }}>
                                <div style={{ fontSize: '3rem', opacity: 0.2 }}>👗</div>
                                <p style={{ color: 'var(--muted)' }}>Your AI outfit recommendations will appear here</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
