'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Profile {
  id?: string;
  phone?: string;
  address?: string;
  about_me?: string;
  current_title?: string;
  years_experience?: number;
  preferred_contract?: string;
  preferred_locations?: string[];
  salary_min_expectations?: number;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/profile`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        setProfile({});
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      setProfile({});
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/profile`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profile),
        }
      );

      if (response.ok) {
        setMessage('✅ Profile updated successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('❌ Failed to save profile');
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
      setMessage('❌ Error saving profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-slate-600 mt-4">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Profile Settings
        </h1>
        <p className="text-slate-600 mt-2">
          Complete your profile to get better recommendations
        </p>
      </div>

      {/* Success/Error Message */}
      {message && (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
          {message}
        </div>
      )}

      {/* Profile Form */}
      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal Info */}
        <div className="bg-white border border-slate-200 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Personal Information</h2>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                Current Job Title
              </label>
              <Input
                placeholder="e.g., Senior React Developer"
                value={profile?.current_title || ''}
                onChange={(e) => setProfile({ ...profile!, current_title: e.target.value })}
                className="border-slate-200"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                Phone
              </label>
              <Input
                type="tel"
                placeholder="+33 6 12 34 56 78"
                value={profile?.phone || ''}
                onChange={(e) => setProfile({ ...profile!, phone: e.target.value })}
                className="border-slate-200"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                Address
              </label>
              <Input
                placeholder="City, Country"
                value={profile?.address || ''}
                onChange={(e) => setProfile({ ...profile!, address: e.target.value })}
                className="border-slate-200"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                About Me
              </label>
              <textarea
                placeholder="Tell us about yourself..."
                value={profile?.about_me || ''}
                onChange={(e) => setProfile({ ...profile!, about_me: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                rows={4}
              />
            </div>
          </div>
        </div>

        {/* Experience & Preferences */}
        <div className="bg-white border border-slate-200 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Experience & Preferences</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-semibold text-slate-700 mb-2 block">
                  Years of Experience
                </label>
                <Input
                  type="number"
                  min="0"
                  max="60"
                  placeholder="5"
                  value={profile?.years_experience || ''}
                  onChange={(e) => setProfile({ ...profile!, years_experience: parseInt(e.target.value) })}
                  className="border-slate-200"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-slate-700 mb-2 block">
                  Contract Type
                </label>
                <select
                  value={profile?.preferred_contract || ''}
                  onChange={(e) => setProfile({ ...profile!, preferred_contract: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">Select...</option>
                  <option value="CDI">CDI (Permanent)</option>
                  <option value="CDD">CDD (Contract)</option>
                  <option value="FREELANCE">Freelance</option>
                  <option value="STAGE">Internship</option>
                  <option value="ALTERNANCE">Alternance</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                Min Salary Expectations (€)
              </label>
              <Input
                type="number"
                placeholder="50000"
                value={profile?.salary_min_expectations || ''}
                onChange={(e) => setProfile({ ...profile!, salary_min_expectations: parseInt(e.target.value) })}
                className="border-slate-200"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 mb-2 block">
                Preferred Locations
              </label>
              <Input
                placeholder="Paris, Remote, Lyon (comma-separated)"
                value={(profile?.preferred_locations || []).join(', ')}
                onChange={(e) => setProfile({ ...profile!, preferred_locations: e.target.value.split(',').map(l => l.trim()) })}
                className="border-slate-200"
              />
            </div>
          </div>
        </div>

        {/* Skills Section */}
        <div className="bg-white border border-slate-200 rounded-2xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-slate-900">Skills</h2>
            <a href="/profile/resume" className="text-blue-600 hover:text-blue-700 font-medium">
              Upload Resume →
            </a>
          </div>
          <p className="text-slate-600">
            Upload your resume to automatically extract and populate your skills.
          </p>
        </div>

        {/* Save Button */}
        <div className="flex gap-4">
          <Button
            type="submit"
            disabled={saving}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-8 py-3"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  );
}
