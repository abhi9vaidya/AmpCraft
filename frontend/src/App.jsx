import { useState, useCallback } from 'react'
import axios from 'axios'
import './App.css'

const TONE_META = {
  'Clean':  { emoji: '🎵', color: '#4caf90', desc: 'Warm, transparent, studio clean' },
  'Crunch': { emoji: '⚡', color: '#f5a623', desc: 'Crunchy mid-gain overdrive' },
  'Lead':   { emoji: '🔥', color: '#e84040', desc: 'High-gain, cutting lead tone' },
}

// Signal chain block config — defines order, icon, title, and how to extract settings
function getChainBlocks(chain) {
  return [
    {
      key:      'noise_gate',
      icon:     '🔇',
      title:    'Noise Gate',
      enabled:  chain.noise_gate.enabled,
      settings: [
        { label: 'Status',    value: chain.noise_gate.enabled ? 'ON' : 'OFF' },
        { label: 'Threshold', value: `${chain.noise_gate.threshold} dB` },
      ],
    },
    {
      key:      'efx',
      icon:     '🎛️',
      title:    'EFX (Drive)',
      enabled:  chain.efx.type !== 'None',
      settings: [
        { label: 'Type', value: chain.efx.type },
        ...(chain.efx.gain != null ? [{ label: 'Gain', value: chain.efx.gain }] : []),
      ],
    },
    {
      key:      'amp',
      icon:     '🔊',
      title:    'Amp',
      enabled:  true,
      settings: [
        { label: 'Type',   value: chain.amp.type   },
        { label: 'Gain',   value: chain.amp.gain   },
        { label: 'Volume', value: chain.amp.volume },
      ],
    },
    {
      key:      'ir',
      icon:     '📦',
      title:    'IR Cab',
      enabled:  true,
      settings: [
        { label: 'Cabinet', value: chain.ir.cab },
        ...(chain.ir.mic ? [{ label: 'Mic', value: chain.ir.mic }] : []),
      ],
    },
    {
      key:      'mod',
      icon:     '🌀',
      title:    'Modulation',
      enabled:  chain.mod.type !== 'None',
      settings: [
        { label: 'Type',  value: chain.mod.type },
        ...(chain.mod.depth != null ? [{ label: 'Depth', value: chain.mod.depth }] : []),
      ],
    },
    {
      key:      'delay',
      icon:     '⏱️',
      title:    'Delay',
      enabled:  chain.delay.type !== 'None',
      settings: [
        { label: 'Type', value: chain.delay.type },
        ...(chain.delay.time != null ? [{ label: 'Time', value: `${chain.delay.time} ms` }] : []),
      ],
    },
    {
      key:      'reverb',
      icon:     '🏔️',
      title:    'Reverb',
      enabled:  chain.reverb.type !== 'None',
      settings: [
        { label: 'Type',  value: chain.reverb.type },
        ...(chain.reverb.level != null ? [{ label: 'Level', value: chain.reverb.level }] : []),
      ],
    },
  ]
}

function ChainBlock({ icon, title, enabled, settings }) {
  return (
    <div className={`chain-block ${enabled ? 'block-on' : 'block-off'}`}>
      <div className="block-header">
        <span className="block-icon">{icon}</span>
        <span className="block-title">{title}</span>
        <span className={`block-pill ${enabled ? 'pill-on' : 'pill-off'}`}>
          {enabled ? 'ON' : 'OFF'}
        </span>
      </div>
      <div className="block-settings">
        {settings.map(({ label, value }) => (
          <div key={label} className="block-row">
            <span className="block-label">{label}</span>
            <span className="block-value">{value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Knob({ label, value, max = 10 }) {
  const pct = value / max
  const angle = -135 + pct * 270
  return (
    <div className="knob-wrap">
      <div className="knob" style={{ '--angle': `${angle}deg` }}>
        <div className="knob-dot" />
      </div>
      <span className="knob-value">{value}</span>
      <span className="knob-label">{label}</span>
    </div>
  )
}

function ResultCard({ chain, features }) {
  const toneName = chain.amp.type
  const meta = TONE_META[toneName] || { emoji: '🎸', color: '#f5a623', desc: '' }
  const blocks = getChainBlocks(chain)

  return (
    <div className="result-card" style={{ '--accent': meta.color }}>
      {/* Tone Header */}
      <div className="tone-header">
        <span className="tone-emoji">{meta.emoji}</span>
        <div>
          <h2 className="tone-name">{toneName}</h2>
          <p className="tone-desc">{meta.desc}</p>
        </div>
      </div>

      {/* Signal Chain */}
      <div className="section-label">Signal Chain</div>
      <div className="chain-list">
        {blocks.map((block, i) => (
          <div key={block.key} className="chain-item">
            <ChainBlock {...block} />
            {i < blocks.length - 1 && <div className="chain-arrow">↓</div>}
          </div>
        ))}
      </div>

      {/* Audio Analysis */}
      <div className="section-label">Audio Analysis</div>
      <div className="features-row">
        <div className="feature-chip">
          <span className="chip-label">Spectral Centroid</span>
          <span className="chip-value">{features.centroid.toFixed(0)} Hz</span>
        </div>
        <div className="feature-chip">
          <span className="chip-label">Zero Crossing Rate</span>
          <span className="chip-value">{features.zcr.toFixed(4)}</span>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [file, setFile]       = useState(null)
  const [dragging, setDrag]   = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const selectFile = (f) => {
    if (!f) return
    setFile(f)
    setResult(null)
    setError(null)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDrag(false)
    selectFile(e.dataTransfer.files[0])
  }, [])

  const analyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('/api/analyze', formData)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">🎸</div>
        <h1 className="brand">AmpCraft</h1>
        <p className="tagline">AI-powered guitar tone analyzer</p>
      </header>

      <main className="main">
        <div className="card">
          <div
            id="drop-zone"
            className={`drop-zone ${dragging ? 'dragover' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <div className="dz-icon">{file ? '✅' : '🎵'}</div>
            {file
              ? <p className="dz-filename">📎 {file.name}</p>
              : <>
                  <p className="dz-main">Drag &amp; drop your audio here</p>
                  <p className="dz-sub">or <span>click to browse</span></p>
                </>
            }
          </div>

          <input
            id="file-input"
            type="file"
            accept="audio/*"
            style={{ display: 'none' }}
            onChange={(e) => selectFile(e.target.files[0])}
          />

          <button
            id="analyze-btn"
            className="btn-analyze"
            disabled={!file || loading}
            onClick={analyze}
          >
            {loading ? <span className="spinner" /> : '🎛️ Analyze Tone'}
          </button>

          {error && <p className="error-msg">❌ {error}</p>}
        </div>

        {result && (
          <div className="result-wrap">
            <ResultCard chain={result.chain} features={result.features} />
          </div>
        )}
      </main>

      <footer className="app-footer">Built with 🎸 + AI</footer>
    </div>
  )
}
