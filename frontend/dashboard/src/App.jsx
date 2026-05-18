import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, ShieldCheck, Box, GitPullRequest, Terminal, 
  Settings, Play, X, Server, Code, CheckCircle, AlertTriangle
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import './index.css';

// Mock data
const MOCK_REPOS = [
  { id: 1, name: 'auth-service', health: 98, status: 'Healthy', lastSync: '2m ago' },
  { id: 2, name: 'payment-mesh', health: 64, status: 'Warning', lastSync: '5m ago' },
  { id: 3, name: 'ui-core', health: 92, status: 'Healthy', lastSync: '12m ago' },
  { id: 4, name: 'dispatch-mesh', health: 45, status: 'Critical', lastSync: '1m ago' },
  { id: 5, name: 'secrets-vault', health: 100, status: 'Healthy', lastSync: '1h ago' },
];

const INITIAL_LOGS = [
  { time: '14:22:01', level: 'INFO', msg: 'Started repo-analyzer for [auth-service]' },
  { time: '14:22:05', level: 'INFO', msg: 'Analysis complete. Score: 98. No risks found.' },
  { time: '14:23:10', level: 'WARNING', msg: 'CI failure detected on [payment-mesh] main branch.' },
  { time: '14:23:12', level: 'INFO', msg: 'Triggering ci-fixer worker for [payment-mesh]...' },
  { time: '14:24:00', level: 'ERROR', msg: '[dispatch-mesh] High complexity alert. Refactoring recommended.' },
];

const CHART_DATA = [
  { time: '10:00', health: 85, load: 40 },
  { time: '11:00', health: 86, load: 45 },
  { time: '12:00', health: 82, load: 75 },
  { time: '13:00', health: 89, load: 60 },
  { time: '14:00', health: 92, load: 30 },
  { time: '15:00', health: 91, load: 35 },
  { time: '16:00', health: 89, load: 50 },
];

function App() {
  const [repos, setRepos] = useState(MOCK_REPOS);
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const terminalEndRef = useRef(null);

  // Auto-scroll terminal
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Simulate incoming live data
  useEffect(() => {
    const interval = setInterval(() => {
      const msgs = [
        "Routine policy validation passed.",
        "K8s worker claimed pending PR generation task.",
        "Dependencies scanned: 0 critical vulnerabilities.",
        "AI Engine evaluating git diff for destructive patterns...",
        "Webhooks synchronized with GitHub API."
      ];
      
      const newLog = {
        time: new Date().toLocaleTimeString('en-US', { hour12: false }),
        level: Math.random() > 0.8 ? 'WARNING' : 'INFO',
        msg: msgs[Math.floor(Math.random() * msgs.length)]
      };
      
      setLogs(prev => [...prev, newLog].slice(-50));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = (repo) => {
    setSelectedRepo(repo);
    const triggerLog = {
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      level: 'INFO',
      msg: `[MANUAL OVERRIDE] Triggered deep analysis job for ${repo.name}...`
    };
    setLogs(prev => [...prev, triggerLog].slice(-50));
  };

  const closeModal = () => setSelectedRepo(null);

  return (
    <div className="app-container">
      {/* Header */}
      <header>
        <div className="brand">
          <div className="brand-logo">
            <ShieldCheck size={20} color="#fff" />
          </div>
          <h2>Repo Autopilot <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '0.9em' }}>Enterprise</span></h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <button className="btn" style={{ background: 'transparent', border: 'none' }}>
            <Settings size={20} color="var(--text-muted)" />
          </button>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
            <span className="live-indicator"></span> System Online
          </span>
        </div>
      </header>

      <main className="dashboard-main">
        {/* Telemetry Cards */}
        <section className="telemetry-grid">
          <div className="telemetry-card glass">
            <div className="telemetry-icon blue">
              <Box size={28} />
            </div>
            <div className="telemetry-data">
              <div className="telemetry-title">Managed Repositories</div>
              <div className="telemetry-value">52</div>
            </div>
          </div>
          <div className="telemetry-card glass">
            <div className="telemetry-icon green">
              <Activity size={28} />
            </div>
            <div className="telemetry-data">
              <div className="telemetry-title">Global Health Index</div>
              <div className="telemetry-value value-success">89.4%</div>
            </div>
          </div>
          <div className="telemetry-card glass">
            <div className="telemetry-icon yellow">
              <GitPullRequest size={28} />
            </div>
            <div className="telemetry-data">
              <div className="telemetry-title">Pending Tasks</div>
              <div className="telemetry-value value-warning">3</div>
            </div>
          </div>
          <div className="telemetry-card glass">
            <div className="telemetry-icon purple">
              <Server size={28} />
            </div>
            <div className="telemetry-data">
              <div className="telemetry-title">Active AI Workers</div>
              <div className="telemetry-value" style={{ color: '#a78bfa'}}>8</div>
            </div>
          </div>
        </section>

        {/* Dynamic Charting */}
        <section className="glass" style={{ padding: '1.5rem' }}>
          <div className="section-header">
            <h3 className="section-title"><Activity size={20} color="var(--primary)"/> Network Telemetry & Health Trends</h3>
          </div>
          <div className="charts-grid">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={CHART_DATA} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--success)" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="var(--success)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="var(--border)" tick={{fill: 'var(--text-muted)'}} />
                <YAxis stroke="var(--border)" tick={{fill: 'var(--text-muted)'}} />
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(19, 24, 35, 0.9)', borderColor: 'var(--border)', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="health" stroke="var(--success)" fillOpacity={1} fill="url(#colorHealth)" name="Health Score" />
                <Area type="monotone" dataKey="load" stroke="var(--primary)" fillOpacity={1} fill="url(#colorLoad)" name="System Load" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <div className="content-grid">
          {/* Repositories Table */}
          <section className="glass" style={{ padding: '1.5rem', overflow: 'hidden' }}>
            <div className="section-header">
              <h3 className="section-title"><Code size={20} color="var(--primary)"/> Repository Intelligence</h3>
              <button className="btn"><Play size={14}/> Sync All</button>
            </div>
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Repository</th>
                    <th>Health Score</th>
                    <th>State</th>
                    <th>Last Sync</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {repos.map(repo => (
                    <tr key={repo.id}>
                      <td>
                        <div className="repo-name">
                          {repo.status === 'Healthy' ? <CheckCircle size={16} color="var(--success)"/> : <AlertTriangle size={16} color="var(--warning)"/>}
                          {repo.name}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{ width: '80px', background: 'rgba(255,255,255,0.05)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ 
                              width: `${repo.health}%`, 
                              background: repo.health > 80 ? 'var(--success)' : repo.health > 50 ? 'var(--warning)' : 'var(--danger)',
                              height: '100%',
                              boxShadow: `0 0 10px ${repo.health > 80 ? 'var(--success)' : repo.health > 50 ? 'var(--warning)' : 'var(--danger)'}`
                            }}></div>
                          </div>
                          <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{repo.health}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`badge badge-${repo.status === 'Healthy' ? 'success' : repo.status === 'Warning' ? 'warning' : 'danger'}`}>
                          {repo.status}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{repo.lastSync}</td>
                      <td>
                        <button className="btn" onClick={() => handleAnalyze(repo)}>
                          <Play size={14}/> Run
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Audit Logger / Terminal */}
          <section>
            <div className="terminal">
              <div className="terminal-header">
                <Terminal size={16} /> Live Governance & Worker Audits
              </div>
              <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
                {logs.map((log, i) => (
                  <div key={i} className="log-line">
                    <span className="log-time">[{log.time}]</span>
                    <span className={`log-level-${log.level.toLowerCase()}`}>{log.level}</span>
                    <span className="log-message">{log.msg}</span>
                  </div>
                ))}
                <div ref={terminalEndRef} />
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Interactive Modal */}
      <div className={`modal-overlay ${selectedRepo ? 'active' : ''}`} onClick={closeModal}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h3 className="section-title">
              <ShieldCheck color="var(--primary)"/> Analyze Trigger
            </h3>
            <button className="modal-close" onClick={closeModal}><X size={20}/></button>
          </div>
          <div className="modal-body">
            <p style={{ marginBottom: '1rem' }}>
              You are about to queue a deep AI analysis job for <strong>{selectedRepo?.name}</strong>.
            </p>
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)', marginBottom: '1.5rem' }}>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><CheckCircle size={14} color="var(--success)"/> Risk & Dependency Check</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><CheckCircle size={14} color="var(--success)"/> Code Complexity Analysis</li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><CheckCircle size={14} color="var(--success)"/> Secret Exposure Scanning</li>
              </ul>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button className="btn" onClick={closeModal}>Cancel</button>
              <button className="btn btn-primary" onClick={() => {
                closeModal();
                // Simulation logs already handle this.
              }}>Queue Job</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
