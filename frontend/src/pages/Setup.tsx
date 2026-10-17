import { useState, useEffect } from 'react';
import SetupPlex from './SetupPlex';
import SetupDiscord from './SetupDiscord';

interface SetupStatus {
  plex: {
    authenticated: boolean;
    server_name: string;
  };
  discord: {
    running: boolean;
  };
}

function Setup() {
  const [status, setStatus] = useState<SetupStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSetupStatus();
  }, []);

  const fetchSetupStatus = async () => {
    try {
      const response = await fetch('/api/setup/status');
      const data = await response.json();
      setStatus(data);
    } catch (e) {
      console.error('Failed to fetch setup status:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading setup status...</div>;
  }

  return (
    <div>
      <h2>Setup</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div>
          <h3>Plex</h3>
          {status?.plex?.authenticated ? (
            <div>
              <p>✅ Connected to: {status.plex.server_name}</p>
            </div>
          ) : (
            <SetupPlex onAuthenticated={fetchSetupStatus} />
          )}
        </div>
        <div>
          <h3>Discord</h3>
          {status?.discord?.running ? (
            <div>
              <p>✅ Bot is running</p>
            </div>
          ) : (
            <SetupDiscord onStarted={fetchSetupStatus} />
          )}
        </div>
      </div>
    </div>
  );
}

export default Setup;