import { useState } from 'react';

function Setup() {
  const [step, setStep] = useState(1);
  const [discordToken, setDiscordToken] = useState('');
  const [plexToken, setPlexToken] = useState('');

  const handleDiscordSetup = async () => {
    // Save Discord token
    await fetch('/api/discord/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: discordToken }),
    });
    setStep(2);
  };

  const handlePlexSetup = async () => {
    // Save Plex token
    await fetch('/api/plex/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: plexToken }),
    });
    setStep(3);
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
        <p>Enter your Plex auth token</p>
        <input
          type="text"
          value={plexToken}
          onChange={(e) => setPlexToken(e.target.value)}
          placeholder="Plex token..."
          style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
        />
        <button
          onClick={handlePlexSetup}
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

  return (
    <div>
      <h2>Setup Complete</h2>
      <p>Your WooSarr instance is now configured.</p>
    </div>
  );
}

export default Setup;