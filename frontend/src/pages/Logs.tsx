import { useState, useEffect } from 'react';

interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  component: string;
  message: string;
}

function Logs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    // Fetch logs from API
    fetch('/api/logs/recent?limit=100')
      .then(res => res.json())
      .then(data => {
        // Backend returns a list directly, not { logs: [...] }
        setLogs(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filteredLogs = logs.filter(log => {
    if (!filter) return true;
    return log.message.toLowerCase().includes(filter.toLowerCase()) ||
           log.level.toLowerCase().includes(filter.toLowerCase()) ||
           log.component.toLowerCase().includes(filter.toLowerCase());
  });

  const levelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error': return '#dc3545';
      case 'warning': return '#ffc107';
      case 'info': return '#17a2b8';
      case 'debug': return '#6c757d';
      default: return '#000';
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Logs</h2>
      <input
        type="text"
        placeholder="Filter logs..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        style={{
          width: '100%',
          padding: '0.5rem',
          marginBottom: '1rem',
          border: '1px solid #ccc',
          borderRadius: '4px',
        }}
      />
      <div style={{ maxHeight: '500px', overflowY: 'auto', border: '1px solid #ccc', borderRadius: '4px' }}>
        {filteredLogs.map(log => (
          <div key={log.id} style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>
            <span style={{ color: levelColor(log.level), fontWeight: 'bold' }}>[{log.level}]</span>{' '}
            <span style={{ color: '#6c757d' }}>({log.component})</span>{' '}
            <span>{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Logs;