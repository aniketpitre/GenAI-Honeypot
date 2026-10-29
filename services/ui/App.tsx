import React, { useState, useEffect, useCallback } from 'react';
import { HoneyToken, Alert, View } from './types';
import { ICONS } from './constants';
import { api, auth, AuthError } from './services/api';
import Dashboard from './components/Dashboard';
import TokenManager from './components/TokenManager';
import CreateTokenModal from './components/CreateTokenModal';
import Login from './components/Login';

const POLL_MS = 5000;

const App: React.FC = () => {
  const [authed, setAuthed] = useState(!!auth.get());
  const [authError, setAuthError] = useState('');
  const [view, setView] = useState<View>('dashboard');
  const [tokens, setTokens] = useState<HoneyToken[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [isCreateModalOpen, setCreateModalOpen] = useState(false);

  const logout = useCallback((msg = '') => {
    auth.clear();
    setAuthError(msg);
    setAuthed(false);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const [t, a] = await Promise.all([api.getTokens(), api.getAlerts()]);
      setTokens(t);
      setAlerts(a);
      setLoadError('');
    } catch (e) {
      if (e instanceof AuthError) logout('Invalid admin token');
      else setLoadError('Cannot reach the API. Retrying…');
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    if (!authed) return;
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [authed, refresh]);

  const guarded = async (fn: () => Promise<unknown>) => {
    try { await fn(); await refresh(); } catch (e) {
      if (e instanceof AuthError) logout('Session expired');
      else setLoadError((e as Error).message);
    }
  };

  const handleCreateToken = async (t: Parameters<typeof api.createToken>[0]) => {
    await guarded(() => api.createToken(t));
    setCreateModalOpen(false);
    setView('tokens');
  };

  if (!authed) {
    return <Login error={authError} onSubmit={(t) => { auth.set(t); setAuthError(''); setIsLoading(true); setAuthed(true); }} />;
  }

  const NavItem: React.FC<{ targetView: View; icon: React.ReactElement; label: string }> = ({ targetView, icon, label }) => (
    <button
      onClick={() => setView(targetView)}
      className={`flex items-center space-x-3 p-3 rounded-lg w-full text-left transition-colors duration-200 ${
        view === targetView ? 'bg-sentinel-cyan text-sentinel-blue font-semibold' : 'hover:bg-sentinel-steel'
      }`}
    >
      {icon}
      <span className="hidden md:inline">{label}</span>
    </button>
  );

  return (
    <div className="flex h-screen bg-sentinel-blue font-sans">
      <nav className="w-16 md:w-64 bg-sentinel-navy p-2 md:p-4 flex flex-col justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-8 p-3">
            {ICONS.shield}
            <h1 className="text-2xl font-bold text-sentinel-light hidden md:inline">Tripwire</h1>
          </div>
          <ul className="space-y-2">
            <li><NavItem targetView="dashboard" icon={ICONS.dashboard} label="Dashboard" /></li>
            <li><NavItem targetView="tokens" icon={ICONS.key} label="Token Manager" /></li>
          </ul>
        </div>
        <div className="space-y-2">
          <button
            onClick={() => setCreateModalOpen(true)}
            className="w-full bg-sentinel-cyan text-sentinel-blue font-bold py-3 px-4 rounded-lg flex items-center justify-center space-x-2 hover:bg-opacity-80 transition-all duration-200"
          >
            {ICONS.plus}
            <span className="hidden md:inline">New Token</span>
          </button>
          <button onClick={() => logout()} className="w-full text-sm text-sentinel-silver hover:text-sentinel-light py-2">Sign out</button>
        </div>
      </nav>

      <main className="flex-1 p-4 md:p-8 overflow-y-auto">
        {loadError && <div className="mb-4 p-3 rounded bg-sentinel-red/20 text-sentinel-red text-sm">{loadError}</div>}
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-sentinel-cyan"></div>
          </div>
        ) : (
          <>
            {view === 'dashboard' && (
              <Dashboard alerts={alerts} onUpdateAlert={(a) => guarded(() => api.updateAlert(a.id, { notes: a.notes, status: a.status }))} />
            )}
            {view === 'tokens' && (
              <TokenManager
                tokens={tokens}
                onUpdateToken={(t) => guarded(() => api.updateToken(t.id, { status: t.status }))}
                onDeleteToken={(id) => guarded(() => api.deleteToken(id))}
              />
            )}
          </>
        )}
      </main>

      <CreateTokenModal isOpen={isCreateModalOpen} onClose={() => setCreateModalOpen(false)} onCreate={handleCreateToken} />
    </div>
  );
};

export default App;
