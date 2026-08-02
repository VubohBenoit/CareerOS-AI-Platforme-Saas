'use client';
import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, FileText, Save, AlertCircle } from 'lucide-react';

export default function ProfilePage() {
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    bio: '',
    skills: [] as string[],
  });
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load profile from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setProfile(JSON.parse(userData));
    }
  }, []);

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profile)
      });

      if (response.ok) {
        setMessage('✅ Profile saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('❌ Failed to save profile');
      }
    } catch (error) {
      setMessage('❌ Error: ' + String(error));
    } finally {
      setLoading(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      setMessage('❌ No file selected');
      return;
    }

    setLoading(true);
    setMessage('Uploading...');

    try {
      // Get user from localStorage
      const userData = localStorage.getItem('user');
      let userId = 'unknown';
      if (userData) {
        try {
          const user = JSON.parse(userData);
          userId = user.id || user.email || 'unknown';
        } catch (e) {
          console.log('Could not parse user data');
        }
      }

      console.log('📤 Uploading file:', file.name, 'User ID:', userId);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);

      const apiUrl = 'http://localhost:8000/api/v1/documents/upload-resume';
      console.log('📍 API URL:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData
      });

      console.log('📊 Response status:', response.status);

      const data = await response.json();
      console.log('📦 Response data:', data);

      if (response.ok) {
        setResume(data);
        setMessage('✅ Resume uploaded successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(`❌ Upload failed: ${data.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Upload error:', error);
      setMessage('❌ Error: ' + String(error));
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAddSkill = () => {
    const skills = profile.skills || [];
    if (newSkill.trim() && !skills.includes(newSkill)) {
      setProfile({
        ...profile,
        skills: [...skills, newSkill]
      });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setProfile({
      ...profile,
      skills: profile.skills.filter(s => s !== skill)
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          👤 Profile
        </h1>
        <p className="text-slate-600 mt-2">Manage your professional profile</p>
      </div>

      {message && (
        <Card className={`p-4 ${message.includes('✅') ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
          <p className={message.includes('✅') ? 'text-green-700' : 'text-red-700'}>{message}</p>
        </Card>
      )}

      {/* Profile Info */}
      <Card className="p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Basic Information</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Full Name</label>
            <input
              type="text"
              value={profile.full_name}
              onChange={(e) => setProfile({...profile, full_name: e.target.value})}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg text-black dark:text-white dark:bg-slate-700"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Email</label>
            <input
              type="email"
              value={profile.email}
              disabled
              className="w-full px-4 py-2 border border-slate-300 rounded-lg bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
            />
            <p className="text-xs text-slate-500 mt-1">Email cannot be changed</p>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Bio</label>
            <textarea
              value={profile.bio || ''}
              onChange={(e) => setProfile({...profile, bio: e.target.value})}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg h-24 text-black dark:text-white dark:bg-slate-700"
              placeholder="Tell us about yourself..."
            />
          </div>

          <Button
            onClick={handleSaveProfile}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
          >
            <Save className="w-4 h-4 mr-2" />
            {loading ? 'Saving...' : 'Save Profile'}
          </Button>
        </div>
      </Card>

      {/* Skills */}
      <Card className="p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Skills</h2>
        
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-black dark:text-white dark:bg-slate-700"
              placeholder="Add a skill (e.g., Python, React)"
            />
            <Button
              onClick={handleAddSkill}
              className="bg-blue-600 text-white"
            >
              Add
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            {(profile.skills || []).map((skill) => (
              <div
                key={skill}
                className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2"
              >
                {skill}
                <button
                  onClick={() => handleRemoveSkill(skill)}
                  className="hover:text-red-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Resume Upload */}
      <Card className="p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <FileText className="w-6 h-6" />
          Resume
        </h2>

        <div className="space-y-4">
          {resume ? (
            <div className="bg-green-50 border-2 border-green-200 p-4 rounded-lg">
              <p className="font-semibold text-green-700">✅ Resume Uploaded</p>
              <p className="text-sm text-green-600 mt-2">
                File: {resume.filename}
              </p>
              <p className="text-sm text-green-600">
                Size: {(resume.file_size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div className="border-2 border-dashed border-slate-300 p-8 rounded-lg text-center hover:bg-slate-50 transition">
              <Upload className="w-12 h-12 text-slate-400 mx-auto mb-2" />
              <p className="font-semibold text-slate-700">Upload Resume</p>
              <p className="text-sm text-slate-500 mt-1">PDF, DOC, DOCX, or TXT (max 5MB)</p>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleResumeUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Upload className="w-4 h-4" />
            {loading ? 'Uploading...' : resume ? 'Update Resume' : 'Upload Resume'}
          </button>
        </div>
      </Card>

      {/* Info Box */}
      <Card className="p-4 bg-blue-50 border-2 border-blue-200">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-semibold">💡 Tip</p>
            <p className="mt-1">Keep your profile up-to-date! This helps us find better job matches for you.</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
