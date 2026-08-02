'use client';
import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, CheckCircle } from 'lucide-react';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analytics/dashboard`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        setError('Failed to load analytics');
      }
    } catch (err) {
      setError('Error loading analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-20"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (error) return <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">{error}</div>;
  if (!analytics) return <div className="text-slate-600">No data</div>;

  return (
    <div className="space-y-8">
      <div><h1 className="text-4xl md:text-5xl font-bold text-slate-900">Analytics</h1><p className="text-slate-600 mt-2 text-lg">Your job search performance</p></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
          <div className="flex items-center gap-4"><div className="p-3 bg-blue-100 rounded-lg"><BarChart3 className="w-6 h-6 text-blue-600" /></div><div><p className="text-sm text-slate-600">Total Applications</p><p className="text-3xl font-bold text-slate-900 mt-1">{analytics?.applications?.total_applications || 0}</p></div></div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
          <div className="flex items-center gap-4"><div className="p-3 bg-green-100 rounded-lg"><CheckCircle className="w-6 h-6 text-green-600" /></div><div><p className="text-sm text-slate-600">Success Rate</p><p className="text-3xl font-bold text-slate-900 mt-1">{analytics?.applications?.success_rate || 0}%</p></div></div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
          <div className="flex items-center gap-4"><div className="p-3 bg-purple-100 rounded-lg"><TrendingUp className="w-6 h-6 text-purple-600" /></div><div><p className="text-sm text-slate-600">Avg Days</p><p className="text-3xl font-bold text-slate-900 mt-1">{analytics?.applications?.avg_days_to_accept || 0}</p></div></div>
        </div>
      </div>
    </div>
  );
}
