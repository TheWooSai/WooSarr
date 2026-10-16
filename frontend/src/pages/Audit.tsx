import { useState, useEffect } from 'react';

interface AuditEntry {
  id: number;
  timestamp: string;
  actor: string;
  action: string;
  target: string;
  details: string;
  dry_run: boolean;
}

function Audit() {
  const [entries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch audit entries from API
    // TODO: Implement audit API endpoint
    setLoading(false);
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Audit Log</h2>
      <p>Permission changes and sync events</p>
      {entries.length === 0 ? (
        <p>No audit entries yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ padding: '0.5rem', textAlign: 'left', borderBottom: '1px solid #ccc' }}>Time</th>
              <th style={{ padding: '0.5rem', textAlign: 'left', borderBottom: '1px solid #ccc' }}>Actor</th>
              <th style={{ padding: '0.5rem', textAlign: 'left', borderBottom: '1px solid #ccc' }}>Action</th>
              <th style={{ padding: '0.5rem', textAlign: 'left', borderBottom: '1px solid #ccc' }}>Target</th>
              <th style={{ padding: '0.5rem', textAlign: 'left', borderBottom: '1px solid #ccc' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(entry => (
              <tr key={entry.id}>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>{entry.timestamp}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>{entry.actor}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>{entry.action}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>{entry.target}</td>
                <td style={{ padding: '0.5rem', borderBottom: '1px solid #eee' }}>
                  {entry.details}
                  {entry.dry_run && <span style={{ color: '#ffc107' }}> [DRY RUN]</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Audit;