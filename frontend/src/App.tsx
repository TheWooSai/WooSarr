import { useState } from 'react';

function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'users', label: 'Users' },
    { id: 'roles', label: 'Roles' },
    { id: 'libraries', label: 'Libraries' },
    { id: 'logs', label: 'Logs' },
    { id: 'settings', label: 'Settings' },
    { id: 'setup', label: 'Setup' },
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* Sidebar */}
      <nav style={{
        width: '200px',
        backgroundColor: '#2d2d3d',
        color: '#fff',
        padding: '1rem',
      }}>
        <h2 style={{ margin: '0 0 1rem 0' }}>WooSarr</h2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {navItems.map(item => (
            <li key={item.id}>
              <button
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '0.5rem',
                  margin: '0.25rem 0',
                  backgroundColor: activePage === item.id ? '#4a4a6a' : 'transparent',
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
      </nav>

      {/* Main content */}
      <main style={{ flex: 1, padding: '2rem', backgroundColor: '#f5f5f5' }}>
        <h1>{activePage.charAt(0).toUpperCase() + activePage.slice(1)}</h1>
        <p>Content for {activePage} page</p>
      </main>
    </div>
  );
}

export default App;