'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';

interface ParsedData {
  email?: string;
  phone?: string;
  name?: string;
  years_experience?: number;
  skills?: string[];
  education?: string[];
}

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState<ParsedData | null>(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setParsed(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setLoading(true);
      setMessage('');

      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/resume-parser/parse`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        }
      );

      if (response.ok) {
        const data = await response.json();
        setParsed(data.parsed_data || data);
        setMessage('✅ Resume parsed successfully!');
      } else {
        setMessage('❌ Failed to parse resume');
      }
    } catch (error) {
      console.error('Failed to upload resume:', error);
      setMessage('❌ Error uploading resume');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFill = async () => {
    if (!parsed) return;

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/profile`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            years_experience: parsed.years_experience,
            // Skills will be added separately
          }),
        }
      );

      if (response.ok) {
        setMessage('✅ Profile updated with resume data!');
        setTimeout(() => {
          window.location.href = '/dashboard/profile';
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to auto-fill profile:', error);
      setMessage('❌ Error updating profile');
    }
  };

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Resume Parser
        </h1>
        <p className="text-slate-600 mt-2">
          Upload your resume to automatically extract skills and experience
        </p>
      </div>

      {/* Upload Section */}
      <form onSubmit={handleUpload} className="bg-white border border-slate-200 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Upload Resume</h2>

        {/* File Drop Area */}
        <label className="block cursor-pointer">
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-12 text-center hover:border-blue-400 transition">
            <div className="text-4xl mb-3">📄</div>
            <p className="font-semibold text-slate-900">
              {file ? file.name : 'Drop your resume here'}
            </p>
            <p className="text-sm text-slate-600 mt-1">
              or click to select (PDF, DOC, DOCX)
            </p>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx"
              className="hidden"
            />
          </div>
        </label>

        {message && (
          <div className={`mt-4 p-3 rounded-lg ${
            message.includes('✅')
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}>
            {message}
          </div>
        )}

        <div className="mt-6">
          <Button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3"
          >
            {loading ? 'Parsing...' : 'Parse Resume'}
          </Button>
        </div>
      </form>

      {/* Parsed Data Section */}
      {parsed && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Extracted Information</h2>

          <div className="space-y-6">
            {parsed.name && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-1">Name</p>
                <p className="text-lg text-slate-900">{parsed.name}</p>
              </div>
            )}

            {parsed.email && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-1">Email</p>
                <p className="text-slate-900">{parsed.email}</p>
              </div>
            )}

            {parsed.phone && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-1">Phone</p>
                <p className="text-slate-900">{parsed.phone}</p>
              </div>
            )}

            {parsed.years_experience && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-1">
                  Years of Experience
                </p>
                <p className="text-slate-900">{parsed.years_experience} years</p>
              </div>
            )}

            {parsed.skills && parsed.skills.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-3">Skills</p>
                <div className="flex flex-wrap gap-2">
                  {parsed.skills.map((skill) => (
                    <span
                      key={skill}
                      className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {parsed.education && parsed.education.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase mb-2">Education</p>
                <ul className="space-y-1">
                  {parsed.education.map((edu) => (
                    <li key={edu} className="text-slate-700">
                      • {edu}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <Button
            onClick={handleAutoFill}
            className="mt-8 w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3"
          >
            ✅ Auto-fill Profile
          </Button>
        </div>
      )}
    </div>
  );
}
