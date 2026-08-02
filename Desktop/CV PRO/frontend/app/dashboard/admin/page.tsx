'use client';
import { Card } from '@/components/ui/card';
import { BarChart3, Users, Zap, TrendingUp } from 'lucide-react';

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          📊 Admin Dashboard
        </h1>
        <p className="text-slate-600 mt-2">Platform analytics and management</p>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        <Card className="p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Total Users</p>
              <p className="text-3xl font-bold text-blue-600">1,024</p>
            </div>
            <Users className="w-8 h-8 text-blue-400" />
          </div>
        </Card>
        
        <Card className="p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Active This Month</p>
              <p className="text-3xl font-bold text-purple-600">756</p>
            </div>
            <Zap className="w-8 h-8 text-purple-400" />
          </div>
        </Card>

        <Card className="p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Applications</p>
              <p className="text-3xl font-bold text-green-600">3,456</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-400" />
          </div>
        </Card>

        <Card className="p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">MRR</p>
              <p className="text-3xl font-bold text-amber-600">$15k</p>
            </div>
            <BarChart3 className="w-8 h-8 text-amber-400" />
          </div>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-slate-600">API Uptime</span>
              <span className="font-bold text-green-600">99.98%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Database Status</span>
              <span className="font-bold text-green-600">Healthy</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Response Time</span>
              <span className="font-bold text-blue-600">145ms</span>
            </div>
          </div>
        </Card>

        <Card className="p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4">Top Companies</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Google</span>
              <span className="font-semibold">124 apps</span>
            </div>
            <div className="flex justify-between">
              <span>Microsoft</span>
              <span className="font-semibold">98 apps</span>
            </div>
            <div className="flex justify-between">
              <span>Amazon</span>
              <span className="font-semibold">87 apps</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
