import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import styles from './Sidebar.module.css'

const NAV = [
  { to: '/dashboard',   icon: '▦',  label: 'Dashboard'    },
  { to: '/predict',     icon: '◎',  label: 'Analyser'     },
  { to: '/history',     icon: '≡',  label: 'Historique'   },
]

export default function Sidebar() {
  const { client, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <aside className={styles.sidebar}>
      {/* Logo */}
      <div className={styles.logo}>
        <span className={styles.logoMark}>▲</span>
        <span className={styles.logoText}>SIGNAL</span>
      </div>

      {/* Nav links */}
      <nav className={styles.nav}>
        {NAV.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.active : ''}`
            }
          >
            <span className={styles.icon}>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer — profil + logout */}
      <div className={styles.footer}>
        {client && (
          <div className={styles.profile}>
            <div className={styles.avatar}>
              {client.nom?.charAt(0).toUpperCase()}
            </div>
            <div className={styles.profileInfo}>
              <span className={styles.profileName}>{client.nom}</span>
              <span className={styles.profileId}>#{client.id_client}</span>
            </div>
          </div>
        )}
        <button className={styles.logout} onClick={handleLogout}>
          ⎋ Déconnexion
        </button>
      </div>
    </aside>
  )
}
