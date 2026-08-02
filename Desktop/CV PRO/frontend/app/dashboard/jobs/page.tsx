'use client';
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, MapPin, DollarSign, Calendar, Briefcase } from 'lucide-react';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('Software Engineer');
  const [location, setLocation] = useState('Remote');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const searchJobs = async () => {
    setLoading(true);
    setError('');
    try {
      // Try real job board integrations first, fallback to demo
      let response = await fetch(
        `http://localhost:8000/api/v1/jobs-demo/search?q=${encodeURIComponent(search)}&location=${encodeURIComponent(location)}`
      );
      
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError('Failed to load jobs. Make sure backend is running on localhost:8000');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchJobs();
  }, []);

  const handleApply = async (jobId: string, jobTitle: string, company: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/applications/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_id: jobId,
          job_title: jobTitle,
          company: company,
          status: 'applied'
        })
      });

      if (response.ok) {
        alert('✅ Applied successfully!');
      } else {
        alert('❌ Application failed');
      }
    } catch (error) {
      alert('❌ Error: ' + String(error));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🔍 Job Search
        </h1>
        <p className="text-slate-600 mt-2">Find your next opportunity</p>
      </div>

      {/* Search Form */}
      <Card className="p-6 shadow-lg">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Job Title</label>
            <input
              type="text"
              placeholder="e.g., Software Engineer"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Location</label>
            <input
              type="text"
              placeholder="e.g., San Francisco or Remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={searchJobs}
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white"
            >
              <Search className="w-4 h-4 mr-2" />
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </div>
      </Card>

      {error && (
        <Card className="p-4 bg-red-50 border-2 border-red-200">
          <p className="text-red-700">⚠️ {error}</p>
        </Card>
      )}

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.length === 0 && !loading && (
          <Card className="p-8 text-center">
            <p className="text-slate-600">No jobs found. Try a different search.</p>
          </Card>
        )}

        {jobs.map((job) => (
          <Card key={job.id} className="p-6 shadow-lg hover:shadow-xl transition">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-slate-900">{job.title}</h3>
                <p className="text-purple-600 font-semibold">{job.company}</p>
                
                <div className="grid grid-cols-3 gap-4 mt-4 text-sm text-slate-600">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {job.location}
                  </div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    {job.salary}
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {job.posted_date}
                  </div>
                </div>

                <p className="mt-4 text-slate-700 line-clamp-2">{job.description}</p>
              </div>
              
              <Button
                onClick={() => handleApply(job.id, job.title, job.company)}
                className="ml-4 bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Briefcase className="w-4 h-4 mr-2" />
                Apply
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
