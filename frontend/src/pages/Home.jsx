import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, Flame, Archive, BarChart2, Inbox, Mail, Send } from 'lucide-react'

const leftLines = [
  '{ "email_id": "msg-8f2a",',
  '  "from": "client@acme.com",',
  '  "subject": "Urgent: Contract",',
  '  "classified": "PRIORITY",',
  '  "confidence": 0.96,',
  '  "timestamp": "09:14 AM",',
  '  "action": "flagged",',
  '  "routed_to": "admin",',
  '}',
  'async function classify(email) {',
  '  const result = await',
  '    llm.route(email);',
  '  return result',
  '    .category;',
  '}',
]

const rightLines = [
  'pipeline.process({',
  '  rag_enabled: true,',
  '  fallback: "database",',
  '  auto_reply: true,',
  '  confidence_threshold: 0.85,',
  '  priority_notify: true,',
  '  classify: "groq/llama",',
  '  observe: "langfuse",',
  '})',
  '.then(result => {',
  '  emit("classified", result);',
  '  router.next(result);',
  '})',
  'const flow = FlowExecutor',
  '  .create({ mode: "auto" })',
]

const floatingIcons = [
  { Icon: Mail,    top: '12%',  left: '10%',   size: 28, opacity: 0.05, rotate: '-8deg' },
  { Icon: Send,    top: '22%',  right: '12%',  size: 22, opacity: 0.045, rotate: '12deg' },
  { Icon: Inbox,   top: '60%',  left: '8%',    size: 34, opacity: 0.04, rotate: '5deg' },
  { Icon: Mail,    bottom: '22%', right: '9%', size: 26, opacity: 0.05, rotate: '-10deg' },
  { Icon: Archive, top: '78%',  right: '18%',  size: 20, opacity: 0.04, rotate: '15deg' },
  { Icon: Send,    bottom: '32%', left: '18%', size: 24, opacity: 0.04, rotate: '-5deg' },
  { Icon: Inbox,   top: '45%',  right: '22%',  size: 18, opacity: 0.035, rotate: '-15deg' },
  { Icon: Mail,    bottom: '48%', left: '22%', size: 20, opacity: 0.035, rotate: '8deg' },
]

const navButtons = [
  { to: '/basic',        icon: AlertCircle, label: 'Basic Emails',    color: '#60a5fa' },
  { to: '/priority',     icon: Flame,       label: 'Priority Emails', color: '#f87171' },
  { to: '/non-business', icon: Archive,     label: 'Non-Business',    color: '#a78bfa' },
  { to: '/analysis',     icon: BarChart2,   label: 'Analysis',        color: '#34d399' },
]

export default function Home() {
  const navigate = useNavigate()
  const leftCanvasRef = useRef(null)
  const rightCanvasRef = useRef(null)

  useEffect(() => {
    // Left canvas animation
    const leftCanvas = leftCanvasRef.current
    if (!leftCanvas) return
    const leftCtx = leftCanvas.getContext('2d')
    
    // Right canvas animation
    const rightCanvas = rightCanvasRef.current
    if (!rightCanvas) return
    const rightCtx = rightCanvas.getContext('2d')
    
    let animId
    let leftEnvelopes = []
    let rightEnvelopes = []
    
    const resize = () => { 
      if (leftCanvas && rightCanvas) {
        leftCanvas.width = leftCanvas.offsetWidth
        leftCanvas.height = leftCanvas.offsetHeight
        rightCanvas.width = rightCanvas.offsetWidth
        rightCanvas.height = rightCanvas.offsetHeight
        
        // Initialize left envelopes (more of them)
        leftEnvelopes = Array.from({ length: 16 }, () => ({
          x: Math.random() * leftCanvas.width,
          y: Math.random() * leftCanvas.height,
          speedX: (Math.random() - 0.5) * 0.5,
          speedY: (Math.random() - 0.5) * 0.4 + 0.1,
          size: 12 + Math.random() * 12,
          opacity: 0.1 + Math.random() * 0.1,
        }))
        
        // Initialize right envelopes (more of them)
        rightEnvelopes = Array.from({ length: 16 }, () => ({
          x: Math.random() * rightCanvas.width,
          y: Math.random() * rightCanvas.height,
          speedX: (Math.random() - 0.5) * 0.5,
          speedY: (Math.random() - 0.5) * 0.4 + 0.1,
          size: 12 + Math.random() * 12,
          opacity: 0.1 + Math.random() * 0.1,
        }))
      }
    }
    resize()
    window.addEventListener('resize', resize)

    const drawEnvelope = (ctx, x, y, size, opacity) => {
      ctx.save()
      ctx.globalAlpha = opacity
      ctx.strokeStyle = '#60a5fa'
      ctx.fillStyle = '#60a5fa'
      ctx.lineWidth = 1.2
      
      // Draw envelope body
      ctx.strokeRect(x - size/2, y - size/2, size, size * 0.7)
      
      // Draw envelope flap (triangle)
      ctx.beginPath()
      ctx.moveTo(x - size/2, y - size/2)
      ctx.lineTo(x, y - size/2 + size * 0.35)
      ctx.lineTo(x + size/2, y - size/2)
      ctx.stroke()
      
      // Draw a small dot (like a seal)
      ctx.beginPath()
      ctx.arc(x, y - size/2 + size * 0.5, size * 0.1, 0, Math.PI * 2)
      ctx.fill()
      
      ctx.restore()
    }

    const animate = () => {
      // Clear and draw left canvas
      if (leftCtx && leftCanvas) {
        leftCtx.clearRect(0, 0, leftCanvas.width, leftCanvas.height)
        leftEnvelopes.forEach(envelope => {
          envelope.x += envelope.speedX
          envelope.y += envelope.speedY
          
          if (envelope.x < -50) envelope.x = leftCanvas.width + 50
          if (envelope.x > leftCanvas.width + 50) envelope.x = -50
          if (envelope.y < -50) envelope.y = leftCanvas.height + 50
          if (envelope.y > leftCanvas.height + 50) envelope.y = -50
          
          drawEnvelope(leftCtx, envelope.x, envelope.y, envelope.size, envelope.opacity)
        })
      }
      
      // Clear and draw right canvas
      if (rightCtx && rightCanvas) {
        rightCtx.clearRect(0, 0, rightCanvas.width, rightCanvas.height)
        rightEnvelopes.forEach(envelope => {
          envelope.x += envelope.speedX
          envelope.y += envelope.speedY
          
          if (envelope.x < -50) envelope.x = rightCanvas.width + 50
          if (envelope.x > rightCanvas.width + 50) envelope.x = -50
          if (envelope.y < -50) envelope.y = rightCanvas.height + 50
          if (envelope.y > rightCanvas.height + 50) envelope.y = -50
          
          drawEnvelope(rightCtx, envelope.x, envelope.y, envelope.size, envelope.opacity)
        })
      }
      
      animId = requestAnimationFrame(animate)
    }
    animate()

    return () => { 
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      background: '#020b18',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
      fontFamily: "'Inter', 'DM Sans', sans-serif",
    }}>

      {/* Grid */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.035,
        backgroundImage: 'linear-gradient(rgba(96,165,250,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(96,165,250,0.6) 1px, transparent 1px)',
        backgroundSize: '65px 65px',
      }} />

      {/* Ambient glow */}
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: 700, height: 700, borderRadius: '50%', background: 'radial-gradient(circle, rgba(29,78,216,0.1) 0%, transparent 70%)', filter: 'blur(50px)' }} />
      </div>

      {/* Floating icons */}
      {floatingIcons.map(({ Icon, size, opacity, rotate, ...pos }, i) => (
        <div key={i} style={{ position: 'absolute', ...pos, opacity, transform: `rotate(${rotate})`, pointerEvents: 'none', color: '#3b82f6' }}>
          <Icon size={size} strokeWidth={1.2} />
        </div>
      ))}

      {/* Left animated envelopes */}
      <div style={{ 
        position: 'absolute', 
        left: 0, 
        top: 0, 
        width: '300px', 
        height: '100%', 
        pointerEvents: 'none',
        zIndex: 2,
      }}>
        <canvas ref={leftCanvasRef} style={{ width: '100%', height: '100%' }} />
      </div>

      {/* Right animated envelopes */}
      <div style={{ 
        position: 'absolute', 
        right: 0, 
        top: 0, 
        width: '300px', 
        height: '100%', 
        pointerEvents: 'none',
        zIndex: 2,
      }}>
        <canvas ref={rightCanvasRef} style={{ width: '100%', height: '100%' }} />
      </div>

      {/* Left code snippet (overlay on animation) */}
      <div style={{ position: 'absolute', left: 0, top: 0, width: 300, height: '100%', overflow: 'hidden', pointerEvents: 'none', zIndex: 3 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to right, #020b18, transparent)', zIndex: 1 }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, #020b18, transparent 20%, transparent 80%, #020b18)', zIndex: 1 }} />
        <div style={{ paddingTop: '6rem', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', position: 'relative', zIndex: 2 }}>
          {leftLines.map((line, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 12, color: 'rgba(148,163,184,0.35)', whiteSpace: 'nowrap' }}>{line}</div>
          ))}
        </div>
      </div>

      {/* Right code snippet (overlay on animation) */}
      <div style={{ position: 'absolute', right: 0, top: 0, width: 300, height: '100%', overflow: 'hidden', pointerEvents: 'none', zIndex: 3 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to left, #020b18, transparent)', zIndex: 1 }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, #020b18, transparent 20%, transparent 80%, #020b18)', zIndex: 1 }} />
        <div style={{ paddingTop: '6rem', paddingRight: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end', position: 'relative', zIndex: 2 }}>
          {rightLines.map((line, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 12, color: 'rgba(148,163,184,0.35)', whiteSpace: 'nowrap' }}>{line}</div>
          ))}
        </div>
      </div>

      {/* Center content - perfectly centered */}
      <div style={{ 
        position: 'relative', 
        zIndex: 10, 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        textAlign: 'center', 
        padding: '0 2rem', 
        maxWidth: 800,
        margin: '0 auto',
        gap: '1.5rem',
      }}>

        {/* Headline - ALL CAPS */}
        <h1 style={{
          fontSize: 'clamp(3rem, 8vw, 4.5rem)',
          fontWeight: 800,
          fontFamily: "'Clash Display', 'Syne', 'Inter', sans-serif",
          letterSpacing: '-0.02em',
          background: 'linear-gradient(135deg, #ffffff 0%, #94a3f8 100%)',
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          textShadow: '0 2px 10px rgba(59,130,246,0.15)',
          textTransform: 'uppercase',
        }}>
          Inbox Manager
        </h1>

        {/* Subtitle */}
        <p style={{ fontSize: '1rem', color: '#5a7fb5', letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 400 }}>
          AI Email Automation &amp; Management System
        </p>

        {/* Nav buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {navButtons.map(({ to, icon: Icon, label, color }) => (
            <button
              key={to}
              onClick={() => navigate(to)}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.6rem',
                background: 'rgba(10,22,40,0.85)',
                border: `1px solid ${color}40`,
                borderRadius: 10,
                padding: '0.7rem 1.3rem',
                color: '#b9c7db',
                fontSize: '0.9rem',
                fontWeight: 500,
                fontFamily: "'Inter', 'DM Sans', sans-serif",
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: `0 0 8px ${color}20`,
                backdropFilter: 'blur(2px)',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = color
                e.currentTarget.style.color = color
                e.currentTarget.style.background = 'rgba(10,22,40,1)'
                e.currentTarget.style.boxShadow = `0 0 18px ${color}50`
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = `${color}40`
                e.currentTarget.style.color = '#b9c7db'
                e.currentTarget.style.background = 'rgba(10,22,40,0.85)'
                e.currentTarget.style.boxShadow = `0 0 8px ${color}20`
              }}
            >
              <Icon size={16} strokeWidth={1.8} />
              {label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', opacity: 0.25, marginTop: '1rem' }}>
          <div style={{ width: 70, height: 1, background: '#3b82f6' }} />
          <Inbox size={14} color="#3b82f6" />
          <div style={{ width: 70, height: 1, background: '#3b82f6' }} />
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', fontSize: '0.8rem', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          <a href="https://github.com/AleeCodeAI" target="_blank" rel="noopener noreferrer"
            style={{ color: '#1e3a5f', textDecoration: 'none', transition: 'color 0.15s', fontWeight: 500 }}
            onMouseEnter={e => e.target.style.color = '#60a5fa'}
            onMouseLeave={e => e.target.style.color = '#1e3a5f'}>
            GitHub
          </a>
          <span style={{ color: '#0f2240' }}>·</span>
          <a href="https://github.com/AleeCodeAI/Intelligent_Inbox_Manager" target="_blank" rel="noopener noreferrer"
            style={{ color: '#1e3a5f', textDecoration: 'none', transition: 'color 0.15s', fontWeight: 500 }}
            onMouseEnter={e => e.target.style.color = '#60a5fa'}
            onMouseLeave={e => e.target.style.color = '#1e3a5f'}>
            Repository
          </a>
        </div>

        <p style={{ fontSize: '0.75rem', color: '#0f2240', fontWeight: 500 }}>Built by Alee — 17 year old aspiring AI Engineer from Quetta, Pakistan</p>

      </div>
    </div>
  )
}