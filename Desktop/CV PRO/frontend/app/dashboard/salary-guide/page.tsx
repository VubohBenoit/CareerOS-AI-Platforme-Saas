'use client';
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp, Target, DollarSign, Zap } from 'lucide-react';

export default function SalaryGuidePage() {
  const [formData, setFormData] = useState({
    job_title: '',
    location: '',
    experience_years: 3,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          💰 Salary Guide
        </h1>
        <p className="text-slate-600 mt-2">Get market-based salary estimates and negotiation tips</p>
      </div>

      <Card className="p-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4">Market Salary Ranges</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { role: 'Software Engineer', entry: '$100k', mid: '$145k', senior: '$200k' },
            { role: 'Data Scientist', entry: '$120k', mid: '$160k', senior: '$220k' },
            { role: 'Product Manager', entry: '$130k', mid: '$180k', senior: '$250k' },
          ].map((item) => (
            <div key={item.role} className="p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
              <h4 className="font-bold text-slate-900 mb-3">{item.role}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Entry</span>
                  <span className="font-semibold text-blue-600">{item.entry}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Mid</span>
                  <span className="font-semibold text-purple-600">{item.mid}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Senior</span>
                  <span className="font-semibold text-indigo-600">{item.senior}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-8 shadow-lg bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-200">
        <div className="flex items-start gap-4">
          <Zap className="w-8 h-8 text-amber-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-amber-900 mb-3">Negotiation Tips</h3>
            <ul className="space-y-2 text-amber-800">
              <li>✅ Research your local market rate</li>
              <li>✅ Wait 48 hours before responding</li>
              <li>✅ Counter-offer 10-15% above if below market</li>
              <li>✅ Negotiate the whole package</li>
              <li>✅ Get everything in writing</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
