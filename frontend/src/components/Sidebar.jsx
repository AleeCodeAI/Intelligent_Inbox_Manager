import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Home, AlertCircle, Flame, Archive, BarChart2, Inbox, ChevronLeft, Menu, Mail, Send } from 'lucide-react'
import { Calendar, PlayCircle, MailCheck } from 'lucide-react'

const links = [
  { to: '/',                  label: 'Home',              icon: Home         },
  { to: '/basic',             label: 'Basic Emails',      icon: AlertCircle  },
  { to: '/priority',          label: 'Priority',          icon: Flame        },
  { to: '/non-business',      label: 'Non-Business',      icon: Archive      },
  { to: '/analysis',          label: 'Analysis',          icon: BarChart2    },
  { to: '/appointments',      label: 'Appointments',      icon: Calendar     },
  { to: '/executor',          label: 'Executor',          icon: PlayCircle   },
  { to: '/emails',            label: 'Emails',            icon: Mail         },
  { to: '/processed-emails',  label: 'Processed Emails',  icon: MailCheck    },
]

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(true)

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          top: '24px',
          left: '24px',
          zIndex: 1000,
          background: 'rgba(2,11,24,0.95)',
          border: '1px solid rgba(59,130,246,0.3)',
          borderRadius: '12px',
          padding: '10px',
          cursor: 'pointer',
          color: '#60a5fa',
          backdropFilter: 'blur(8px)',
          transition: 'all 0.25s ease',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = '#0a1a2f'
          e.currentTarget.style.borderColor = '#60a5fa'
          e.currentTarget.style.transform = 'scale(1.05)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'rgba(2,11,24,0.95)'
          e.currentTarget.style.borderColor = 'rgba(59,130,246,0.3)'
          e.currentTarget.style.transform = 'scale(1)'
        }}
      >
        <Menu size={20} />
      </button>
    )
  }

  return (
    <>
      {/* Overlay */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(4px)',
        zIndex: 998,
        animation: 'fadeIn 0.25s ease',
      }} onClick={() => setIsOpen(false)} />

      <aside style={{
        position: 'fixed', top: 0, left: 0,
        width: '280px', height: '100vh',
        background: 'linear-gradient(180deg, #071425 0%, #030a15 100%)',
        borderRight: '1px solid rgba(59,130,246,0.15)',
        display: 'flex', flexDirection: 'column',
        padding: '1.75rem 1.25rem',
        zIndex: 999,
        animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        boxShadow: '8px 0 32px rgba(0,0,0,0.6)',
      }}>

        {/* Animated gradient border top */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(90deg, #1e3a5f, #3b82f6, #60a5fa, #1e3a5f)',
          backgroundSize: '200% 100%',
          animation: 'gradientMove 4s linear infinite',
        }} />

        {/* Header with close button - cleaner design */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          marginBottom: '2.5rem',
          padding: '0 0.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ position: 'relative' }}>
              <Inbox size={26} color="#3b82f6" />
              <div style={{
                position: 'absolute',
                bottom: -2,
                right: -2,
                width: 8,
                height: 8,
                background: '#3b82f6',
                borderRadius: '50%',
                animation: 'pulse 2s ease infinite',
              }} />
            </div>
            <span style={{ 
              fontFamily: 'Syne', 
              fontWeight: 700, 
              fontSize: '1.15rem', 
              letterSpacing: '-0.01em',
              background: 'linear-gradient(135deg, #e2e8f0, #94a3b8)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
            }}>
              Inbox Manager
            </span>
          </div>
          
          {/* Clean close button - chevron left */}
          <button
            onClick={() => setIsOpen(false)}
            style={{
              background: 'rgba(59,130,246,0.08)',
              border: 'none',
              borderRadius: '8px',
              padding: '6px',
              cursor: 'pointer',
              color: '#64748b',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'rgba(59,130,246,0.2)'
              e.currentTarget.style.color = '#60a5fa'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'rgba(59,130,246,0.08)'
              e.currentTarget.style.color = '#64748b'
            }}
          >
            <ChevronLeft size={18} />
          </button>
        </div>

        {/* Animated floating mail icons */}
        <div style={{ position: 'absolute', bottom: '15%', right: '12px', opacity: 0.25, pointerEvents: 'none' }}>
          <Mail size={28} style={{ animation: 'float1 5s ease-in-out infinite' }} color="#3b82f6" />
          <Send size={20} style={{ animation: 'float2 6s ease-in-out infinite', marginTop: '12px', marginLeft: '10px' }} color="#60a5fa" />
        </div>

        {/* Navigation */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '0.875rem',
              padding: '0.75rem 1rem', borderRadius: '12px',
              textDecoration: 'none',
              fontFamily: 'DM Sans', fontSize: '0.9rem', fontWeight: 500,
              color: isActive ? '#e2e8f0' : '#5c6b8a',
              background: isActive ? 'rgba(59,130,246,0.12)' : 'transparent',
              borderLeft: isActive ? '3px solid #3b82f6' : '3px solid transparent',
              transition: 'all 0.2s ease',
            })}>
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom status */}
        <div style={{
          marginTop: 'auto',
          paddingTop: '1.5rem',
          borderTop: '1px solid rgba(59,130,246,0.1)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            fontSize: '0.7rem',
            color: '#3b6e9e',
          }}>
            <div style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#3b82f6',
              animation: 'pulse 1.5s ease infinite',
            }} />
            <span>AI Pipeline • Active</span>
          </div>
        </div>
      </aside>

      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(-100%);
          }
          to {
            transform: translateX(0);
          }
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.3);
          }
        }
        
        @keyframes gradientMove {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        
        @keyframes float1 {
          0%, 100% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-12px) rotate(5deg);
          }
        }
        
        @keyframes float2 {
          0%, 100% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-8px) rotate(-3deg);
          }
        }
      `}</style>
    </>
  )
}