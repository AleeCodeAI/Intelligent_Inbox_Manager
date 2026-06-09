import { useState, useEffect } from 'react'
import emailService from '../services/emailService'

const LEFT_LINES = [
  '{ "appointment_id": "apt-8f2a",',
  '  "event_title": "Client Sync",',
  '  "event_start": "2025-03-20T14:00",',
  '  "calendar_status": "failed",',
  '  "routed_to": "calendar",',
  '}',
  'async function fetchAppointments() {',
  '  const result = await',
  '    db.appointments.find();',
  '  return result.data;',
  '}',
]

const RIGHT_LINES = [
  'calendar.sync({',
  '  provider: "google",',
  '  timezone: "UTC",',
  '  auto_update: true,',
  '  retry_on_fail: 3,',
  '})',
  '.then(appointments => {',
  '  render(appointments);',
  '  cache.set(appointments);',
  '})',
  'const view = AppointmentView',
  '  .create({ mode: "list" })',
]

export default function Appointments() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [notification, setNotification] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  // Appointment status color mapping
  const getAppointmentColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'confirmed': return '#10b981'
      case 'pending': return '#f59e0b'
      case 'error': return '#ef4444'
      case 'failed': return '#ef4444'
      case 'cancelled': return '#6b7280'
      default: return '#6b7280'
    }
  }

  const getAppointmentLabel = (status) => {
    switch(status?.toLowerCase()) {
      case 'confirmed': return 'Confirmed'
      case 'pending': return 'Pending'
      case 'error': return 'Failed'
      case 'failed': return 'Failed'
      case 'cancelled': return 'Cancelled'
      default: return status || 'Unknown'
    }
  }

  const getConfirmationStatus = (status) => {
    switch(status?.toLowerCase()) {
      case 'success': return { label: 'Email Sent', color: '#10b981' }
      case 'sent': return { label: 'Email Sent', color: '#10b981' }
      case 'pending': return { label: 'Awaiting', color: '#f59e0b' }
      case 'failed': return { label: 'Failed', color: '#ef4444' }
      default: return { label: 'Unknown', color: '#6b7280' }
    }
  }

  const formatDateTime = (isoString) => {
    if (!isoString) return 'TBD'
    const date = new Date(isoString)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit'
    })
  }

  // ── Data fetching ───────────────────────────────────────────────
  useEffect(() => { fetchAppointments() }, [])

  const fetchAppointments = async () => {
    setLoading(true)
    try {
      const response = await emailService.getAppointments()
      if (response.status === 'success') {
        setAppointments(response.data)
      }
    } catch (error) {
      showNotification('error', 'Failed to fetch appointments: ' + (error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  const showNotification = (type, message) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 5000)
  }

  const handleDeleteAppointment = async (appointment) => {
    if (!window.confirm(`Delete appointment "${appointment.event_title}" from ${appointment.sender_name}?`)) return
    setDeletingId(appointment.email_db_id)
    try {
      await emailService.deleteAppointment({
        gmail_id: appointment.gmail_id,
        event_id: appointment.event_id
      })
      showNotification('success', `Appointment from ${appointment.sender_name} deleted.`)
      setAppointments(prev => prev.filter(apt => apt.email_db_id !== appointment.email_db_id))
      setExpandedId(null)
    } catch (error) {
      showNotification('error', 'Failed to delete: ' + (error.response?.data?.message || error.message))
    } finally {
      setDeletingId(null)
    }
  }

  const toggleExpand = (id) => setExpandedId(expandedId === id ? null : id)

  // ── Loading state ───────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#020b18', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Inter', sans-serif" }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: 36, height: 36, border: '2px solid rgba(139,92,246,0.15)', borderTopColor: '#8b5cf6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }} />
          <p style={{ color: 'rgba(148,163,184,0.5)', marginTop: '1rem', fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 500 }}>Loading appointments...</p>
        </div>
      </div>
    )
  }

  // ── Main render ─────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: '#020b18', position: 'relative', overflow: 'hidden', fontFamily: "'Inter', sans-serif" }}>

      {/* Grid overlay */}
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.03, backgroundImage: 'linear-gradient(rgba(139,92,246,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(139,92,246,0.6) 1px,transparent 1px)', backgroundSize: '55px 55px' }} />

      {/* Ambient center glow */}
      <div style={{ position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%,-50%)', width: 700, height: 500, borderRadius: '50%', background: 'radial-gradient(circle,rgba(139,92,246,0.08) 0%,transparent 70%)', filter: 'blur(40px)', pointerEvents: 'none' }} />

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
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#8b5cf6', display: 'inline-block' }} />
            <span style={{ fontSize: 11, color: '#8b5cf6', letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 600 }}>Calendar Queue</span>
          </div>
          
          <h1 style={{
            fontSize: 'clamp(1.8rem, 4vw, 2.4rem)',
            fontWeight: 700,
            letterSpacing: '-0.01em',
            background: 'linear-gradient(135deg, #ffffff 30%, #a78bfa 75%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            color: 'transparent',
            textTransform: 'uppercase',
            margin: 0,
          }}>
            Appointments
          </h1>
          
          <p style={{ color: '#5a7fb5', fontSize: '0.75rem', margin: 0, letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 500, opacity: 0.8 }}>
            Scheduled meetings and calendar events
          </p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginTop: '0.75rem' }}>
            <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
            <span style={{ fontSize: '0.72rem', color: '#5a7fb5', letterSpacing: '0.05em', fontWeight: 500 }}>
              {appointments.length} appointment{appointments.length !== 1 ? 's' : ''} scheduled
            </span>
            <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
          </div>
        </div>

        {/* Card container */}
        <div style={{ background: 'rgba(6,18,36,0.85)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: 16, padding: '1.75rem 1.5rem', backdropFilter: 'blur(12px)', boxShadow: 'none' }}>

          {/* Toolbar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '0.72rem', color: '#5a7fb5', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 600 }}>Upcoming events</span>
            <button
              onClick={fetchAppointments}
              style={{ padding: '0.4rem 1rem', background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: '#a78bfa', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.02em', fontFamily: 'inherit', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#a78bfa'; e.currentTarget.style.color = '#fff'; e.currentTarget.style.background = '#7c3aed' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)'; e.currentTarget.style.color = '#a78bfa'; e.currentTarget.style.background = 'rgba(139,92,246,0.06)' }}
            >
              ↺ Refresh Queue
            </button>
          </div>

          {/* Empty state */}
          {appointments.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3.5rem 2rem', border: '1px dashed rgba(139,92,246,0.15)', borderRadius: 12 }}>
              <div style={{ fontSize: 24, color: '#8b5cf6', marginBottom: '0.5rem', fontWeight: 700 }}>📅</div>
              <h3 style={{ color: '#fff', margin: '0 0 0.25rem', fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>No appointments found!</h3>
              <p style={{ color: '#5a7fb5', fontSize: '0.8rem', margin: 0, fontWeight: 400 }}>All calendar events are up to date.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {appointments.map(appointment => {
                const isExpanded = expandedId === appointment.email_db_id
                const badgeColor = getAppointmentColor(appointment.calendar_status)
                const confirmStatus = getConfirmationStatus(appointment.confirmation_email_status)
                const isFailed = appointment.calendar_status?.toLowerCase() === 'error' || appointment.calendar_status?.toLowerCase() === 'failed'
                
                return (
                  <div
                    key={appointment.email_db_id}
                    style={{ 
                      background: '#0a1424', 
                      border: `1px solid ${isExpanded ? 'rgba(139,92,246,0.4)' : 'rgba(255,255,255,0.03)'}`,
                      borderLeft: isFailed ? '3px solid #ef4444' : 'none',
                      borderRadius: 12, 
                      overflow: 'hidden', 
                      transition: 'all 0.25s' 
                    }}
                  >
                    {/* Row header */}
                    <div
                      onClick={() => toggleExpand(appointment.email_db_id)}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.25rem', cursor: 'pointer', background: isExpanded ? 'rgba(139,92,246,0.04)' : 'transparent', transition: 'background 0.2s' }}
                      onMouseEnter={e => { if (!isExpanded) e.currentTarget.style.background = 'rgba(255,255,255,0.01)' }}
                      onMouseLeave={e => { if (!isExpanded) e.currentTarget.style.background = 'transparent' }}
                    >
                      <div style={{ flex: 1, paddingRight: '1rem' }}>
                        <div style={{ fontWeight: 700, color: '#fff', fontSize: '0.9rem', marginBottom: '0.3rem', letterSpacing: '0.01em' }}>
                          {appointment.event_title}
                          {isFailed && <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: '#ef4444', fontWeight: 500 }}>(Needs Manual Setup)</span>}
                        </div>
                        <div style={{ display: 'flex', gap: '0.6rem', fontSize: '0.78rem', color: '#5a7fb5', fontWeight: 500, flexWrap: 'wrap' }}>
                          <span style={{ color: '#fff', opacity: 0.9 }}>{appointment.sender_name}</span>
                          <span style={{ opacity: 0.4 }}>•</span>
                          <span style={{ fontFamily: 'monospace', opacity: 0.8 }}>{appointment.sender_email}</span>
                          <span style={{ opacity: 0.4 }}>•</span>
                          <span style={{ color: '#a78bfa' }}>{formatDateTime(appointment.event_start)}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ 
                          fontSize: 10, 
                          background: `${badgeColor}12`, 
                          border: `1px solid ${badgeColor}33`, 
                          color: badgeColor, 
                          padding: '3px 9px', 
                          borderRadius: 6, 
                          letterSpacing: '0.06em', 
                          fontWeight: 600 
                        }}>
                          {getAppointmentLabel(appointment.calendar_status)}
                        </span>
                        <span style={{ color: '#5a7fb5', fontSize: '0.65rem', display: 'inline-block', transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s', opacity: 0.7 }}>▼</span>
                      </div>
                    </div>

                    {/* Expanded body */}
                    {isExpanded && (
                      <div style={{ padding: '1.25rem 1.5rem', borderTop: '1px solid rgba(255,255,255,0.03)', background: 'rgba(2,8,23,0.4)', animation: 'slideDown 0.25s ease-out' }}>

                        {/* Event details */}
                        <div style={{ marginBottom: '1.25rem' }}>
                          <h4 style={{ color: '#8b5cf6', fontWeight: 700, margin: '0 0 0.4rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Event Details</h4>
                          <div style={{ padding: '0.85rem 1rem', background: '#020b18', border: '1px solid rgba(255,255,255,0.03)', borderRadius: 8 }}>
                            <div style={{ display: 'grid', gap: '0.5rem' }}>
                              <div style={{ color: '#b9c7db', fontSize: '0.85rem' }}>
                                <strong style={{ color: '#a78bfa' }}>Start:</strong> {formatDateTime(appointment.event_start)}
                              </div>
                              <div style={{ color: '#b9c7db', fontSize: '0.85rem' }}>
                                <strong style={{ color: '#a78bfa' }}>End:</strong> {formatDateTime(appointment.event_end)}
                              </div>
                              <div style={{ color: '#b9c7db', fontSize: '0.85rem' }}>
                                <strong style={{ color: '#a78bfa' }}>Calendar Status:</strong>{' '}
                                <span style={{ color: badgeColor, fontWeight: 600 }}>
                                  {getAppointmentLabel(appointment.calendar_status)}
                                </span>
                                {isFailed && (
                                  <span style={{ display: 'inline-block', marginLeft: '0.5rem', fontSize: '0.7rem', color: '#ef4444', background: 'rgba(239,68,68,0.1)', padding: '2px 6px', borderRadius: 4 }}>
                                    Needs manual calendar setup
                                  </span>
                                )}
                              </div>
                              <div style={{ color: '#b9c7db', fontSize: '0.85rem' }}>
                                <strong style={{ color: '#a78bfa' }}>Confirmation Email:</strong>{' '}
                                <span style={{ color: confirmStatus.color, fontWeight: 600 }}>
                                  {confirmStatus.label}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Original email */}
                        <div style={{ marginBottom: '1.25rem' }}>
                          <h4 style={{ color: '#8b5cf6', fontWeight: 700, margin: '0 0 0.4rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Original Message</h4>
                          <div style={{ padding: '0.85rem 1rem', background: '#020b18', border: '1px solid rgba(255,255,255,0.03)', borderLeft: `2px solid ${badgeColor}`, borderRadius: 8 }}>
                            <div style={{ color: '#b9c7db', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                              <strong style={{ color: '#a78bfa' }}>Subject:</strong> {appointment.subject}
                            </div>
                            <div style={{ color: '#b9c7db', fontSize: '0.85rem', lineHeight: 1.65, whiteSpace: 'pre-wrap' }}>
                              {appointment.body}
                            </div>
                          </div>
                        </div>

                        {/* Delete button only */}
                        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                          <button
                            onClick={() => handleDeleteAppointment(appointment)}
                            disabled={deletingId === appointment.email_db_id}
                            style={{ padding: '0.45rem 1rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, color: '#f87171', cursor: deletingId === appointment.email_db_id ? 'not-allowed' : 'pointer', fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.01em', fontFamily: 'inherit', transition: 'all 0.2s' }}
                            onMouseEnter={e => { if (deletingId !== appointment.email_db_id) { e.currentTarget.style.background = '#ef4444'; e.currentTarget.style.color = '#fff' } }}
                            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.06)'; e.currentTarget.style.color = '#f87171' }}
                          >
                            {deletingId === appointment.email_db_id ? 'Deleting...' : 'Delete'}
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