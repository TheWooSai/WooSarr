import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';

interface Library {
  key: number;
  title: string;
  type: string;
  exempt: boolean;
  roles: string[];
}

function Libraries() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch libraries from API
    fetch('/api/libraries/')
      .then(res => res.json())
      .then(data => {
        setLibraries(data.libraries || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'title', label: 'Title', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'exempt', label: 'Exempt' },
    { key: 'roles', label: 'Roles' },
  ];

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Libraries</h2>
      <DataTable columns={columns} data={libraries} searchPlaceholder="Search libraries..." />
    </div>
  );
}

export default Libraries;