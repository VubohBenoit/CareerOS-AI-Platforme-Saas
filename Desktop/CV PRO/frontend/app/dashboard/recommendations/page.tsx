'use client';

import { useEffect, useState } from 'react';
import { Sparkles, MapPin, DollarSign, Briefcase, Heart } from 'lucide-react';

interface Recommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_min?: number;
  match_score: number;
  required_skills: string[];
  employment_type: string;
  description: string;
}

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/recommendations/`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      } else {
        setError('Failed to load recommendations');
      }
    } catch (err) {
      setError('Error loading recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl md:text-5xl font-bold text-slate-900">AI Recommendations</h1>
        <p className="text-slate-600 mt-2 text-lg">Jobs matched to your profile with AI</p>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">{error}</div>}

      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-slate-600 mt-4">Finding perfect matches...</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-300">
            <Sparkles className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600 text-lg">No recommendations yet</p>
          </div>
        ) : (
          recommendations.map((rec) => (
            <div key={rec.id} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-md hover:shadow-lg border border-blue-200 p-6 transition-all hover:-translate-y-1">
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="mt-1"><Sparkles className="w-5 h-5 text-purple-600" /></div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-900">{rec.title}</h3>
                      <p className="text-slate-600 font-medium">{rec.company}</p>
                    </div>
                    <div className="bg-gradient-to-r from-green-400 to-emerald-500 text-white text-sm font-bold px-4 py-2 rounded-full">{rec.match_score}%</div>
                  </div>

                  <div className="mb-4 w-full bg-slate-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full" style={{ width: `${rec.match_score}%` }}></div>
                  </div>

                  <p className="text-slate-600 text-sm mb-4">{rec.description}</p>

                  <div className="flex flex-wrap gap-3 mb-4">
                    <div className="flex items-center gap-1 text-sm text-slate-600"><MapPin className="w-4 h-4" />{rec.location}</div>
                    {rec.salary_min && <div className="flex items-center gap-1 text-sm text-slate-600"><DollarSign className="w-4 h-4" />€{rec.salary_min.toLocaleString()}</div>}
                    <div className="flex items-center gap-1 text-sm text-slate-600"><Briefcase className="w-4 h-4" />{rec.employment_type}</div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {rec.required_skills.map((skill) => (
                      <span key={skill} className="bg-white text-slate-700 text-xs px-3 py-1 rounded-full border border-slate-200">{skill}</span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2 flex-shrink-0">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition">Apply</button>
                  <button className="text-slate-400 hover:text-red-500 p-2 transition"><Heart className="w-6 h-6" /></button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
