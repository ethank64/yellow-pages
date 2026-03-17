import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import BaseLayout from './BaseLayout'
import Index from './Index'
import DocsLayout from './pages/DocsLayout'
import QuickStart from './pages/QuickStart'
import EnvVars from './pages/EnvVars'
import AddingToCursor from './pages/AddingToCursor'
import SchemaFormat from './pages/SchemaFormat'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <BaseLayout>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="docs" element={<DocsLayout />}>
            <Route path="quick-start" element={<QuickStart />} />
            <Route path="env-vars" element={<EnvVars />} />
            <Route path="adding-to-cursor" element={<AddingToCursor />} />
            <Route path="schema-format" element={<SchemaFormat />} />
            <Route index element={<Navigate to="quick-start" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BaseLayout>
    </BrowserRouter>
  )
}

export default App
