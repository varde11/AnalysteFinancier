import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import styles from './Login.module.css' // réutilise le même style que Login
import { register } from '../services/api'

export default function Register() {
  const navigate = useNavigate()

  const [form, setForm]       = useState({ id_client: '', nom: '', password: '', confirm: '' })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (form.id_client.length < 3) {
      setError("L'ID client doit contenir au moins 3 caractères (ex: 001, usr).")
      return
    }
    if (form.nom.length < 3) {
      setError('Le nom doit contenir au moins 3 caractères.')
      return
    }
    if (form.password.length < 3) {
      setError('Le mot de passe doit contenir au moins 3 caractères.')
      return
    }
    if (form.password !== form.confirm) {
      setError('Les mots de passe ne correspondent pas.')
      return
    }

    setLoading(true)
    try {
      await register(form.id_client, form.nom, form.password)
      navigate('/login', { state: { registered: true } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.grid} aria-hidden />

      <div className={styles.card}>
        <div className={styles.header}>
          <span className={styles.logoMark}>▲</span>
          <h1 className={styles.title}>SIGNAL</h1>
          <p className={styles.subtitle}>Créer un compte</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>ID Client</label>
            <input
              className={styles.input}
              type="text"
              name="id_client"
              placeholder="min. 3 caractères (ex: 001)"
              value={form.id_client}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Nom</label>
            <input
              className={styles.input}
              type="text"
              name="nom"
              placeholder="Votre nom"
              value={form.nom}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Mot de passe</label>
            <input
              className={styles.input}
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Confirmer le mot de passe</label>
            <input
              className={styles.input}
              type="password"
              name="confirm"
              placeholder="••••••••"
              value={form.confirm}
              onChange={handleChange}
              required
            />
          </div>

          {error && <p className={styles.error}>⚠ {error}</p>}

          <button className={styles.btn} disabled={loading}>
            {loading ? 'Création...' : 'Créer le compte →'}
          </button>

          <p className={styles.switchLink}>
            Déjà un compte ?{' '}
            <Link to="/login">Se connecter</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
