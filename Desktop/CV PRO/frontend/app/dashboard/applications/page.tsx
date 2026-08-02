'use client';
import { useEffect, useState } from 'react';
import { FileText, CheckCircle, Clock, XCircle } from 'lucide-react';

interface Application {
  id: string;
  status: string;
  created_at: string;
}

const statusConfig: Record<string, { color: string; icon: any; label: string }> = {
  SENT: { color: 'blue', icon: Clock, label: 'Sent' },
  INTERVIEWING: { color: 'purple', icon: FileText, label: 'Interviewing' },
  REJECTED: { color: 'red', icon: XCircle, label: 'Rejected' },
  ACCEPTED: { color: 'green', icon: CheckCircle, label: 'Accepted' },
};

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        setApplications(data);
      } else {
        setError('Failed to load applications');
      }
    } catch (err) {
      setError('Error loading applications');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl md:text-5xl font-bold text-slate-900">Applications</h1>
        <p className="text-slate-600 mt-2 text-lg">Track your job applications</p>
      </div>
      {error && <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">{error}</div>}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-20"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div><p className="text-slate-600 mt-4">Loading...</p></div>
        ) : applications.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-300"><FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" /><p className="text-slate-600">No applications</p></div>
        ) : (
          applications.map((app) => {
            const config = statusConfig[app.status] || statusConfig.SENT;
            const Icon = config.icon;
            const colorClasses: Record<string, string> = { blue: 'bg-blue-100 text-blue-700', purple: 'bg-purple-100 text-purple-700', red: 'bg-red-100 text-red-700', green: 'bg-green-100 text-green-700' };
            return (
              <div key={app.id} className="bg-white rounded-xl shadow-md hover:shadow-lg border border-slate-200 p-6">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg ${colorClasses[config.color]}`}><Icon className="w-6 h-6" /></div>
                    <div><p className="text-sm text-slate-600">Application #{app.id.slice(0,8)}</p><p className="text-slate-900 font-semibold">Applied on {new Date(app.created_at).toLocaleDateString()}</p></div>
                  </div>
                  <span className={`px-4 py-2 rounded-full font-semibold text-sm ${colorClasses[config.color]}`}>{config.label}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
