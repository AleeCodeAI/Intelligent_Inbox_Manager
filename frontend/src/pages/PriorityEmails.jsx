import { useState, useEffect, useRef } from 'react'
import emailService from '../services/emailService'

const LEFT_LINES = [
  '{ "email_id": "msg-8f2a",',
  '  "from": "client@acme.com",',
  '  "subject": "Urgent: Contract",',
  '  "classified": "PRIORITY",',
  '  "confidence": 0.96,',
  '  "action": "flagged",',
  '  "routed_to": "admin",',
  '}',
  'async function classify(email) {',
  '  const result = await',
  '    llm.route(email);',
  '  return result.category;',
  '}',
]

const RIGHT_LINES = [
  'pipeline.process({',
  '  rag_enabled: true,',
  '  fallback: "database",',
  '  auto_reply: true,',
  '  confidence_threshold: 0.85,',
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

export default function PriorityEmails() {
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [adminActions, setAdminActions] = useState({})
  const [calendarDetails, setCalendarDetails] = useState({})
  const [notification, setNotification] = useState(null)
  const [processingId, setProcessingId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const canvasRef = useRef(null)
  const animRef = useRef(null)

  // Priority type color mapping
  const getPriorityColor = (type) => {
    switch(type) {
      case 'SENSITIVE': return '#ef4444'
      case 'HIGH_VALUE': return '#f59e0b'
      case 'CLIENT_COMMUNICATION': return '#3b82f6'
      case 'APPOINTMENT': return '#8b5cf6'
      default: return '#a78bfa'
    }
  }

  const getPriorityLabel = (type) => {
    switch(type) {
      case 'SENSITIVE': return '🔒 Sensitive'
      case 'HIGH_VALUE': return '⭐ High Value'
      case 'CLIENT_COMMUNICATION': return '🤝 Client Communication'
      case 'APPOINTMENT': return '📅 Appointment'
      default: return type
    }
  }

  // ── Envelope canvas animation ──────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let envelopes = []

    const resize = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      envelopes = Array.from({ length: 18 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        sx: (Math.random() - 0.5) * 0.45,
        sy: (Math.random() - 0.5) * 0.35 + 0.08,
        size: 10 + Math.random() * 12,
        op: 0.04 + Math.random() * 0.05,
      }))
    }
    resize()
    window.addEventListener('resize', resize)

    const drawEnvelope = (x, y, s, op) => {
      ctx.save()
      ctx.globalAlpha = op
      ctx.strokeStyle = '#a78bfa'
      ctx.fillStyle = '#a78bfa'
      ctx.lineWidth = 1.1
      ctx.strokeRect(x - s / 2, y - s / 2, s, s * 0.7)
      ctx.beginPath()
      ctx.moveTo(x - s / 2, y - s / 2)
      ctx.lineTo(x, y - s / 2 + s * 0.33)
      ctx.lineTo(x + s / 2, y - s / 2)
      ctx.stroke()
      ctx.restore()
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      envelopes.forEach(e => {
        e.x += e.sx
        e.y += e.sy
        if (e.x < -40) e.x = canvas.width + 40
        if (e.x > canvas.width + 40) e.x = -40
        if (e.y < -40) e.y = canvas.height + 40
        if (e.y > canvas.height + 40) e.y = -40
        drawEnvelope(e.x, e.y, e.size, e.op)
      })
      animRef.current = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      cancelAnimationFrame(animRef.current)
      window.removeEventListener('resize', resize)
    }
  }, [])

  // ── Data fetching ───────────────────────────────────────────────
  useEffect(() => { fetchEmails() }, [])

  const fetchEmails = async () => {
    setLoading(true)
    try {
      const response = await emailService.getPriorityUnreviewed()
      if (response.status === 'success') {
        setEmails(response.data)
        const initial = {}
        const initialCalendar = {}
        response.data.forEach(e => { 
          initial[e.email_db_id] = ''
          initialCalendar[e.email_db_id] = {
            title: '',
            start: '',
            end: ''
          }
        })
        setAdminActions(initial)
        setCalendarDetails(initialCalendar)
      }
    } catch (error) {
      showNotification('error', 'Failed to fetch priority emails: ' + (error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  const showNotification = (type, message) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 5000)
  }

  const handlePriorityAction = async (email) => {
    setProcessingId(email.email_db_id)
    try {
      // Validate for APPOINTMENT type
      if (email.priority_type === 'APPOINTMENT') {
        const calendar = calendarDetails[email.email_db_id]
        if (!calendar.start || !calendar.end) {
          showNotification('error', 'Please set both start and end times for the appointment')
          setProcessingId(null)
          return
        }
      }

      // Validate manual response
      if (!adminActions[email.email_db_id]?.trim()) {
        showNotification('error', 'Please enter a response message')
        setProcessingId(null)
        return
      }

      // Build payload with calendar_details defaulting to null
      const payload = {
        gmail_id: email.gmail_id,
        sender_name: email.sender_name,
        priority_type: email.priority_type,
        manual_response: adminActions[email.email_db_id].trim(),
        calendar_details: null
      }
      
      // Only add calendar_details object for APPOINTMENT type
      if (email.priority_type === 'APPOINTMENT') {
        const calendar = calendarDetails[email.email_db_id]
        payload.calendar_details = {
          title: calendar.title?.trim() || `Meeting with ${email.sender_name}`,
          start: calendar.start,
          end: calendar.end
        }
      }
      
      console.log('Sending payload to backend:', JSON.stringify(payload, null, 2))
      const response = await emailService.takePriorityAction(payload)
      console.log('Backend response:', response)
      
      showNotification('success', `Action completed for ${email.sender_name}!`)
      setTimeout(() => fetchEmails(), 1000)
    } catch (error) {
      console.error('Full error:', error)
      console.error('Error response data:', error.response?.data)
      const errorMessage = error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message
      showNotification('error', `Failed to process: ${errorMessage}`)
    } finally {
      setProcessingId(null)
    }
  }

  const handleDeleteEmail = async (email) => {
    if (!window.confirm(`Delete priority email from ${email.sender_name}?`)) return
    setDeletingId(email.email_db_id)
    try {
      await emailService.deleteEmail(email.gmail_id)
      showNotification('success', `Email from ${email.sender_name} deleted.`)
      setEmails(prev => prev.filter(e => e.email_db_id !== email.email_db_id))
      setExpandedId(null)
    } catch (error) {
      showNotification('error', 'Failed to delete: ' + (error.response?.data?.message || error.message))
    } finally {
      setDeletingId(null)
    }
  }

  const toggleExpand = (id) => setExpandedId(expandedId === id ? null : id)
  const updateAction = (id, value) => setAdminActions(prev => ({ ...prev, [id]: value }))
  const updateCalendar = (id, field, value) => {
    setCalendarDetails(prev => ({
      ...prev,
      [id]: { ...prev[id], [field]: value }
    }))
  }

  // ── Loading state ───────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#020b18', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Inter', sans-serif" }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: 36, height: 36, border: '2px solid rgba(167,139,250,0.15)', borderTopColor: '#a78bfa', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }} />
          <p style={{ color: 'rgba(148,163,184,0.5)', marginTop: '1rem', fontSize: '0.85rem' }}>Loading priority emails...</p>
        </div>
      </div>
    )
  }

  // ── Main render ─────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: '#020b18', position: 'relative', overflow: 'hidden', fontFamily: "'Inter', sans-serif" }}>

      {/* Grid overlay */}
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.03, backgroundImage: 'linear-gradient(rgba(167,139,250,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(167,139,250,0.6) 1px,transparent 1px)', backgroundSize: '55px 55px' }} />

      {/* Ambient center glow - purple for priority */}
      <div style={{ position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%,-50%)', width: 700, height: 500, borderRadius: '50%', background: 'radial-gradient(circle,rgba(139,92,246,0.08) 0%,transparent 70%)', filter: 'blur(40px)', pointerEvents: 'none' }} />

      {/* Envelope canvas */}
      <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 2 }} />

      {/* Left code column */}
      <div style={{ position: 'absolute', left: 0, top: 0, width: 260, height: '100%', overflow: 'hidden', pointerEvents: 'none', zIndex: 3 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to right,#020b18 55%,transparent)', zIndex: 1 }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom,#020b18,transparent 18%,transparent 82%,#020b18)', zIndex: 1 }} />
        <div style={{ paddingTop: '5rem', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: 6, position: 'relative', zIndex: 2 }}>
          {LEFT_LINES.map((line, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 11, color: `rgba(148,163,184,${Math.max(0.1, 0.32 - i * 0.018)})`, whiteSpace: 'nowrap' }}>{line}</div>
          ))}
        </div>
      </div>

      {/* Right code column */}
      <div style={{ position: 'absolute', right: 0, top: 0, width: 260, height: '100%', overflow: 'hidden', pointerEvents: 'none', zIndex: 3 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to left,#020b18 55%,transparent)', zIndex: 1 }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom,#020b18,transparent 18%,transparent 82%,#020b18)', zIndex: 1 }} />
        <div style={{ paddingTop: '5rem', paddingRight: '1.5rem', display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end', position: 'relative', zIndex: 2 }}>
          {RIGHT_LINES.map((line, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 11, color: `rgba(148,163,184,${Math.max(0.1, 0.32 - i * 0.018)})`, whiteSpace: 'nowrap' }}>{line}</div>
          ))}
        </div>
      </div>

      {/* Notification */}
      {notification && (
        <div style={{ position: 'fixed', top: 20, right: 20, zIndex: 1000, padding: '0.65rem 1.25rem', background: notification.type === 'success' ? 'rgba(16,185,129,0.95)' : 'rgba(239,68,68,0.95)', borderRadius: 8, color: '#fff', fontSize: '0.875rem', backdropFilter: 'blur(8px)', animation: 'slideInRight 0.3s ease', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}>
          {notification.message}
        </div>
      )}

      {/* Page content - centered wrapper */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: 860, margin: '0 auto', padding: '3.5rem 2rem 4rem' }}>

        {/* Header */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: '2.5rem', gap: '0.35rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 20, padding: '4px 14px', marginBottom: '0.5rem' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#a78bfa', display: 'inline-block' }} />
          <span style={{ fontSize: 11, color: '#a78bfa', letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 600 }}>Priority Queue</span>
        </div>
        
        {/* Slate-Steel Metallic Gradient Title Header */}
        <h1 style={{
          fontSize: 'clamp(1.8rem, 4vw, 2.4rem)',
          fontWeight: 700,
          letterSpacing: '-0.01em',
          background: 'linear-gradient(135deg, #ffffff 30%, #c4b5fd 75%, #a78bfa 100%)',
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          textTransform: 'uppercase',
          margin: 0,
        }}>
          Priority Emails
        </h1>
        
        <p style={{ color: '#a78bfa', fontSize: '0.75rem', margin: 0, letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 500, opacity: 0.8 }}>
          High-confidence emails requiring executive review
        </p>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginTop: '0.75rem' }}>
          <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
          <span style={{ fontSize: '0.72rem', color: '#a78bfa', letterSpacing: '0.05em', fontWeight: 500 }}>
            {emails.length} priority email{emails.length !== 1 ? 's' : ''} awaiting action
          </span>
          <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
        </div>
      </div>

        {/* Card container */}
        <div style={{ background: 'rgba(10,20,36,0.85)', border: '1px solid rgba(139,92,246,0.12)', borderRadius: 16, padding: '1.75rem 1.5rem', backdropFilter: 'blur(12px)', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}>

          {/* Toolbar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '0.7rem', color: 'rgba(148,163,184,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Pending executive actions</span>
            <button
              onClick={fetchEmails}
              style={{ padding: '0.4rem 1rem', background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'rgba(148,163,184,0.7)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 500, fontFamily: 'inherit', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#a78bfa'; e.currentTarget.style.color = '#a78bfa'; e.currentTarget.style.background = 'rgba(139,92,246,0.12)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)'; e.currentTarget.style.color = 'rgba(148,163,184,0.7)'; e.currentTarget.style.background = 'rgba(139,92,246,0.06)' }}
            >
              ↺ Refresh Queue
            </button>
          </div>

          {/* Empty state */}
          {emails.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3.5rem 2rem', border: '1px dashed rgba(139,92,246,0.15)', borderRadius: 12 }}>
              <div style={{ fontSize: 28, color: '#a78bfa', marginBottom: '0.75rem' }}>✓</div>
              <h3 style={{ color: '#fff', margin: '0 0 0.35rem', fontSize: '1.1rem', fontWeight: 600 }}>No priority emails!</h3>
              <p style={{ color: 'rgba(148,163,184,0.45)', fontSize: '0.85rem', margin: 0 }}>All high-priority messages have been reviewed.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {emails.map(email => {
                const isExpanded = expandedId === email.email_db_id
                const hasAction = !!adminActions[email.email_db_id]?.trim()
                const isAppointment = email.priority_type === 'APPOINTMENT'
                const calendar = calendarDetails[email.email_db_id] || { title: '', start: '', end: '' }
                const hasValidCalendar = isAppointment ? (calendar.start && calendar.end) : true
                
                return (
                  <div
                    key={email.email_db_id}
                    style={{ background: '#0a1424', border: `1px solid ${isExpanded ? 'rgba(139,92,246,0.5)' : 'rgba(17,34,64,0.7)'}`, borderRadius: 12, overflow: 'hidden', transition: 'all 0.25s', boxShadow: isExpanded ? '0 0 20px rgba(139,92,246,0.1)' : 'none' }}
                  >
                    {/* Row header */}
                    <div
                      onClick={() => toggleExpand(email.email_db_id)}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.25rem', cursor: 'pointer', background: isExpanded ? 'rgba(139,92,246,0.05)' : 'transparent', transition: 'background 0.2s' }}
                      onMouseEnter={e => { if (!isExpanded) e.currentTarget.style.background = 'rgba(255,255,255,0.02)' }}
                      onMouseLeave={e => { if (!isExpanded) e.currentTarget.style.background = 'transparent' }}
                    >
                      <div style={{ flex: 1, paddingRight: '1rem' }}>
                        <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem', marginBottom: '0.25rem' }}>{email.subject}</div>
                        <div style={{ display: 'flex', gap: '0.6rem', fontSize: '0.78rem', color: 'rgba(148,163,184,0.5)' }}>
                          <span style={{ color: 'rgba(148,163,184,0.85)' }}>{email.sender_name}</span>
                          <span>•</span>
                          <span>{email.sender_email}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ fontSize: 10, background: `rgba(${parseInt(getPriorityColor(email.priority_type).slice(1,3), 16)}, ${parseInt(getPriorityColor(email.priority_type).slice(3,5), 16)}, ${parseInt(getPriorityColor(email.priority_type).slice(5,7), 16)}, 0.1)`, border: `1px solid ${getPriorityColor(email.priority_type)}40`, color: getPriorityColor(email.priority_type), padding: '2px 8px', borderRadius: 10, letterSpacing: '0.06em', fontWeight: 500 }}>
                          {getPriorityLabel(email.priority_type)} • {(email.confidence * 100).toFixed(0)}%
                        </span>
                        <span style={{ color: 'rgba(148,163,184,0.4)', fontSize: '0.7rem', display: 'inline-block', transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>▼</span>
                      </div>
                    </div>

                    {/* Expanded body */}
                    {isExpanded && (
                      <div style={{ padding: '1.25rem 1.5rem', borderTop: '1px solid rgba(139,92,246,0.08)', background: 'rgba(2,8,23,0.5)', animation: 'slideDown 0.25s ease-out' }}>

                        {/* Original message */}
                        <div style={{ marginBottom: '1.25rem' }}>
                          <h4 style={{ color: '#a78bfa', fontWeight: 600, margin: '0 0 0.4rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Original Message</h4>
                          <div style={{ padding: '0.85rem 1rem', background: '#020b18', border: '1px solid rgba(139,92,246,0.1)', borderLeft: '2px solid rgba(139,92,246,0.35)', borderRadius: 8, color: 'rgba(148,163,184,0.8)', fontSize: '0.88rem', lineHeight: 1.65, whiteSpace: 'pre-wrap' }}>
                            {email.body}
                          </div>
                        </div>

                        {/* Calendar picker for APPOINTMENT type */}
                        {isAppointment && (
                          <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'rgba(139,92,246,0.04)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 8 }}>
                            <h4 style={{ color: '#a78bfa', fontWeight: 600, margin: '0 0 0.75rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>📅 Calendar Event Details (Required)</h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                              <input
                                type="text"
                                value={calendar.title}
                                onChange={e => updateCalendar(email.email_db_id, 'title', e.target.value)}
                                placeholder="Event title (optional - defaults to 'Meeting with [sender]')"
                                style={{ width: '100%', padding: '0.65rem 0.85rem', background: '#020b18', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 6, color: 'rgba(148,163,184,0.9)', fontSize: '0.85rem', outline: 'none' }}
                                onFocus={e => e.currentTarget.style.borderColor = '#a78bfa'}
                                onBlur={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)'}
                              />
                              <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <div style={{ flex: 1 }}>
                                  <label style={{ fontSize: '0.7rem', color: 'rgba(148,163,184,0.5)', display: 'block', marginBottom: '0.25rem' }}>Start time *</label>
                                  <input
                                    type="datetime-local"
                                    value={calendar.start}
                                    onChange={e => updateCalendar(email.email_db_id, 'start', e.target.value)}
                                    style={{ width: '100%', padding: '0.65rem 0.85rem', background: '#020b18', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 6, color: 'rgba(148,163,184,0.9)', fontSize: '0.85rem', outline: 'none' }}
                                    onFocus={e => e.currentTarget.style.borderColor = '#a78bfa'}
                                    onBlur={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)'}
                                  />
                                </div>
                                <div style={{ flex: 1 }}>
                                  <label style={{ fontSize: '0.7rem', color: 'rgba(148,163,184,0.5)', display: 'block', marginBottom: '0.25rem' }}>End time *</label>
                                  <input
                                    type="datetime-local"
                                    value={calendar.end}
                                    onChange={e => updateCalendar(email.email_db_id, 'end', e.target.value)}
                                    style={{ width: '100%', padding: '0.65rem 0.85rem', background: '#020b18', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 6, color: 'rgba(148,163,184,0.9)', fontSize: '0.85rem', outline: 'none' }}
                                    onFocus={e => e.currentTarget.style.borderColor = '#a78bfa'}
                                    onBlur={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)'}
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Admin response */}
                        <div style={{ marginBottom: '1.25rem' }}>
                          <h4 style={{ color: '#fff', fontWeight: 600, margin: '0 0 0.4rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Executive Response *</h4>
                          <textarea
                            value={adminActions[email.email_db_id] || ''}
                            onChange={e => updateAction(email.email_db_id, e.target.value)}
                            placeholder="Enter your decision or response for this priority email..."
                            rows={5}
                            style={{ width: '100%', boxSizing: 'border-box', padding: '0.85rem 1rem', background: '#020b18', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 8, color: 'rgba(148,163,184,0.9)', fontSize: '0.88rem', lineHeight: 1.6, fontFamily: 'inherit', resize: 'vertical', outline: 'none', transition: 'border-color 0.2s' }}
                            onFocus={e => e.currentTarget.style.borderColor = '#a78bfa'}
                            onBlur={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.15)'}
                          />
                        </div>

                        {/* Actions */}
                        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                          <button
                            onClick={() => handleDeleteEmail(email)}
                            disabled={deletingId === email.email_db_id}
                            style={{ padding: '0.45rem 1rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, color: '#f87171', cursor: deletingId === email.email_db_id ? 'not-allowed' : 'pointer', fontSize: '0.82rem', fontWeight: 500, fontFamily: 'inherit', transition: 'all 0.2s' }}
                            onMouseEnter={e => { if (deletingId !== email.email_db_id) { e.currentTarget.style.background = 'rgba(239,68,68,0.15)'; e.currentTarget.style.borderColor = '#ef4444' } }}
                            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.06)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.2)' }}
                          >
                            {deletingId === email.email_db_id ? 'Deleting...' : 'Delete'}
                          </button>
                          <button
                            onClick={() => handlePriorityAction(email)}
                            disabled={processingId === email.email_db_id || !hasAction || (isAppointment && !hasValidCalendar)}
                            style={{ padding: '0.45rem 1.25rem', background: (hasAction && (!isAppointment || hasValidCalendar)) ? '#8b5cf6' : 'rgba(139,92,246,0.15)', border: 'none', borderRadius: 8, color: '#fff', cursor: (!hasAction || processingId === email.email_db_id || (isAppointment && !hasValidCalendar)) ? 'not-allowed' : 'pointer', fontSize: '0.82rem', fontWeight: 600, fontFamily: 'inherit', transition: 'all 0.2s', opacity: (!hasAction || processingId === email.email_db_id || (isAppointment && !hasValidCalendar)) ? 0.45 : 1 }}
                            onMouseEnter={e => { if (hasAction && processingId !== email.email_db_id && (!isAppointment || hasValidCalendar)) e.currentTarget.style.filter = 'brightness(1.12)' }}
                            onMouseLeave={e => { e.currentTarget.style.filter = 'none' }}
                          >
                            {processingId === email.email_db_id ? 'Processing...' : 'Execute ↗'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(40px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}