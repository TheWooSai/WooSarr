import { useState } from 'react';

function Settings() {
  const [theme, setTheme] = useState('light');
  const [reconcileInterval, setReconcileInterval] = useState(300);
  const [dryRun, setDryRun] = useState(false);

  const handleSave = () => {
    // Save settings to API
    console.log('Saving settings:', { theme, reconcileInterval, dryRun });
  };

  return (
    <div>
      <h2>Settings</h2>
      <div style={{ maxWidth: '600px' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label>Theme</label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            style={{ width: '100%', padding: '0.5rem' }}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label>Reconcile Interval (seconds)</label>
          <input
            type="number"
            value={reconcileInterval}
            onChange={(e) => setReconcileInterval(Number(e.target.value))}
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label>
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
            />
            Dry Run Mode
          </label>
        </div>
        <button
          onClick={handleSave}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Save
        </button>
      </div>
    </div>
  );
}

export default Settings;