import styles from './ScoreBar.module.css'

export default function ScoreBar({ score, max = 6 }) {
  // Convertit le score (-6 à +6) en pourcentage (0% à 100%)
  const pct = ((score + max) / (max * 2)) * 100

  const color = score >= 3 ? 'var(--green)'
              : score <= -3 ? 'var(--red)'
              : 'var(--blue)'

  return (
    <div className={styles.wrapper}>
      <div className={styles.labels}>
        <span className={styles.neg}>−{max}</span>
        <span className={styles.score} style={{ color }}>
          {score > 0 ? `+${score}` : score} / {max}
        </span>
        <span className={styles.pos}>+{max}</span>
      </div>
      <div className={styles.track}>
        {/* Ligne centrale */}
        <div className={styles.center} />
        {/* Barre de score */}
        <div
          className={styles.fill}
          style={{
            width: `${Math.abs(score) / max * 50}%`,
            left: score >= 0 ? '50%' : `${pct}%`,
            background: color,
            boxShadow: `0 0 10px ${color}55`,
          }}
        />
      </div>
    </div>
  )
}
