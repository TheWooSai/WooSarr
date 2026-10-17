import { useState, useEffect } from 'react';

function Setup() {
  const [step, setStep] = useState(1);
  const [discordToken, setDiscordToken] = useState('');
  const [plexCode, setPlexCode] = useState('');
  const [plexUrl, setPlexUrl] = useState('');
  const [plexAuthenticating, setPlexAuthenticating] = useState(false);
  const [plexAuthenticated, setPlexAuthenticated] = useState(false);
  const [plexServerName, setPlexServerName] = useState('');
  const [plexMachineId, setPlexMachineId] = useState('');
  const [error, setError] = useState('');

  // Check if Plex is already authenticated
  useEffect(() => {
    checkPlexStatus();
  }, []);

  const checkPlexStatus = async () => {
    try {
      const response = await fetch('/api/plex/status');
      const data = await response.json();
      if (data.authenticated) {
        setPlexAuthenticated(true);
        setPlexServerName(data.server_name);
        setPlexMachineId(data.machine_identifier);
      }
    } catch (e) {
      console.error('Failed to check Plex status:', e);
    }
  };

  const handleDiscordSetup = async () => {
    try {
      await fetch('/api/discord/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: discordToken }),
      });
      setStep(2);
    } catch (e) {
      setError('Failed to save Discord token');
    }
  };

  const handlePlexOAuthStart = async () => {
    try {
      setError('');
      const response = await fetch('/api/plex/oauth/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      if (data.success) {
        setPlexCode(data.code);
        setPlexUrl(data.url);
        setPlexAuthenticating(true);
        // Start polling
        pollPlexOAuth();
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError('Failed to start Plex OAuth');
    }
  };

  const pollPlexOAuth = async () => {
    if (!plexCode) return;

    try {
      const response = await fetch('/api/plex/oauth/poll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: plexCode }),
      });
      const data = await response.json();

      if (data.success && data.authenticated) {
        setPlexAuthenticating(false);
        setPlexAuthenticated(true);
        setPlexServerName(data.server_name);
        setPlexMachineId(data.machine_identifier);
        setStep(3);
      } else if (data.success && !data.authenticated) {
        // Keep polling
        setTimeout(pollPlexOAuth, 2000);
      } else {
        setPlexAuthenticating(false);
        setError(data.message);
      }
    } catch (e) {
      setPlexAuthenticating(false);
      setError('Failed to poll Plex OAuth');
    }
  };

  if (step === 1) {
    return (
      <div>
        <h2>Setup: Discord Bot</h2>
        <p>Enter your Discord bot token</p>
        <input
          type="text"
          value={discordToken}
          onChange={(e) => setDiscordToken(e.target.value)}
          placeholder="Bot token..."
          style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
        />
        <button
          onClick={handleDiscordSetup}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Next
        </button>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div>
        <h2>Setup: Plex Integration</h2>
        {plexAuthenticated ? (
          <div>
            <p>Connected to: {plexServerName}</p>
            <p>Machine ID: {plexMachineId}</p>
            <button
              onClick={() => setStep(3)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#7c3aed',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Next
            </button>
          </div>
        ) : (
          <div>
            <p>Click the button below to authenticate with Plex using OAuth.</p>
            {plexUrl && (
              <p>
                Or visit:{' '}
                <a href={plexUrl} target="_blank" rel="noopener noreferrer">
                  {plexUrl}
                </a>
              </p>
            )}
            <button
              onClick={handlePlexOAuthStart}
              disabled={plexAuthenticating}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#7c3aed',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: plexAuthenticating ? 'wait' : 'pointer',
              }}
            >
              {plexAuthenticating ? 'Waiting for authentication...' : 'Connect with Plex'}
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <h2>Setup Complete</h2>
      <p>Your WooSarr instance is now configured.</p>
    </div>
  );
}

export default Setup;