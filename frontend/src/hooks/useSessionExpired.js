import { useState, useCallback } from 'react'

/**
 * Retourne un message d'expiration de session et une fonction
 * qui wrape un appel API et détecte les erreurs 401.
 *
 * Usage :
 *   const { sessionMsg, callApi } = useSessionExpired()
 *   const data = await callApi(() => getPredictionsByClient(token))
 *   if (sessionMsg) return <SessionBanner />
 */
export function useSessionExpired() {
  const [sessionExpired, setSessionExpired] = useState(false)

  const callApi = useCallback(async (apiFn) => {
    try {
      return await apiFn()
    } catch (err) {
      if (err.status === 401) {
        setSessionExpired(true)
        return null
      }
      throw err  // autres erreurs remontées normalement
    }
  }, [])

  return { sessionExpired, callApi }
}