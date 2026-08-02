'use client';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Lightbulb, Trophy } from 'lucide-react';

export default function InterviewPrepPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🎯 Interview Prep
        </h1>
        <p className="text-slate-600 mt-2">Practice with AI-powered mock interviews</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { type: 'Behavioral', count: 15, icon: '💭' },
          { type: 'Technical', count: 12, icon: '💻' },
          { type: 'Role-Specific', count: 8, icon: '🎯' },
        ].map((cat) => (
          <Card key={cat.type} className="p-6 shadow-lg hover:shadow-xl transition cursor-pointer">
            <p className="text-3xl mb-2">{cat.icon}</p>
            <h3 className="font-bold text-lg mb-1">{cat.type}</h3>
            <p className="text-sm text-slate-600">{cat.count} questions</p>
            <Button className="w-full mt-4 bg-blue-600 text-white">Practice Now</Button>
          </Card>
        ))}
      </div>

      <Card className="p-8 shadow-lg">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-yellow-500" />
          Interview Tips
        </h3>
        <ul className="space-y-2 text-slate-700">
          <li>✓ Use the STAR method for behavioral questions</li>
          <li>✓ Research the company thoroughly beforehand</li>
          <li>✓ Practice speaking your answers out loud</li>
          <li>✓ Ask thoughtful questions about the role</li>
          <li>✓ Follow up within 24 hours</li>
        </ul>
      </Card>
    </div>
  );
}
