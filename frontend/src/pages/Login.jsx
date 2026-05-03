import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../services/api'
import { useAuth } from '../context/AuthContext'
import styles from './Login.module.css'

export default function Login() {
  const { saveToken } = useAuth()
  const navigate = useNavigate()

  const [id_client, setId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (id_client.length < 3) {
      setError("L'ID client doit contenir au moins 3 caractères.")
      return
    }

    setLoading(true)
    try {
      const data = await login(id_client, password)   // string, pas Number
      saveToken(data.access_token)
      navigate('/dashboard')
    } catch (err) {
      // Messages d'erreur personnalisés selon le code HTTP
      if (err.message.includes('401') || err.message.toLowerCase().includes('identifiant')) {
        setError('ID ou mot de passe incorrect.')
      } else if (err.message.includes('404')) {
        setError('Aucun compte trouvé avec cet ID.')
      } else {
        setError('Erreur de connexion. Vérifie que le serveur est actif.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      {/* Grille déco en fond */}
      <div className={styles.grid} aria-hidden />

      <div className={styles.card}>
        <div className={styles.header}>
          <span className={styles.logoMark}>▲</span>
          <h1 className={styles.title}>SIGNAL</h1>
          <p className={styles.subtitle}>Plateforme d'analyse boursière IA</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>ID Client</label>
            <input
              className={styles.input}
              type="text"
              placeholder="min. 3 caractères"
              value={id_client}
              onChange={e => setId(e.target.value)}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Mot de passe</label>
            <input
              className={styles.input}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className={styles.error}>⚠ {error}</p>}

          <button className={styles.btn} disabled={loading}>
            {loading ? 'Connexion...' : 'Se connecter →'}
          </button>

          <p className={styles.switchLink}>
            Pas encore de compte ?{' '}
            <Link to="/register">Créer un compte</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
