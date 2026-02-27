import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './pages.css'

const HERO_IMAGES = [
    'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=1400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=1400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1400&auto=format&fit=crop&q=80',
]

const FEATURES = [
    {
        icon: '✦',
        title: 'Text to Design',
        desc: 'Describe your dream outfit and watch AI generate a stunning fashion design in seconds.',
        img: 'https://images.unsplash.com/photo-1630694093867-4b947d812bf0?w=600&auto=format&fit=crop&q=80',
        link: '/design',
    },
    {
        icon: '📷',
        title: 'Photo Stylist',
        desc: 'Upload your photo — AI analyzes your body type, skin tone, and recommends perfect outfits.',
        img: 'https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=600&auto=format&fit=crop&q=80',
        link: '/upload',
    },
    {
        icon: '🛍️',
        title: 'Shop the Look',
        desc: 'Discover affordable fashion items that match your AI-generated designs instantly.',
        img: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80',
        link: '/design',
    },
]

const PROMPTS = [
    'Red silk evening gown with floral embroidery',
    'Minimalist beige linen summer co-ord',
    'Royal blue velvet blazer with gold buttons',
    'Bohemian floral maxi dress',
    'Monochrome black power suit',
    'Ivory bridal lehenga with zari work',
]

const STATS = [
    { num: '10K+', label: 'Designs Generated' },
    { num: '5K+', label: 'Happy Users' },
    { num: '50+', label: 'Style Categories' },
    { num: '98%', label: 'Satisfaction Rate' },
]

export default function LandingPage() {
    const navigate = useNavigate()
    const [heroIdx, setHeroIdx] = useState(0)

    useEffect(() => {
        const t = setInterval(() => setHeroIdx(i => (i + 1) % HERO_IMAGES.length), 5000)
        return () => clearInterval(t)
    }, [])

    return (
        <div>
            {/* ─── HERO ─────────────────────────────────── */}
            <section className="hero">
                {HERO_IMAGES.map((src, i) => (
                    <div key={i} className={`hero-bg ${i === heroIdx ? 'active' : ''}`}
                        style={{ backgroundImage: `url(${src})` }} />
                ))}
                <div className="hero-overlay" />
                <div className="hero-content container fade-up">
                    <div className="hero-badge">AI-Powered Fashion Studio</div>
                    <h1 className="hero-title">
                        Design Your<br />
                        <em className="hero-title-em">Perfect Style</em><br />
                        with AI
                    </h1>
                    <p className="hero-sub">
                        From a single prompt to runway-ready designs — generate, style, and shop your dream outfit in minutes.
                    </p>
                    <div className="hero-ctas">
                        <button className="btn btn-primary hero-btn" onClick={() => navigate('/design')}>
                            ✦ Start Designing Free
                        </button>
                        <button className="btn btn-ghost hero-btn" onClick={() => navigate('/upload')}>
                            📷 Try Photo Stylist
                        </button>
                    </div>

                    {/* Prompt chips */}
                    <div className="hero-chips">
                        {PROMPTS.map(p => (
                            <button key={p} className="chip" onClick={() => navigate(`/design?prompt=${encodeURIComponent(p)}`)}>
                                {p}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Scroll indicator */}
                <div className="hero-scroll">
                    <div className="scroll-mouse"><div className="scroll-dot" /></div>
                    <span>Scroll to explore</span>
                </div>
            </section>

            {/* ─── STATS STRIP ──────────────────────────── */}
            <section className="stats-strip">
                <div className="container">
                    <div className="stats-grid">
                        {STATS.map(s => (
                            <div key={s.label} className="stat-item">
                                <div className="stat-num">{s.num}</div>
                                <div className="stat-label">{s.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── FEATURES ─────────────────────────────── */}
            <section className="section features-section">
                <div className="container">
                    <div className="text-center" style={{ marginBottom: 56 }}>
                        <p className="section-eyebrow">What We Offer</p>
                        <h2 className="section-title">
                            Fashion Intelligence,<br />
                            <em className="gold-text">Reimagined</em>
                        </h2>
                        <p className="section-subtitle" style={{ marginTop: 16 }}>
                            Three powerful AI tools to transform how you experience fashion — all in one place.
                        </p>
                    </div>

                    <div className="features-grid">
                        {FEATURES.map((f, i) => (
                            <div key={i} className="feature-card" onClick={() => navigate(f.link)}>
                                <div className="feature-img-wrap">
                                    <img src={f.img} alt={f.title} loading="lazy" />
                                    <div className="feature-img-overlay" />
                                    <span className="feature-icon">{f.icon}</span>
                                </div>
                                <div className="feature-body">
                                    <h3 className="feature-title">{f.title}</h3>
                                    <p className="feature-desc">{f.desc}</p>
                                    <span className="feature-link">Explore →</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── HOW IT WORKS ─────────────────────────── */}
            <section className="section" style={{ background: 'rgba(255,255,255,0.02)' }}>
                <div className="container">
                    <div className="text-center" style={{ marginBottom: 56 }}>
                        <p className="section-eyebrow">Simple Process</p>
                        <h2 className="section-title">How It <em className="gold-text">Works</em></h2>
                    </div>
                    <div className="how-grid">
                        {[
                            { step: '01', title: 'Describe or Upload', desc: 'Type your fashion idea or upload a photo of yourself.' },
                            { step: '02', title: 'AI Generates', desc: 'Our AI creates a unique fashion design or outfit recommendation tailored to you.' },
                            { step: '03', title: 'Shop & Style', desc: 'Find affordable products that match, save your designs, and build your wardrobe.' },
                        ].map(s => (
                            <div key={s.step} className="how-card">
                                <div className="how-step">{s.step}</div>
                                <h3 className="how-title">{s.title}</h3>
                                <p className="how-desc">{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── CTA BANNER ───────────────────────────── */}
            <section className="section">
                <div className="container">
                    <div className="cta-banner">
                        <div className="cta-bg" />
                        <div className="cta-content">
                            <h2 className="cta-title">Ready to Design Your Dream Outfit?</h2>
                            <p className="cta-sub">Join thousands of fashion lovers already using AI Fashion Studio.</p>
                            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
                                <button className="btn btn-primary" onClick={() => navigate('/login?tab=register')}>
                                    ✦ Create Free Account
                                </button>
                                <button className="btn btn-secondary" onClick={() => navigate('/design')}>
                                    Try Without Account
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── FOOTER ───────────────────────────────── */}
            <footer className="footer">
                <div className="container">
                    <div className="footer-inner">
                        <span className="nav-logo" style={{ fontSize: '1.2rem' }}>✦ AI <span>Fashion</span></span>
                        <p style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>© 2026 AI Fashion Studio. Powered by AI.</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}
