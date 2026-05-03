import styles from './ScoreBreakdown.module.css'

export default function ScoreBreakdown({ breakdown }) {
  return (
    <div className={styles.table}>
      <div className={styles.header}>
        <span>Signal</span>
        <span>Score</span>
        <span>Détail</span>
      </div>
      {breakdown.map((row, i) => {
        const cls = row.score > 0 ? styles.pos : row.score < 0 ? styles.neg : styles.neu
        return (
          <div key={i} className={`${styles.row} ${cls}`}>
            <span className={styles.signal}>{row.signal}</span>
            <span className={styles.scoreVal}>
              {row.score > 0 ? `+${row.score}` : row.score}
            </span>
            <span className={styles.label}>{row.label}</span>
          </div>
        )
      })}
    </div>
  )
}
