import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/layout/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'

import Login            from './pages/Login'
import Register         from './pages/Register'
import Dashboard        from './pages/Dashboard'
import NewPrediction    from './pages/NewPrediction'
import History          from './pages/History'
import PredictionDetail from './pages/PredictionDetail'

// Layout wrapper qui combine ProtectedRoute + AppLayout + Outlet
function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <Outlet />   {/* React Router injecte ici la page active */}
      </AppLayout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protégé — toutes les pages enfants partagent le layout */}
          <Route element={<ProtectedLayout />}>
            <Route path="/"                  element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard"         element={<Dashboard />} />
            <Route path="/predict"           element={<NewPrediction />} />
            <Route path="/history"           element={<History />} />
            <Route path="/prediction/:id"    element={<PredictionDetail />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
