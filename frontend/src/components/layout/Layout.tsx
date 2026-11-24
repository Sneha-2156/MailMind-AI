import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import { ToastContainer } from '@/components/ui/Toast'
import { useEmailStore } from '@/stores/emailStore'
import { useGmailAutoSync } from '@/hooks/useGmailAutoSync'
import { Spinner } from '@/components/ui/Spinner'

export const Layout: React.FC = () => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const { emails } = useEmailStore()

  const { isInitialSync } = useGmailAutoSync()

  const unreadCount = emails.filter((e) => !e.is_read).length

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] text-slate-900 dark:text-slate-100 flex">
      {/* Toast notifications container */}
      <ToastContainer />

      {/* Sidebar Navigation */}
      <Sidebar
        isOpen={mobileSidebarOpen}
        onClose={() => setMobileSidebarOpen(false)}
        unreadCount={unreadCount}
      />

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        {/* Topbar Header */}
        <Topbar onOpenMobileSidebar={() => setMobileSidebarOpen(true)} />

        {/* Dynamic Route Pages */}
        <main className="flex-1 overflow-x-hidden">
          {isInitialSync ? (
            <div className="h-[calc(100vh-4rem)] flex flex-col items-center justify-center gap-3 text-center px-6">
              <Spinner size="lg" />
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                Importing your Gmail inbox…
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Classifying emails and extracting tasks. This takes a few seconds the first time.
              </p>
            </div>
          ) : (
            <Outlet />
          )}
        </main>
      </div>
    </div>
  )
}
