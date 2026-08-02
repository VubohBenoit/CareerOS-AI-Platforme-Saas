'use client';
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Share2, Gift } from 'lucide-react';

export default function ReferralsPage() {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = () => {
    navigator.clipboard.writeText('https://careerosai.com?ref=BENOIT123');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🎁 Referral Program
        </h1>
        <p className="text-slate-600 mt-2">Earn rewards by referring friends to CareerOS AI</p>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        <Card className="p-4 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
          <p className="text-sm text-slate-600">Referrals</p>
          <p className="text-3xl font-bold text-blue-600">12</p>
        </Card>
        <Card className="p-4 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
          <p className="text-sm text-slate-600">Successful</p>
          <p className="text-3xl font-bold text-green-600">3</p>
        </Card>
        <Card className="p-4 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
          <p className="text-sm text-slate-600">Earned</p>
          <p className="text-3xl font-bold text-purple-600">$450</p>
        </Card>
        <Card className="p-4 shadow-lg bg-gradient-to-br from-amber-50 to-amber-100">
          <p className="text-sm text-slate-600">Tier</p>
          <p className="text-3xl font-bold text-amber-600">Silver</p>
        </Card>
      </div>

      <Card className="p-8 shadow-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <h2 className="text-2xl font-bold mb-4">Share Your Link</h2>
        <p className="mb-6">Earn $50 for each friend who signs up and gets hired!</p>
        
        <div className="bg-white/20 p-4 rounded-lg mb-4 flex items-center justify-between">
          <code className="text-sm">https://careerosai.com?ref=BENOIT123</code>
          <Button 
            onClick={handleCopyLink}
            className="bg-white text-blue-600 hover:bg-slate-50"
          >
            {copied ? 'Copied!' : 'Copy'}
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <Button className="bg-white text-blue-600 hover:bg-slate-50">
            <Share2 className="w-4 h-4 mr-2" />
            LinkedIn
          </Button>
          <Button className="bg-white text-blue-600 hover:bg-slate-50">
            <Share2 className="w-4 h-4 mr-2" />
            Twitter
          </Button>
          <Button className="bg-white text-blue-600 hover:bg-slate-50">
            <Share2 className="w-4 h-4 mr-2" />
            Email
          </Button>
        </div>
      </Card>

      <Card className="p-8 shadow-lg">
        <h3 className="text-xl font-bold mb-6">Rewards Tiers</h3>
        <div className="grid md:grid-cols-2 gap-6">
          {[
            { tier: 'Bronze', referrals: 3, reward: '$50' },
            { tier: 'Silver', referrals: 5, reward: '$150' },
            { tier: 'Gold', referrals: 10, reward: '$500' },
            { tier: 'Platinum', referrals: 20, reward: '$1,500' },
          ].map((t) => (
            <div key={t.tier} className="border-2 border-slate-200 p-6 rounded-lg">
              <h4 className="text-lg font-bold mb-2">{t.tier}</h4>
              <p className="text-2xl font-bold text-blue-600 mb-2">{t.reward}</p>
              <p className="text-sm text-slate-600">{t.referrals} successful referrals</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
