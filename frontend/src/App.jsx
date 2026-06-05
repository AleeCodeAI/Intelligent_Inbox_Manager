import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import BasicEmails from './pages/BasicEmails'
import PriorityEmails from './pages/PriorityEmails'
import NonBusinessEmails from './pages/NonBusinessEmails'
import Analysis from './pages/Analysis'

function DashboardLayout({ children }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ flex: 1, padding: '2rem', marginLeft: '240px' }}>
        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"             element={<Home />} />
        <Route path="/basic"        element={<DashboardLayout><BasicEmails /></DashboardLayout>} />
        <Route path="/priority"     element={<DashboardLayout><PriorityEmails /></DashboardLayout>} />
        <Route path="/non-business" element={<DashboardLayout><NonBusinessEmails /></DashboardLayout>} />
        <Route path="/analysis"     element={<DashboardLayout><Analysis /></DashboardLayout>} />
      </Routes>
    </BrowserRouter>
  )
}