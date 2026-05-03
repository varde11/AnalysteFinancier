import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { makePrediction, TICKERS } from '../services/api'
import { useAuth } from '../context/AuthContext'
import SessionBanner from '../components/ui/SessionBanner'
import { useSessionExpired } from '../hooks/useSessionExpired'
import styles from './NewPrediction.module.css'

// Correspondance ticker → nom complet + pays
const TICKER_INFO = {
  'TSLA':      { name: 'Tesla',               country: '🇺🇸' },
  'AMZN':      { name: 'Amazon',              country: '🇺🇸' },
  'GOOG':      { name: 'Alphabet (Google)',   country: '🇺🇸' },
  'MSFT':      { name: 'Microsoft',           country: '🇺🇸' },
  'AAPL':      { name: 'Apple',               country: '🇺🇸' },
  'NVDA':      { name: 'Nvidia',              country: '🇺🇸' },
  'META':      { name: 'Meta Platforms',      country: '🇺🇸' },
  'NFLX':      { name: 'Netflix',             country: '🇺🇸' },
  'BA':        { name: 'Boeing',              country: '🇺🇸' },
  'ZS':        { name: 'Zscaler',             country: '🇺🇸' },
  'JPM':       { name: 'JPMorgan Chase',      country: '🇺🇸' },
  'GLD':       { name: 'SPDR Gold ETF',       country: '🇺🇸' },
  'MO':        { name: 'Altria Group',        country: '🇺🇸' },
  'MC.PA':     { name: 'LVMH',               country: '🇫🇷' },
  'TTE':       { name: 'TotalEnergies',       country: '🇫🇷' },
  'AIR.PA':    { name: 'Airbus',              country: '🇫🇷' },
  'ASML':      { name: 'ASML Holding',        country: '🇳🇱' },
  'SAP':       { name: 'SAP SE',              country: '🇩🇪' },
  'SPOT':      { name: 'Spotify',             country: '🇸🇪' },
  '005930.KS': { name: 'Samsung Electronics', country: '🇰🇷' },
}

export default function NewPrediction() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const { sessionExpired, callApi } = useSessionExpired()

  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyse() {
    if (!ticker) return
    setError('')
    setLoading(true)
    try {
      const prediction = await callApi(() => makePrediction(ticker, token))
      if (prediction) navigate(`/prediction/${prediction.id_prediction}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Nouvelle analyse</h1>
      <p className={styles.subtitle}>
        Sélectionne un ticker — le système récupère les indicateurs techniques
        et les actualités récentes pour produire une recommandation.
      </p>

      {sessionExpired && <SessionBanner />}

      <div className={styles.layout}>
        {/* Panneau gauche — sélection + bouton */}
        <div className={styles.card}>
          <label className={styles.label}>Ticker</label>
          <div className={styles.grid}>
            {TICKERS.map(t => (
              <button
                key={t}
                className={`${styles.tickerBtn} ${ticker === t ? styles.selected : ''}`}
                onClick={() => setTicker(t)}
                disabled={loading}
              >
                {t}
              </button>
            ))}
          </div>

          {error && <p className={styles.error}>⚠ {error}</p>}

          <button
            className={styles.analyseBtn}
            onClick={handleAnalyse}
            disabled={!ticker || loading}
          >
            {loading ? (
              <>
                <span className={styles.spinner} />
                Analyse en cours… (~30s)
              </>
            ) : (
              `Analyser ${ticker || '—'} →`
            )}
          </button>

          {loading && (
            <div className={styles.loadingInfo}>
              <p>Le système récupère les données de marché et scrute les actualités.</p>
              <p>Cette opération prend généralement entre 20 et 40 secondes.</p>
            </div>
          )}
        </div>

        {/* Panneau droit — tableau de référence des tickers */}
        <div className={styles.refCard}>
          <label className={styles.label}>Référentiel</label>
          <div className={styles.refTable}>
            {TICKERS.map(t => {
              const info = TICKER_INFO[t] || { name: t, country: '🌐' }
              return (
                <div
                  key={t}
                  className={`${styles.refRow} ${ticker === t ? styles.refRowActive : ''}`}
                  onClick={() => !loading && setTicker(t)}
                >
                  <span className={styles.refFlag}>{info.country}</span>
                  <span className={styles.refTicker}>{t}</span>
                  <span className={styles.refName}>{info.name}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}