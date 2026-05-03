import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { getPredictionsByClient } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { DecisionBadge } from '../components/ui/Badge'
import SessionBanner from '../components/ui/SessionBanner'
import { useSessionExpired } from '../hooks/useSessionExpired'
import styles from './Dashboard.module.css'
 
const COLORS = { BUY: '#22C55E', HOLD: '#3B82F6', SELL: '#EF4444' }
 
export default function Dashboard() {
  const { token, client } = useAuth()
  const navigate = useNavigate()
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { sessionExpired, callApi } = useSessionExpired()
 
  useEffect(() => {
    callApi(() => getPredictionsByClient(token))
      .then(data => { if (data) setPredictions(data) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])
 
  // Statistiques
  const counts = predictions.reduce((acc, p) => {
    acc[p.decision] = (acc[p.decision] || 0) + 1
    return acc
  }, {})
 
  const pieData = ['BUY','HOLD','SELL']
    .filter(d => counts[d])
    .map(d => ({ name: d, value: counts[d] }))
 
  // Dernières prédictions — une par ticker, la plus récente
  const latest = Object.values(
    predictions.reduce((acc, p) => {
      if (!acc[p.ticket] || new Date(p.time_stamp) > new Date(acc[p.ticket].time_stamp)) {
        acc[p.ticket] = p
      }
      return acc
    }, {})
  ).sort((a, b) => new Date(b.time_stamp) - new Date(a.time_stamp))
 
  if (loading) return <p className={styles.msg}>Chargement...</p>
  if (error)   return <p className={styles.msg} style={{color:'var(--red)'}}>Erreur : {error}</p>
 
  return (
    <div className={styles.page}>
      {sessionExpired && <SessionBanner />}
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Dashboard</h1>
          <p className={styles.hello}>Bonjour, <span>{client?.nom}</span></p>
        </div>
        <button className={styles.newBtn} onClick={() => navigate('/predict')}>
          + Nouvelle analyse
        </button>
      </div>
 
      {predictions.length === 0 ? (
        <div className={styles.empty}>
          <p>Aucune prédiction pour l'instant.</p>
          <button className={styles.newBtn} onClick={() => navigate('/predict')}>
            Lancer une première analyse
          </button>
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className={styles.stats}>
            {[
              { label: 'Total', value: predictions.length, color: 'var(--text-primary)' },
              { label: 'BUY',   value: counts.BUY  || 0,  color: 'var(--green)' },
              { label: 'HOLD',  value: counts.HOLD || 0,  color: 'var(--blue)'  },
              { label: 'SELL',  value: counts.SELL || 0,  color: 'var(--red)'   },
            ].map(s => (
              <div key={s.label} className={styles.statCard}>
                <span className={styles.statVal} style={{ color: s.color }}>{s.value}</span>
                <span className={styles.statLabel}>{s.label}</span>
              </div>
            ))}
          </div>
 
          {/* Contenu principal */}
          <div className={styles.grid}>
            {/* Pie chart */}
            <div className={styles.chartCard}>
              <h2 className={styles.cardTitle}>Répartition des décisions</h2>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%" cy="50%"
                    innerRadius={60} outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={COLORS[entry.name]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                    labelStyle={{ color: 'var(--text-primary)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className={styles.legend}>
                {pieData.map(d => (
                  <div key={d.name} className={styles.legendItem}>
                    <span className={styles.dot} style={{ background: COLORS[d.name] }} />
                    <span>{d.name}</span>
                    <span className={styles.legendVal}>{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
 
            {/* Dernières analyses par ticker */}
            <div className={styles.tickerList}>
              <h2 className={styles.cardTitle}>Dernière analyse par ticker</h2>
              <div className={styles.tickers}>
                {latest.map(p => (
                  <div
                    key={p.ticket}
                    className={styles.tickerCard}
                    onClick={() => navigate(`/prediction/${p.id_prediction}`)}
                  >
                    <div className={styles.tickerLeft}>
                      <span className={styles.ticker}>{p.ticket}</span>
                      <span className={styles.price}>
                        {p.report_detail?.technicals?.current_price
                          ? `$${p.report_detail.technicals.current_price}`
                          : '—'}
                      </span>
                    </div>
                    <div className={styles.tickerRight}>
                      <DecisionBadge decision={p.decision} />
                      <span className={styles.score}>
                        {p.report_detail?.total_score > 0
                          ? `+${p.report_detail.total_score}`
                          : p.report_detail?.total_score}
                        /6
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}