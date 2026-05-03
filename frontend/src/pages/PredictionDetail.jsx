import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip
} from 'recharts'
import { getPredictionById, deletePredictionById } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { DecisionBadge, ConfidenceBadge } from '../components/ui/Badge'
import ScoreBar from '../components/prediction/ScoreBar'
import ScoreBreakdown from '../components/prediction/ScoreBreakdown'
import styles from './PredictionDetail.module.css'

function toRadarData(breakdown) {
  return breakdown.map(row => ({
    subject: row.signal,
    value: Math.round(((row.score + 2) / 4) * 100),
  }))
}

function fmt(val) {
  if (val == null) return '—'
  return typeof val === 'number'
    ? val.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : val
}

export default function PredictionDetail() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()

  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState('')
  const [deleting, setDeleting]     = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  useEffect(() => {
    getPredictionById(id, token)
      .then(setPrediction)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, token])

  async function handleDelete() {
    if (!confirmDelete) { setConfirmDelete(true); return }
    setDeleting(true)
    try {
      await deletePredictionById(id, token)
      navigate(-1)
    } catch (e) {
      setError(e.message)
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  if (loading) return <p className={styles.msg}>Chargement...</p>
  if (error)   return <p className={styles.msg} style={{ color: 'var(--red)' }}>Erreur : {error}</p>
  if (!prediction) return null

  const rd        = prediction.report_detail || {}
  const tech      = rd.technicals || {}
  const news      = rd.news_summary || {}
  const breakdown = rd.score_breakdown || []
  const radarData = toRadarData(breakdown)

  const scoreColor = rd.total_score >= 3 ? 'var(--green)'
                   : rd.total_score <= -3 ? 'var(--red)'
                   : 'var(--blue)'

  return (
    <div className={styles.page}>
      {/* Header avec bouton supprimer */}
      <div className={styles.topBar}>
        <button className={styles.back} onClick={() => navigate(-1)}>← Retour</button>
        <button
          className={`${styles.deleteBtn} ${confirmDelete ? styles.deleteBtnConfirm : ''}`}
          onClick={handleDelete}
          disabled={deleting}
        >
          {deleting ? 'Suppression...' : confirmDelete ? '⚠ Confirmer la suppression' : '🗑 Supprimer'}
        </button>
      </div>

      {confirmDelete && !deleting && (
        <p className={styles.deleteHint}>
          Clique à nouveau sur le bouton pour confirmer.{' '}
          <button className={styles.cancelBtn} onClick={() => setConfirmDelete(false)}>Annuler</button>
        </p>
      )}

      {/* Header ticker + décision */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.ticker}>{prediction.ticket}</span>
          <span className={styles.timestamp}>
            {new Date(prediction.time_stamp).toLocaleString('fr-FR')}
          </span>
        </div>
        <DecisionBadge decision={prediction.decision} large />
      </div>

      {/* Score bar */}
      <ScoreBar score={rd.total_score ?? 0} />

      {/* Explication */}
      <div className={styles.explanation}>
        <span className={styles.expIcon} style={{ color: scoreColor }}>◈</span>
        <p>{rd.explanation || prediction.reasoning}</p>
      </div>

      {/* Grille principale */}
      <div className={styles.mainGrid}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Indicateurs techniques</h2>
          <div className={styles.techGrid}>
            <TechRow label="Prix actuel"  value={`$${fmt(tech.current_price)}`} />
            <TechRow label="RSI (14j)"    value={fmt(tech.rsi)}
              hint={tech.rsi < 30 ? 'Survendue' : tech.rsi > 70 ? 'Surachetée' : 'Neutre'}
              hintColor={tech.rsi < 30 ? 'var(--green)' : tech.rsi > 70 ? 'var(--red)' : 'var(--text-secondary)'}
            />
            <TechRow label="SMA 50"  value={`$${fmt(tech.sma50)}`} />
            <TechRow label="SMA 200" value={`$${fmt(tech.sma200)}`} />
            <TechRow
              label="Tendance"
              value={tech.golden_cross ? 'Golden Cross ✓' : 'Death Cross ✗'}
              valueColor={tech.golden_cross ? 'var(--green)' : 'var(--red)'}
            />
            <TechRow
              label="Prix vs SMA50"
              value={tech.price_above_sma50 ? 'Au-dessus' : 'En dessous'}
              valueColor={tech.price_above_sma50 ? 'var(--green)' : 'var(--text-secondary)'}
            />
          </div>
        </div>

        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Empreinte des signaux</h2>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              />
              <Radar dataKey="value" stroke={scoreColor} fill={scoreColor}
                fillOpacity={0.15} strokeWidth={2} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                formatter={v => [`${v}/100`, 'Score normalisé']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className={styles.card}>
        <h2 className={styles.cardTitle}>Détail du scoring</h2>
        <ScoreBreakdown breakdown={breakdown} />
      </div>

      <div className={styles.card}>
        <div className={styles.newsHeader}>
          <h2 className={styles.cardTitle} style={{ margin: 0 }}>Actualités analysées</h2>
          <span className={styles.sentiment} style={{
            color: news.sentiment === 'POSITIVE' ? 'var(--green)'
                 : news.sentiment === 'NEGATIVE' ? 'var(--red)'
                 : 'var(--text-secondary)'
          }}>
            {news.sentiment}
          </span>
        </div>
        <div className={styles.newsList}>
          {(news.items || []).length === 0 ? (
            <p className={styles.noNews}>Aucune actualité vérifiable trouvée.</p>
          ) : (
            (news.items || []).map((item, i) => (
              <div key={i} className={styles.newsItem}>
                <div className={styles.newsTop}>
                  <ConfidenceBadge confidence={item.confidence} />
                </div>
                <p className={styles.claim}>{item.claim}</p>
                <p className={styles.evidence}>{item.evidence}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function TechRow({ label, value, hint, hintColor, valueColor }) {
  return (
    <div className={styles.techRow}>
      <span className={styles.techLabel}>{label}</span>
      <div className={styles.techRight}>
        <span className={styles.techValue} style={{ color: valueColor }}>{value}</span>
        {hint && <span className={styles.techHint} style={{ color: hintColor }}>{hint}</span>}
      </div>
    </div>
  )
}