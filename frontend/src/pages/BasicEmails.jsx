import { useState, useEffect } from 'react'
import emailService from '../services/emailService'

export default function BasicEmails() {
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [manualResponses, setManualResponses] = useState({})
  const [notification, setNotification] = useState(null)
  const [sendingId, setSendingId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    fetchEmails()
  }, [])

  const fetchEmails = async () => {
    setLoading(true)
    try {
      const response = await emailService.getPendingEmails()
      if (response.status === 'success') {
        setEmails(response.data)
        const initialResponses = {}
        response.data.forEach(email => {
          initialResponses[email.email_db_id] = ''
        })
        setManualResponses(initialResponses)
      }
    } catch (error) {
      showNotification('error', 'Failed to fetch emails: ' + (error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  const showNotification = (type, message) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 5000)
  }

  const handleSendResponse = async (email) => {
    setSendingId(email.email_db_id)
    try {
      await emailService.sendManualResponse(
        email.gmail_id,
        email.sender_name,
        manualResponses[email.email_db_id]
      )
      
      showNotification('success', `Response sent to ${email.sender_name} successfully!`)
      setTimeout(() => fetchEmails(), 1000)
    } catch (error) {
      showNotification('error', 'Failed to send response: ' + (error.response?.data?.message || error.message))
    } finally {
      setSendingId(null)
    }
  }

  const handleDeleteEmail = async (email) => {
    if (!window.confirm(`Are you sure you want to delete email from ${email.sender_name}?`)) {
      return
    }
    
    setDeletingId(email.email_db_id)
    try {
      await emailService.deleteEmail(email.gmail_id)
      
      showNotification('success', `Email from ${email.sender_name} deleted successfully!`)
      setEmails(prev => prev.filter(e => e.email_db_id !== email.email_db_id))
      setExpandedId(null)
    } catch (error) {
      showNotification('error', 'Failed to delete email: ' + (error.response?.data?.message || error.message))
    } finally {
      setDeletingId(null)
    }
  }

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const updateManualResponse = (id, value) => {
    setManualResponses(prev => ({ ...prev, [id]: value }))
  }

  if (loading) {
    return (
      <div style={{
        padding: '2rem',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(59,130,246,0.2)',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }} />
          <p style={{ color: '#94a3b8', marginTop: '1rem' }}>Loading pending emails...</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      padding: '2rem',
      maxWidth: '1200px',
      margin: '0 auto',
      position: 'relative',
      minHeight: '100vh',
      background: '#020b18',
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '2rem',
      }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 700,
          fontFamily: "'Syne', sans-serif",
          background: 'linear-gradient(135deg, #ffffff, #60a5fa)',
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          marginBottom: '0.5rem',
        }}>
          Basic Emails
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
          Emails that failed to be automatically responded by the RAG system
        </p>
        <p style={{ color: '#475569', fontSize: '0.85rem' }}>
          {emails.length} email{emails.length !== 1 ? 's' : ''} require manual attention
        </p>
      </div>

      {/* Refresh Button */}
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        marginBottom: '1.5rem',
      }}>
        <button
          onClick={fetchEmails}
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(59,130,246,0.1)',
            border: '1px solid rgba(59,130,246,0.3)',
            borderRadius: '8px',
            color: '#60a5fa',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontSize: '0.85rem',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(59,130,246,0.2)'
            e.currentTarget.style.boxShadow = '0 0 10px rgba(59,130,246,0.3)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'rgba(59,130,246,0.1)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          Refresh
        </button>
      </div>

      {/* Notification */}
      {notification && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 1000,
          padding: '0.75rem 1.5rem',
          background: notification.type === 'success' ? 'rgba(16,185,129,0.95)' : 'rgba(239,68,68,0.95)',
          borderRadius: '8px',
          color: '#fff',
          fontSize: '0.875rem',
          backdropFilter: 'blur(8px)',
          animation: 'slideInRight 0.3s ease',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        }}>
          {notification.message}
        </div>
      )}

      {/* Email List */}
      {emails.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '4rem',
          background: 'rgba(15,25,45,0.6)',
          borderRadius: '12px',
          border: '1px solid rgba(59,130,246,0.2)',
          backdropFilter: 'blur(4px)',
        }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '1rem',
          }}>✓</div>
          <h3 style={{ color: '#e2e8f0', marginBottom: '0.5rem' }}>All caught up!</h3>
          <p style={{ color: '#64748b' }}>No emails are waiting for manual response.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {emails.map((email) => (
            <div
              key={email.email_db_id}
              style={{
                background: 'rgba(10,20,35,0.8)',
                border: `1px solid ${expandedId === email.email_db_id ? 'rgba(59,130,246,0.5)' : 'rgba(59,130,246,0.15)'}`,
                borderRadius: '12px',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(4px)',
                boxShadow: expandedId === email.email_db_id ? '0 0 20px rgba(59,130,246,0.15)' : 'none',
              }}
            >
              {/* Email Header */}
              <div
                onClick={() => toggleExpand(email.email_db_id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '1.25rem 1.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(59,130,246,0.05)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: 600,
                    color: '#e2e8f0',
                    fontSize: '1rem',
                    marginBottom: '0.5rem',
                  }}>
                    {email.subject}
                  </div>
                  <div style={{
                    display: 'flex',
                    gap: '1rem',
                    fontSize: '0.8rem',
                    color: '#64748b',
                  }}>
                    <span>From: {email.sender_name}</span>
                    <span>{email.sender_email}</span>
                  </div>
                </div>
                <div style={{
                  fontSize: '1.5rem',
                  color: '#64748b',
                  transition: 'transform 0.2s ease',
                  transform: expandedId === email.email_db_id ? 'rotate(180deg)' : 'rotate(0deg)',
                }}>
                  ▼
                </div>
              </div>

              {/* Expanded Content */}
              {expandedId === email.email_db_id && (
                <div style={{
                  padding: '1.5rem',
                  borderTop: '1px solid rgba(59,130,246,0.1)',
                  animation: 'slideDown 0.3s ease',
                  background: 'rgba(5,12,22,0.5)',
                }}>
                  {/* Email Body */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{
                      color: '#94a3b8',
                      fontWeight: 600,
                      marginBottom: '0.75rem',
                      fontSize: '0.85rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}>Email Body</h3>
                    <div style={{
                      padding: '1rem',
                      background: 'rgba(2,11,24,0.6)',
                      borderRadius: '8px',
                      color: '#cbd5e1',
                      lineHeight: 1.6,
                      whiteSpace: 'pre-wrap',
                      fontSize: '0.9rem',
                    }}>
                      {email.body}
                    </div>
                  </div>

                  {/* AI Response */}
                  {email.rag_answer && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h3 style={{
                        color: '#94a3b8',
                        fontWeight: 600,
                        marginBottom: '0.75rem',
                        fontSize: '0.85rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}>AI Suggested Response</h3>
                      <div style={{
                        padding: '1rem',
                        background: 'rgba(167,139,250,0.08)',
                        borderRadius: '8px',
                        borderLeft: '3px solid #a78bfa',
                        color: '#c4b5fd',
                        lineHeight: 1.6,
                        fontSize: '0.9rem',
                      }}>
                        {email.rag_answer}
                        {email.failure_reason && (
                          <div style={{
                            marginTop: '0.75rem',
                            paddingTop: '0.75rem',
                            borderTop: '1px solid rgba(167,139,250,0.2)',
                            fontSize: '0.75rem',
                            color: '#f87171',
                          }}>
                            Note: {email.failure_reason}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Manual Response */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{
                      color: '#94a3b8',
                      fontWeight: 600,
                      marginBottom: '0.75rem',
                      fontSize: '0.85rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}>Your Response</h3>
                    <textarea
                      value={manualResponses[email.email_db_id] || ''}
                      onChange={(e) => updateManualResponse(email.email_db_id, e.target.value)}
                      placeholder="Write your response here..."
                      rows={5}
                      style={{
                        width: '100%',
                        padding: '1rem',
                        background: 'rgba(2,11,24,0.6)',
                        border: '1px solid rgba(59,130,246,0.2)',
                        borderRadius: '8px',
                        color: '#e2e8f0',
                        fontSize: '0.9rem',
                        lineHeight: 1.6,
                        fontFamily: 'inherit',
                        resize: 'vertical',
                        transition: 'all 0.2s ease',
                      }}
                      onFocus={e => {
                        e.currentTarget.style.borderColor = 'rgba(59,130,246,0.5)'
                        e.currentTarget.style.boxShadow = '0 0 10px rgba(59,130,246,0.2)'
                      }}
                      onBlur={e => {
                        e.currentTarget.style.borderColor = 'rgba(59,130,246,0.2)'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    />
                  </div>

                  {/* Action Buttons */}
                  <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                    <button
                      onClick={() => handleDeleteEmail(email)}
                      disabled={deletingId === email.email_db_id}
                      style={{
                        padding: '0.6rem 1.2rem',
                        background: 'rgba(239,68,68,0.15)',
                        border: '1px solid rgba(239,68,68,0.3)',
                        borderRadius: '8px',
                        color: '#f87171',
                        cursor: deletingId === email.email_db_id ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease',
                        fontSize: '0.85rem',
                        fontWeight: 500,
                      }}
                      onMouseEnter={e => {
                        if (deletingId !== email.email_db_id) {
                          e.currentTarget.style.background = 'rgba(239,68,68,0.25)'
                          e.currentTarget.style.boxShadow = '0 0 12px rgba(239,68,68,0.3)'
                        }
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.background = 'rgba(239,68,68,0.15)'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    >
                      {deletingId === email.email_db_id ? 'Deleting...' : 'Delete'}
                    </button>
                    <button
                      onClick={() => handleSendResponse(email)}
                      disabled={sendingId === email.email_db_id || !manualResponses[email.email_db_id]?.trim()}
                      style={{
                        padding: '0.6rem 1.5rem',
                        background: !manualResponses[email.email_db_id]?.trim() 
                          ? 'rgba(59,130,246,0.3)' 
                          : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff',
                        cursor: (!manualResponses[email.email_db_id]?.trim() || sendingId === email.email_db_id) 
                          ? 'not-allowed' 
                          : 'pointer',
                        transition: 'all 0.2s ease',
                        opacity: (!manualResponses[email.email_db_id]?.trim() || sendingId === email.email_db_id) ? 0.6 : 1,
                        fontSize: '0.85rem',
                        fontWeight: 500,
                        boxShadow: manualResponses[email.email_db_id]?.trim() ? '0 0 12px rgba(59,130,246,0.4)' : 'none',
                      }}
                      onMouseEnter={e => {
                        if (manualResponses[email.email_db_id]?.trim() && sendingId !== email.email_db_id) {
                          e.currentTarget.style.transform = 'translateY(-1px)'
                          e.currentTarget.style.boxShadow = '0 0 20px rgba(59,130,246,0.5)'
                        }
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.transform = 'translateY(0)'
                        if (manualResponses[email.email_db_id]?.trim()) {
                          e.currentTarget.style.boxShadow = '0 0 12px rgba(59,130,246,0.4)'
                        }
                      }}
                    >
                      {sendingId === email.email_db_id ? 'Sending...' : 'Send Response'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Keyframes */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  )
}