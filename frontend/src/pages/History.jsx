import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer
} from 'recharts'
import { getPredictionsByClient, deletePredictionsByClient } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { DecisionBadge } from '../components/ui/Badge'
import SessionBanner from '../components/ui/SessionBanner'
import { useSessionExpired } from '../hooks/useSessionExpired'
import styles from './History.module.css'

const DECISION_COLOR = { BUY: '#22C55E', HOLD: '#3B82F6', SELL: '#EF4444' }

export default function History() {
  const { token } = useAuth()
  const navigate  = useNavigate()
  const { sessionExpired, callApi } = useSessionExpired()

  const [predictions, setPredictions] = useState([])
  const [selectedTicker, setSelectedTicker] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')
  const [confirmDeleteAll, setConfirmDeleteAll] = useState(false)
  const [deletingAll, setDeletingAll]           = useState(false)

  useEffect(() => {
    callApi(() => getPredictionsByClient(token))
      .then(data => {
        if (data) setPredictions([...data].sort((a, b) => new Date(a.time_stamp) - new Date(b.time_stamp)))
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])

  async function handleDeleteAll() {
    if (!confirmDeleteAll) { setConfirmDeleteAll(true); return }
    setDeletingAll(true)
    try {
      await deletePredictionsByClient(token)
      setPredictions([])
      setConfirmDeleteAll(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setDeletingAll(false)
    }
  }

  // Tickers uniques
  const tickers = ['ALL', ...new Set(predictions.map(p => p.ticket))]

  const filtered = selectedTicker === 'ALL'
    ? predictions
    : predictions.filter(p => p.ticket === selectedTicker)

  // Données pour le line chart
  const chartData = filtered.map(p => ({
    date: new Date(p.time_stamp).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }),
    score: p.report_detail?.total_score ?? 0,
    decision: p.decision,
    ticket: p.ticket,
    id: p.id_prediction,
  }))

  if (loading) return <p className={styles.msg}>Chargement...</p>
  if (error)   return <p className={styles.msg} style={{ color: 'var(--red)' }}>Erreur : {error}</p>

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Historique</h1>
        {predictions.length > 0 && (
          <div className={styles.deleteAllWrap}>
            {confirmDeleteAll && (
              <button className={styles.cancelBtn} onClick={() => setConfirmDeleteAll(false)}>
                Annuler
              </button>
            )}
            <button
              className={`${styles.deleteAllBtn} ${confirmDeleteAll ? styles.deleteAllConfirm : ''}`}
              onClick={handleDeleteAll}
              disabled={deletingAll}
            >
              {deletingAll ? 'Suppression...'
                : confirmDeleteAll ? '⚠ Confirmer — tout effacer'
                : '🗑 Tout supprimer'}
            </button>
          </div>
        )}
      </div>
      {sessionExpired && <SessionBanner />}

      {/* Filtre tickers */}
      <div className={styles.filters}>
        {tickers.map(t => (
          <button
            key={t}
            className={`${styles.filterBtn} ${selectedTicker === t ? styles.active : ''}`}
            onClick={() => setSelectedTicker(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className={styles.empty}>Aucune prédiction pour ce ticker.</div>
      ) : (
        <>
          {/* Line chart des scores */}
          {filtered.length > 1 && (
            <div className={styles.chartCard}>
              <h2 className={styles.cardTitle}>Évolution du score</h2>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 0, left: -20 }}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
                    axisLine={false} tickLine={false}
                  />
                  <YAxis
                    domain={[-6, 6]}
                    tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
                    axisLine={false} tickLine={false}
                  />
                  <ReferenceLine y={3}  stroke="var(--green)" strokeDasharray="4 3" strokeOpacity={0.4} />
                  <ReferenceLine y={0}  stroke="var(--border-strong)" />
                  <ReferenceLine y={-3} stroke="var(--red)"   strokeDasharray="4 3" strokeOpacity={0.4} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                    formatter={(v, _, props) => [`${v > 0 ? '+' : ''}${v} / 6`, props.payload.decision]}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="var(--blue)"
                    strokeWidth={2}
                    dot={{ fill: 'var(--bg-card)', stroke: 'var(--blue)', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Liste des prédictions */}
          <div className={styles.list}>
            {[...filtered].reverse().map(p => (
              <div
                key={p.id_prediction}
                className={styles.row}
                onClick={() => navigate(`/prediction/${p.id_prediction}`)}
              >
                <div className={styles.rowLeft}>
                  <span className={styles.rowTicker}>{p.ticket}</span>
                  <span className={styles.rowDate}>
                    {new Date(p.time_stamp).toLocaleString('fr-FR')}
                  </span>
                </div>

                <div className={styles.rowMid}>
                  <span className={styles.rowScore} style={{
                    color: (p.report_detail?.total_score ?? 0) > 0
                      ? 'var(--green)'
                      : (p.report_detail?.total_score ?? 0) < 0
                      ? 'var(--red)'
                      : 'var(--text-secondary)'
                  }}>
                    {(p.report_detail?.total_score ?? 0) > 0 ? '+' : ''}
                    {p.report_detail?.total_score ?? '—'}/6
                  </span>
                  <span className={styles.rowPrice}>
                    {p.report_detail?.technicals?.current_price
                      ? `$${p.report_detail.technicals.current_price}`
                      : ''}
                  </span>
                </div>

                <DecisionBadge decision={p.decision} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}