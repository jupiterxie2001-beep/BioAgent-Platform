'use client';

import { useState } from 'react';
import { useStore } from '../store/useStore';
import { AuthForm } from '../components/AuthForm';
import { Dashboard } from '../components/Dashboard';
import { Bot } from 'lucide-react';

export default function Home() {
  const { isLoggedIn } = useStore();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  if (isLoggedIn) {
    return <Dashboard />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="flex flex-col items-center mb-8">
        <div className="bg-white p-4 rounded-full mb-4">
          <Bot size={48} className="text-blue-600" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-2">BioAgent</h1>
        <p className="text-white/80">AI-Powered Bioinformatics Analysis Platform</p>
      </div>
      
      <AuthForm
        mode={authMode}
        onToggle={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
      />
    </div>
  );
}
