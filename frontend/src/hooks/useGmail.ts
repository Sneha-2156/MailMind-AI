import { useEffect, useRef, useState } from 'react'
import { gmailApi } from '@/api/gmail'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/hooks/useToast'

export const EMAILS_SYNCED_EVENT = 'mailmind:emails-synced'
const DEMO_EMAIL = 'demo@mailmind.ai'
const STALE_AFTER_MS = 5 * 60 * 1000

/**
 * Pulls the signed-in user's Gmail into MailMind right after login.
 * - First ever sync: returns isInitialSync=true so the UI can show a loading screen.
 * - Later visits: refreshes quietly in the background when data is older than 5 minutes.
 */
export const useGmailAutoSync = () => {
  const user = useAuthStore((s) => s.user)
  const toast = useToast()
  const startedFor = useRef<string | null>(null)
  const [isInitialSync, setIsInitialSync] = useState(false)

  useEffect(() => {
    if (!user?.id || user.email === DEMO_EMAIL || !user.gmail_connected) return
    if (startedFor.current === user.id) return
    startedFor.current = user.id

    const run = async () => {
      let firstTime = false
      try {
        const { data } = await gmailApi.getSyncStatus()
        const last = data.last_synced_at ? new Date(data.last_synced_at).getTime() : 0
        const fresh = last > 0 && Date.now() - last < STALE_AFTER_MS
        if (fresh) return
        firstTime = !data.total_synced
      } catch {
        // status is best-effort; fall through to a sync attempt
      }

      if (firstTime) setIsInitialSync(true)
      try {
        const res = await gmailApi.syncEmails()
        if (res.data.new_count) {
          toast.success(res.data.message || `Synced ${res.data.new_count} new emails`)
        }
      } catch (err: any) {
        const detail = err?.response?.data?.detail
        toast.error(detail || 'Could not sync your Gmail. Try the sync button again.')
      } finally {
        setIsInitialSync(false)
        window.dispatchEvent(new Event(EMAILS_SYNCED_EVENT))
      }
    }
    run()
  }, [user?.id, user?.email, user?.gmail_connected, toast])

  return { isInitialSync }
}
