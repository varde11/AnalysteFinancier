import styles from './Badge.module.css'

const DECISION_CONFIG = {
  BUY:  { label: '▲ BUY',  cls: 'buy'  },
  SELL: { label: '▼ SELL', cls: 'sell' },
  HOLD: { label: '◆ HOLD', cls: 'hold' },
}

const CONFIDENCE_CONFIG = {
  HIGH:   { cls: 'high'   },
  MEDIUM: { cls: 'medium' },
  LOW:    { cls: 'low'    },
}

export function DecisionBadge({ decision, large = false }) {
  const cfg = DECISION_CONFIG[decision] || DECISION_CONFIG.HOLD
  return (
    <span className={`${styles.badge} ${styles[cfg.cls]} ${large ? styles.large : ''}`}>
      {cfg.label}
    </span>
  )
}

export function ConfidenceBadge({ confidence }) {
  const cfg = CONFIDENCE_CONFIG[confidence] || CONFIDENCE_CONFIG.LOW
  return (
    <span className={`${styles.confBadge} ${styles[cfg.cls]}`}>
      {confidence}
    </span>
  )
}
