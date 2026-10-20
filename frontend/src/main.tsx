import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// No service worker. A precache on the NAS served a stale login build, and
// iPhone Add to Home Screen does not need one. Drop any worker left behind.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((regs) => {
    regs.forEach((reg) => reg.unregister())
  })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
