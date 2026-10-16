import { useState, useEffect } from 'react';

function Dashboard() {
  const [plexStatus, setPlexStatus] = useState('unknown');
  const [discordStatus, setDiscordStatus] = useState('unknown');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch Plex status
    fetch('/api/plex/status')
      .then(res => res.json())
      .then(data => setPlexStatus(data.authenticated ? 'connected' : 'disconnected'))
      .catch(() => setPlexStatus('error'));

    // Fetch Discord status
    fetch('/api/discord/status')
      .then(res => res.json())
      .then(data => setDiscordStatus(data.running ? 'connected' : 'disconnected'))
      .catch(() => setDiscordStatus('error'));

    setLoading(false);
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'connected': return '#28a745';
      case 'disconnected': return '#dc3545';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
          <h3>Plex</h3>
          <span style={{ color: statusColor(plexStatus) }}>●</span> {plexStatus}
        </div>
        <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
          <h3>Discord</h3>
          <span style={{ color: statusColor(discordStatus) }}>●</span> {discordStatus}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;