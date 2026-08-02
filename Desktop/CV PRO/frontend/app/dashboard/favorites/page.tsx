'use client';
import { useEffect, useState } from 'react';
import { Heart, MapPin, DollarSign, Briefcase } from 'lucide-react';

interface FavoriteJob {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_min?: number;
  employment_type: string;
}

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/favorites/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        setFavorites(data);
      } else {
        setError('Failed to load favorites');
      }
    } catch (err) {
      setError('Error loading favorites');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div><h1 className="text-4xl md:text-5xl font-bold text-slate-900">Saved Jobs</h1><p className="text-slate-600 mt-2 text-lg">Your bookmarked opportunities</p></div>
      {error && <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">{error}</div>}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-20"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div><p className="text-slate-600 mt-4">Loading...</p></div>
        ) : favorites.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-300"><Heart className="w-16 h-16 text-slate-300 mx-auto mb-4" /><p className="text-slate-600">No saved jobs</p></div>
        ) : (
          favorites.map((job) => (
            <div key={job.id} className="bg-white rounded-xl shadow-md hover:shadow-lg border border-slate-200 p-6">
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-slate-900">{job.title}</h3>
                  <p className="text-slate-600">{job.company}</p>
                  <div className="flex gap-3 mt-3"><div className="flex items-center gap-1 text-sm text-slate-600"><MapPin className="w-4 h-4" />{job.location}</div>{job.salary_min && <div className="flex items-center gap-1 text-sm text-slate-600"><DollarSign className="w-4 h-4" />€{job.salary_min.toLocaleString()}</div>}<div className="flex items-center gap-1 text-sm text-slate-600"><Briefcase className="w-4 h-4" />{job.employment_type}</div></div>
                </div>
                <button className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg">Apply</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
