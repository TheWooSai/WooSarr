import { useState } from 'react';

interface SetupPlexProps {
  onAuthenticated: () => void;
}

function SetupPlex({ onAuthenticated }: SetupPlexProps) {
  const [plexCode, setPlexCode] = useState('');
  const [plexUrl, setPlexUrl] = useState('');
  const [plexAuthenticating, setPlexAuthenticating] = useState(false);
  const [error, setError] = useState('');

  const handlePlexOAuthStart = async () => {
    try {
      setError('');
      const response = await fetch('/api/setup/plex/authenticate', {
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
      const response = await fetch('/api/setup/plex/poll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: plexCode }),
      });
      const data = await response.json();

      if (data.success && data.authenticated) {
        setPlexAuthenticating(false);
        onAuthenticated();
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

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
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
  );
}

export default SetupPlex;