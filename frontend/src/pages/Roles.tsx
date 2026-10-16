import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';

interface Role {
  id: string;
  name: string;
  color: string;
  members: number;
  libraries: string[];
}

function Roles() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch roles from API
    fetch('/api/discord/roles')
      .then(res => res.json())
      .then(data => {
        setRoles(data.roles || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'color', label: 'Color' },
    { key: 'members', label: 'Members', sortable: true },
    { key: 'libraries', label: 'Libraries' },
  ];

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Roles</h2>
      <DataTable columns={columns} data={roles} searchPlaceholder="Search roles..." />
    </div>
  );
}

export default Roles;