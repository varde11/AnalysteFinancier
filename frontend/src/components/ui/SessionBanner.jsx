import styles from './SessionBanner.module.css'

export default function SessionBanner() {
  return (
    <div className={styles.banner}>
      <span className={styles.icon}>⏱</span>
      <span>Session expirée. Veuillez actualiser la page pour vous reconnecter.</span>
      <button className={styles.btn} onClick={() => window.location.reload()}>
        Actualiser
      </button>
    </div>
  )
}
