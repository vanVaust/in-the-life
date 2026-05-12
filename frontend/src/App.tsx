import React, { useState } from 'react'
import TreemapView from './components/TreemapView'
import SearchPanel from './components/SearchPanel'

export default function App() {
  const [selectedGeoId, setSelectedGeoId] = useState<string | null>(null)

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f0f1a', color: '#e0e0e0', fontFamily: 'Inter, sans-serif' }}>
      <aside style={{ width: 320, borderRight: '1px solid #222', padding: 16, overflowY: 'auto' }}>
        <h1 style={{ fontSize: 18, marginBottom: 16, color: '#7dd3fc' }}>🌍 In-The-Life</h1>
        <SearchPanel onSelect={setSelectedGeoId} />
      </aside>
      <main style={{ flex: 1, padding: 16 }}>
        {selectedGeoId
          ? <TreemapView geoId={selectedGeoId} width={window.innerWidth - 360} height={window.innerHeight - 48} />
          : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.4 }}>Geo-Entität auswählen</div>
        }
      </main>
    </div>
  )
}
