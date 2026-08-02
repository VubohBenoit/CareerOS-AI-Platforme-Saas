'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  FileText,
  Heart,
  Save,
  BarChart3,
  Search,
  Sparkles,
  TrendingUp,
  Zap,
  ArrowRight,
  Briefcase
} from 'lucide-react';

interface DashboardStats {
  applications?: { total_applications: number; accepted: number; success_rate: number };
  favorites?: { total_favorites: number };
  searches?: { total_saved_searches: number; active_alerts: number };
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Demo stats
    setStats({
      applications: { total_applications: 8, accepted: 1, success_rate: 12 },
      favorites: { total_favorites: 15 },
      searches: { total_saved_searches: 3, active_alerts: 2 },
    });
  }, []);

  return (
    <div className="space-y-12">
      {/* Header Section */}
      <div className="pt-4">
        <h1 className="text-5xl md:text-6xl font-bold text-slate-900">
          Welcome back, {user?.full_name}! 👋
        </h1>
        <p className="text-slate-600 mt-3 text-lg">
          Monitor your job search progress and find your next opportunity
        </p>
      </div>

      {/* Stats Grid - 4 Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Applications Card */}
        <Link href="/dashboard/applications">
          <div className="group bg-white rounded-xl shadow-md hover:shadow-xl border border-slate-200 p-6 transition-all hover:-translate-y-2 cursor-pointer h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg group-hover:scale-110 transition">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-blue-600 transition" />
            </div>
            <p className="text-sm font-semibold text-slate-600 uppercase tracking-wider">Applications</p>
            <div className="text-4xl font-bold text-slate-900 mt-3">
              {stats?.applications?.total_applications || 0}
            </div>
            <p className="text-sm text-blue-600 font-semibold mt-2">
              {stats?.applications?.accepted || 0} accepted
            </p>
          </div>
        </Link>

        {/* Favorites Card */}
        <Link href="/dashboard/favorites">
          <div className="group bg-white rounded-xl shadow-md hover:shadow-xl border border-slate-200 p-6 transition-all hover:-translate-y-2 cursor-pointer h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-red-100 rounded-lg group-hover:scale-110 transition">
                <Heart className="w-6 h-6 text-red-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-red-600 transition" />
            </div>
            <p className="text-sm font-semibold text-slate-600 uppercase tracking-wider">Favorites</p>
            <div className="text-4xl font-bold text-slate-900 mt-3">
              {stats?.favorites?.total_favorites || 0}
            </div>
            <p className="text-sm text-red-600 font-semibold mt-2">
              Bookmarked jobs
            </p>
          </div>
        </Link>

        {/* Saved Searches Card */}
        <Link href="/dashboard/saved-searches">
          <div className="group bg-white rounded-xl shadow-md hover:shadow-xl border border-slate-200 p-6 transition-all hover:-translate-y-2 cursor-pointer h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg group-hover:scale-110 transition">
                <Save className="w-6 h-6 text-purple-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-purple-600 transition" />
            </div>
            <p className="text-sm font-semibold text-slate-600 uppercase tracking-wider">Saved Searches</p>
            <div className="text-4xl font-bold text-slate-900 mt-3">
              {stats?.searches?.total_saved_searches || 0}
            </div>
            <p className="text-sm text-purple-600 font-semibold mt-2">
              {stats?.searches?.active_alerts || 0} active alerts
            </p>
          </div>
        </Link>

        {/* Success Rate Card */}
        <Link href="/dashboard/analytics">
          <div className="group bg-white rounded-xl shadow-md hover:shadow-xl border border-slate-200 p-6 transition-all hover:-translate-y-2 cursor-pointer h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg group-hover:scale-110 transition">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-green-600 transition" />
            </div>
            <p className="text-sm font-semibold text-slate-600 uppercase tracking-wider">Success Rate</p>
            <div className="text-4xl font-bold text-green-600 mt-3">
              {stats?.applications?.success_rate || 0}%
            </div>
            <p className="text-sm text-green-600 font-semibold mt-2">
              Acceptance rate
            </p>
          </div>
        </Link>
      </div>

      {/* Quick Actions Section */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Get Started</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/dashboard/jobs">
            <button className="w-full bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2">
              <Search className="w-5 h-5" />
              Search Jobs
            </button>
          </Link>
          <Link href="/dashboard/recommendations">
            <button className="w-full bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5" />
              AI Recommendations
            </button>
          </Link>
          <Link href="/dashboard/profile">
            <button className="w-full bg-gradient-to-br from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white font-semibold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2">
              <Briefcase className="w-5 h-5" />
              Complete Profile
            </button>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* AI Recommendations */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 p-8 hover:shadow-lg transition">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-purple-200 rounded-lg">
                <Sparkles className="w-6 h-6 text-purple-700" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">AI Recommendations</h3>
            </div>
            <p className="text-slate-700 leading-relaxed">
              Get personalized job recommendations based on your skills and career preferences
            </p>
          </div>

          {/* Analytics */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 p-8 hover:shadow-lg transition">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-blue-200 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-700" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Analytics Dashboard</h3>
            </div>
            <p className="text-slate-700 leading-relaxed">
              Track your application success rate and performance metrics in real-time
            </p>
          </div>

          {/* Saved Searches */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 p-8 hover:shadow-lg transition">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-green-200 rounded-lg">
                <Save className="w-6 h-6 text-green-700" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Saved Searches</h3>
            </div>
            <p className="text-slate-700 leading-relaxed">
              Create saved job searches and get alerts when new jobs match your criteria
            </p>
          </div>

          {/* Favorites */}
          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl border border-red-200 p-8 hover:shadow-lg transition">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-red-200 rounded-lg">
                <Heart className="w-6 h-6 text-red-700" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Save Favorites</h3>
            </div>
            <p className="text-slate-700 leading-relaxed">
              Bookmark jobs you like and come back to them later when you're ready
            </p>
          </div>
        </div>
      </div>

      {/* Tips Section */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-8">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-amber-200 rounded-lg flex-shrink-0">
            <Zap className="w-6 h-6 text-amber-700" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Pro Tip</h3>
            <p className="text-slate-700">
              Personalize each application. Customizing your cover letter and CV for each job increases your response rate by 40%+. Use our AI tools to optimize your materials for each position.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
