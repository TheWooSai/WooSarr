import { useState } from 'react';

interface SetupDiscordProps {
  onStarted: () => void;
}

function SetupDiscord({ onStarted }: SetupDiscordProps) {
  const [discordToken, setDiscordToken] = useState('');
  const [error, setError] = useState('');

  const handleDiscordSetup = async () => {
    try {
      setError('');
      await fetch('/api/setup/discord/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: discordToken }),
      });
      onStarted();
    } catch (e) {
      setError('Failed to save Discord token');
    }
  };

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
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
        Connect Discord
      </button>
    </div>
  );
}

export default SetupDiscord;