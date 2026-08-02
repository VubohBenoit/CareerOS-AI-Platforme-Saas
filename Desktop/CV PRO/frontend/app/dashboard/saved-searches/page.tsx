'use client';
import { useEffect, useState } from 'react';
import { Save, Bell, Trash2, Search } from 'lucide-react';

interface SavedSearch {
  id: string;
  name: string;
  keywords?: string;
  location?: string;
  notify_enabled: boolean;
}

export default function SavedSearchesPage() {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/saved-searches/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        setSearches(data);
      } else {
        setError('Failed to load saved searches');
      }
    } catch (err) {
      setError('Error loading searches');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-start"><div><h1 className="text-4xl md:text-5xl font-bold text-slate-900">Saved Searches</h1><p className="text-slate-600 mt-2 text-lg">Create alerts for jobs</p></div><button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg">+ New</button></div>
      {error && <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">{error}</div>}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-20"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>
        ) : searches.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-300"><Search className="w-16 h-16 text-slate-300 mx-auto mb-4" /><p className="text-slate-600">No saved searches</p></div>
        ) : (
          searches.map((s) => (
            <div key={s.id} className="bg-white rounded-xl shadow-md hover:shadow-lg border border-slate-200 p-6">
              <div className="flex justify-between items-start"><div className="flex-1"><div className="flex items-center gap-3 mb-2"><Save className="w-5 h-5 text-blue-600" /><h3 className="text-lg font-bold text-slate-900">{s.name}</h3></div><div className="space-y-1 text-sm text-slate-600">{s.keywords && <p>Keywords: {s.keywords}</p>}{s.location && <p>Location: {s.location}</p>}</div></div><div className="flex gap-2"><button className={`p-2 rounded-lg transition ${s.notify_enabled ? 'bg-green-100 text-green-700' : 'bg-slate-100'}`}><Bell className="w-5 h-5" /></button><button className="p-2 rounded-lg text-slate-400 hover:text-red-600"><Trash2 className="w-5 h-5" /></button></div></div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
