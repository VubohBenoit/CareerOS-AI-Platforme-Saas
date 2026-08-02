'use client';

import { useEffect, useState } from 'react';
import { Search, MapPin, DollarSign, Briefcase, Heart, Clock } from 'lucide-react';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  description: string;
  required_skills: string[];
  employment_type: string;
  posted_date: string;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchJobs();
  }, [searchTerm]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jobs/?${params}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (response.ok) {
        const data = await response.json();
        setJobs(data);
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
          Job Opportunities
        </h1>
        <p className="text-slate-600 mt-2 text-lg">
          Explore thousands of job listings
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-slate-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search jobs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
            <p className="text-slate-600 mt-4">Loading jobs...</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-slate-300">
            <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600 text-lg">No jobs found</p>
          </div>
        ) : (
          jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-xl shadow-md hover:shadow-xl border border-slate-200 p-6 transition-all hover:-translate-y-1"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-2">
                    <div className="mt-1">
                      <Briefcase className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-900">{job.title}</h3>
                      <p className="text-slate-600 font-medium">{job.company}</p>
                    </div>
                    <span className="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap">
                      {job.employment_type}
                    </span>
                  </div>

                  <p className="text-slate-600 text-sm mb-4 line-clamp-2">
                    {job.description}
                  </p>

                  <div className="flex flex-wrap gap-3 mb-4">
                    <div className="flex items-center gap-1 text-sm text-slate-600">
                      <MapPin className="w-4 h-4" />
                      {job.location}
                    </div>
                    {job.salary_min && (
                      <div className="flex items-center gap-1 text-sm text-slate-600">
                        <DollarSign className="w-4 h-4" />
                        €{job.salary_min.toLocaleString()}-€{(job.salary_max || job.salary_min).toLocaleString()}
                      </div>
                    )}
                    <div className="flex items-center gap-1 text-sm text-slate-600">
                      <Clock className="w-4 h-4" />
                      {new Date(job.posted_date).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.map((skill) => (
                      <span
                        key={skill}
                        className="bg-slate-100 text-slate-700 text-xs px-3 py-1 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2 flex-shrink-0">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition">
                    Apply
                  </button>
                  <button className="text-slate-400 hover:text-red-500 p-2 transition">
                    <Heart className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
