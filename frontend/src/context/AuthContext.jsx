import { createContext, useContext, useState, useEffect } from 'react'
import { getMe } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => localStorage.getItem('token'))
  const [client, setClient] = useState(null)
  const [loading, setLoading] = useState(!!localStorage.getItem('token'))

  // Au montage, si token présent → récupère le profil client
  useEffect(() => {
    if (!token) { setLoading(false); return }
    getMe(token)
      .then(setClient)
      .catch(() => { localStorage.removeItem('token'); setToken(null) })
      .finally(() => setLoading(false))
  }, [token])

  function saveToken(t) {
    localStorage.setItem('token', t)
    setToken(t)
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
    setClient(null)
  }

  return (
    <AuthContext.Provider value={{ token, client, loading, saveToken, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook raccourci
export function useAuth() {
  return useContext(AuthContext)
}
