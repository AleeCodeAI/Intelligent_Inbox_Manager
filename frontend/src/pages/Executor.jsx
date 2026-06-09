import { useState } from 'react'
import emailService from '../services/emailService'

const LEFT_LINES = [
  '{ "executor": "master_pipeline",',
  '  "status": "idle",',
  '  "emails_processed": 0,',
  '  "last_run": null,',
  '}',
  'async function runExecutor() {',
  '  const result = await',
  '    pipeline.process();',
  '  return result.data;',
  '}',
]

const RIGHT_LINES = [
  'executor.process({',
  '  batch_size: 50,',
  '  rag_enabled: true,',
  '  fallback: "database",',
  '  confidence_threshold: 0.85,',
  '  classification_model: "groq/llama",',
  '  observe: "langfuse",',
  '})',
  '.then(results => {',
  '  emit("completed", results);',
  '  updateDashboard(results);',
  '})',
]

export default function Executor() {
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [notification, setNotification] = useState(null)

  const showNotification = (type, message) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 5000)
  }

  const getClassificationColor = (classification) => {
    switch(classification?.toUpperCase()) {
      case 'PRIORITY': return '#8b5cf6'
      case 'NON_BUSINESS': return '#10b981'
      case 'BASIC': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const getClassificationLabel = (classification) => {
    switch(classification?.toUpperCase()) {
      case 'PRIORITY': return 'Priority'
      case 'NON_BUSINESS': return 'Non-Business'
      case 'BASIC': return 'Basic'
      default: return classification || 'Unknown'
    }
  }

  const handleRunExecutor = async () => {
    setIsRunning(true)
    setResult(null)
    
    try {
      const response = await emailService.runExecutor()
      
      if (response.status === 'success') {
        setResult(response)
        showNotification('success', `Executor completed! Processed ${response.processed_count} email(s).`)
      }
    } catch (error) {
      showNotification('error', 'Failed to run executor: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsRunning(false)
    }
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

      {/* Page content */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: 860, margin: '0 auto', padding: '3.5rem 2rem 4rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: '2.5rem', gap: '0.35rem' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 20, padding: '4px 14px', marginBottom: '0.5rem' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#8b5cf6', display: 'inline-block' }} />
            <span style={{ fontSize: 11, color: '#8b5cf6', letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 600 }}>Pipeline Controller</span>
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
            Executor
          </h1>
          
          <p style={{ color: '#5a7fb5', fontSize: '0.75rem', margin: 0, letterSpacing: '0.12em', textTransform: 'uppercase', fontWeight: 500, opacity: 0.8 }}>
            Master pipeline execution engine
          </p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginTop: '0.75rem' }}>
            <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
            <span style={{ fontSize: '0.72rem', color: '#5a7fb5', letterSpacing: '0.05em', fontWeight: 500 }}>
              Process unprocessed emails through AI pipeline
            </span>
            <div style={{ width: 40, height: 1, background: 'rgba(139,92,246,0.2)' }} />
          </div>
        </div>

        {/* Card container */}
        <div style={{ background: 'rgba(6,18,36,0.85)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: 16, padding: '1.75rem 1.5rem', backdropFilter: 'blur(12px)' }}>

          {/* Executor button */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: result ? '2rem' : 0 }}>
            <button
              onClick={handleRunExecutor}
              disabled={isRunning}
              style={{
                padding: '0.875rem 2rem',
                background: isRunning ? 'rgba(139,92,246,0.3)' : '#7c3aed',
                border: 'none',
                borderRadius: 12,
                color: '#fff',
                cursor: isRunning ? 'not-allowed' : 'pointer',
                fontSize: '0.875rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                fontFamily: 'inherit',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                opacity: isRunning ? 0.6 : 1
              }}
              onMouseEnter={e => {
                if (!isRunning) {
                  e.currentTarget.style.background = '#6d28d9'
                  e.currentTarget.style.transform = 'translateY(-1px)'
                }
              }}
              onMouseLeave={e => {
                if (!isRunning) {
                  e.currentTarget.style.background = '#7c3aed'
                  e.currentTarget.style.transform = 'translateY(0)'
                }
              }}
            >
              {isRunning ? (
                <>
                  <div style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                  Processing...
                </>
              ) : (
                <>
                  ▶ Execute Pipeline
                </>
              )}
            </button>
          </div>

          {/* Results section */}
          {result && (
            <div style={{ marginTop: '2rem', animation: 'slideDown 0.3s ease-out' }}>
              <div style={{ 
                padding: '1rem 1.25rem', 
                background: 'rgba(16,185,129,0.05)', 
                border: '1px solid rgba(16,185,129,0.15)', 
                borderRadius: 12,
                marginBottom: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span style={{ color: '#10b981', fontWeight: 600, fontSize: '0.875rem' }}>
                    ✓ Execution completed successfully
                  </span>
                  <span style={{ color: '#a78bfa', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#b9c7db' }}>
                  Processed <strong style={{ color: '#a78bfa' }}>{result.processed_count}</strong> email{result.processed_count !== 1 ? 's' : ''}
                </div>
              </div>

              <h4 style={{ color: '#8b5cf6', fontWeight: 700, margin: '0 0 1rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Classification Results
              </h4>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {result.results.map((item, index) => {
                  const classificationColor = getClassificationColor(item.classification)
                  const isSuccess = item.success
                  
                  return (
                    <div
                      key={item.gmail_id || index}
                      style={{ 
                        background: '#0a1424', 
                        border: '1px solid rgba(255,255,255,0.03)',
                        borderRadius: 10, 
                        padding: '0.875rem 1rem',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                          <span style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: '#5a7fb5' }}>
                            {item.gmail_id?.slice(-12) || 'N/A'}
                          </span>
                          <span style={{ 
                            fontSize: 10, 
                            background: `${classificationColor}12`, 
                            border: `1px solid ${classificationColor}33`, 
                            color: classificationColor, 
                            padding: '4px 10px', 
                            borderRadius: 6, 
                            letterSpacing: '0.06em', 
                            fontWeight: 600 
                          }}>
                            {getClassificationLabel(item.classification)}
                          </span>
                        </div>
                        <span style={{ 
                          fontSize: 10, 
                          background: isSuccess ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)', 
                          border: `1px solid ${isSuccess ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`, 
                          color: isSuccess ? '#10b981' : '#ef4444', 
                          padding: '4px 10px', 
                          borderRadius: 6, 
                          letterSpacing: '0.06em', 
                          fontWeight: 600 
                        }}>
                          {isSuccess ? 'Success' : 'Failed'}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Idle state hint */}
          {!result && !isRunning && (
            <div style={{ 
              textAlign: 'center', 
              padding: '3rem 2rem', 
              color: '#5a7fb5', 
              fontSize: '0.8rem',
              border: '1px dashed rgba(139,92,246,0.15)',
              borderRadius: 12,
              marginTop: '1rem'
            }}>
              Click the button above to run the master pipeline executor.
              <br />
              Unprocessed emails will be fetched and classified automatically.
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