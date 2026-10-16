import { useState, useEffect } from 'react';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [theme, setTheme] = useState('light');

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('woosarr-theme');
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  // Save theme to localStorage
  useEffect(() => {
    localStorage.setItem('woosarr-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'users', label: 'Users' },
    { id: 'roles', label: 'Roles' },
    { id: 'libraries', label: 'Libraries' },
    { id: 'logs', label: 'Logs' },
    { id: 'settings', label: 'Settings' },
    { id: 'setup', label: 'Setup' },
  ];

  const isDark = theme === 'dark';

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      fontFamily: 'system-ui, sans-serif',
      backgroundColor: isDark ? '#1a1a2e' : '#f5f5f5',
      color: isDark ? '#fff' : '#000',
    }}>
      {/* Sidebar */}
      <nav style={{
        width: '200px',
        backgroundColor: isDark ? '#16213e' : '#2d2d3d',
        color: '#fff',
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <h2 style={{ margin: '0 0 1rem 0' }}>WooSarr</h2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, flex: 1 }}>
          {navItems.map(item => (
            <li key={item.id}>
              <button
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '0.5rem',
                  margin: '0.25rem 0',
                  backgroundColor: activePage === item.id ? '#7c3aed' : 'transparent',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
        <button
          onClick={toggleTheme}
          style={{
            padding: '0.5rem',
            backgroundColor: '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {isDark ? '☀️ Light' : '🌙 Dark'}
        </button>
      </nav>

      {/* Main content */}
      <main style={{
        flex: 1,
        padding: '2rem',
        backgroundColor: isDark ? '#1a1a2e' : '#f5f5f5',
        color: isDark ? '#fff' : '#000',
      }}>
        <h1>{activePage.charAt(0).toUpperCase() + activePage.slice(1)}</h1>
        <p>Content for {activePage} page</p>
      </main>
    </div>
  );
}

export default App;