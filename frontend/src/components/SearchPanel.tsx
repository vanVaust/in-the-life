import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

interface GeoEntity {
  id: string
  name: string
  geo_level: string
  iso_code?: string
}

interface Props {
  onSelect: (id: string) => void
}

export default function SearchPanel({ onSelect }: Props) {
  const [query, setQuery] = useState('')

  const { data } = useQuery<GeoEntity[]>({
    queryKey: ['geo', 'list'],
    queryFn: () => api.get('/api/v1/geo?geo_level=country&limit=200').then(r => r.data),
  })

  const filtered = (data ?? []).filter(e =>
    e.name.toLowerCase().includes(query.toLowerCase()) ||
    (e.iso_code ?? '').toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div>
      <input
        type="text"
        placeholder="Land suchen…"
        value={query}
        onChange={e => setQuery(e.target.value)}
        style={{
          width: '100%', padding: '8px 12px', background: '#1e1e2e',
          border: '1px solid #333', borderRadius: 6, color: '#e0e0e0',
          marginBottom: 12, boxSizing: 'border-box'
        }}
      />
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {filtered.slice(0, 50).map(e => (
          <li key={e.id}
            onClick={() => onSelect(e.id)}
            style={{
              padding: '6px 10px', cursor: 'pointer', borderRadius: 4,
              marginBottom: 2, fontSize: 13,
              background: 'transparent',
            }}
            onMouseEnter={ev => (ev.currentTarget.style.background = '#2d2d4a')}
            onMouseLeave={ev => (ev.currentTarget.style.background = 'transparent')}
          >
            <span style={{ marginRight: 8, opacity: 0.5 }}>{e.iso_code}</span>{e.name}
          </li>
        ))}
      </ul>
    </div>
  )
}
