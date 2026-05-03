import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100vh', color:'var(--text-secondary)', fontFamily:'var(--font-mono)' }}>
        Chargement...
      </div>
    )
  }

  return token ? children : <Navigate to="/login" replace />
}
