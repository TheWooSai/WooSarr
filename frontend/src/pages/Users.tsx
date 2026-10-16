import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';

interface User {
  id: string;
  username: string;
  email: string;
  linked_discord: string;
  roles: string[];
  libraries: string[];
}

function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch users from API
    fetch('/api/users/')
      .then(res => res.json())
      .then(data => {
        setUsers(data.users || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'username', label: 'Username', sortable: true },
    { key: 'email', label: 'Email', sortable: true },
    { key: 'linked_discord', label: 'Discord', sortable: true },
    { key: 'roles', label: 'Roles' },
    { key: 'libraries', label: 'Libraries' },
  ];

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Users</h2>
      <DataTable columns={columns} data={users} searchPlaceholder="Search users..." />
    </div>
  );
}

export default Users;