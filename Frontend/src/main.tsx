import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'  // This loads Tailwind CSS
import App from './App.tsx'
import { pdfjs } from 'react-pdf'

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)