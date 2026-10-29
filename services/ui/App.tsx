
import React, { useState, useEffect, useCallback } from 'react';
import { HoneyToken, Alert, View, TokenStatus } from './types';
import { MOCK_TOKENS, MOCK_ALERTS, ICONS } from './constants';
import Dashboard from './components/Dashboard';
import TokenManager from './components/TokenManager';
import CreateTokenModal from './components/CreateTokenModal';

// Mock API functions to simulate backend
const api = {
  getTokens: async (): Promise<HoneyToken[]> => {
    await new Promise(res => setTimeout(res, 500));
    return JSON.parse(localStorage.getItem('tokens') || JSON.stringify(MOCK_TOKENS));
  },
  getAlerts: async (): Promise<Alert[]> => {
    await new Promise(res => setTimeout(res, 500));
    return JSON.parse(localStorage.getItem('alerts') || JSON.stringify(MOCK_ALERTS));
  },
  saveTokens: (tokens: HoneyToken[]) => {
    localStorage.setItem('tokens', JSON.stringify(tokens));
  },
  saveAlerts: (alerts: Alert[]) => {
    localStorage.setItem('alerts', JSON.stringify(alerts));
  }
};

if (!localStorage.getItem('tokens')) {
  api.saveTokens(MOCK_TOKENS);
}
if (!localStorage.getItem('alerts')) {
  api.saveAlerts(MOCK_ALERTS);
}

const App: React.FC = () => {
  const [view, setView] = useState<View>('dashboard');
  const [tokens, setTokens] = useState<HoneyToken[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setCreateModalOpen] = useState(false);
  const [isTrapped, setIsTrapped] = useState(false);

  // This effect runs once on mount to check for a triggered honey token URL
  useEffect(() => {
    const handleTrap = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const tokenId = urlParams.get('token_id');

      if (tokenId) {
        // Clean the URL immediately to prevent re-triggering on refresh
        window.history.replaceState({}, document.title, window.location.pathname);

        const allTokens: HoneyToken[] = JSON.parse(localStorage.getItem('tokens') || '[]');
        const trappedToken = allTokens.find(t => t.id === tokenId);

        if (trappedToken && trappedToken.status === TokenStatus.Active) {
          // Token is valid and active, trigger alert
          const newAlert: Alert = {
            id: `alert-${Date.now()}`,
            tokenId: trappedToken.id,
            tokenName: trappedToken.name,
            timestamp: new Date().toISOString(),
            ip: `1${Math.floor(Math.random() * 99)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`, // Mock IP
            geolocation: { city: 'Unknown', country: 'Unknown', lat: 0, lon: 0 }, // Mock Geo
            userAgent: navigator.userAgent,
            requestHeaders: { 'Referrer': document.referrer || 'N/A' },
            notes: 'Alert triggered by direct URL access.',
            status: 'New',
          };

          // Update alerts in storage
          const allAlerts: Alert[] = JSON.parse(localStorage.getItem('alerts') || '[]');
          const updatedAlerts = [newAlert, ...allAlerts];
          api.saveAlerts(updatedAlerts);

          // Update token's alert count in storage
          const updatedTokens = allTokens.map(t =>
            t.id === tokenId ? { ...t, alertCount: t.alertCount + 1 } : t
          );
          api.saveTokens(updatedTokens);
          
          setIsTrapped(true);
        }
      }
    };

    handleTrap();
  }, []);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    const [fetchedTokens, fetchedAlerts] = await Promise.all([
      api.getTokens(),
      api.getAlerts(),
    ]);
    setTokens(fetchedTokens);
    setAlerts(fetchedAlerts.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()));
    setIsLoading(false);
  }, []);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.get('token_id')) {
      fetchData();
    }
  }, [fetchData]);

  // Simulate WebSocket for live alerts
  useEffect(() => {
    const interval = setInterval(() => {
      setAlerts(prevAlerts => {
        if (tokens.length === 0) return prevAlerts;
        const randomToken = tokens[Math.floor(Math.random() * tokens.length)];
        const newAlert: Alert = {
          id: `alert-${Date.now()}`,
          tokenId: randomToken.id,
          tokenName: randomToken.name,
          timestamp: new Date().toISOString(),
          ip: `1${Math.floor(Math.random() * 99)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
          geolocation: {
            city: 'Unknown',
            country: 'Unknown',
            lat: Math.random() * 180 - 90,
            lon: Math.random() * 360 - 180,
          },
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
          requestHeaders: { 'Accept-Language': 'en-US,en;q=0.9' },
          notes: '',
          status: 'New',
        };
        const updatedAlerts = [newAlert, ...prevAlerts];
        api.saveAlerts(updatedAlerts);
        return updatedAlerts;
      });
    }, 15000); // New alert every 15 seconds

    return () => clearInterval(interval);
  }, [tokens]);


  const handleCreateToken = (token: HoneyToken) => {
    const updatedTokens = [...tokens, token];
    setTokens(updatedTokens);
    api.saveTokens(updatedTokens);
    setCreateModalOpen(false);
    setView('tokens');
  };

  const handleUpdateToken = (updatedToken: HoneyToken) => {
    const updatedTokens = tokens.map(t => t.id === updatedToken.id ? updatedToken : t);
    setTokens(updatedTokens);
    api.saveTokens(updatedTokens);
  };
  
  const handleDeleteToken = (tokenId: string) => {
    const updatedTokens = tokens.filter(t => t.id !== tokenId);
    setTokens(updatedTokens);
    api.saveTokens(updatedTokens);
  };

  const handleUpdateAlert = (updatedAlert: Alert) => {
    const updatedAlerts = alerts.map(a => a.id === updatedAlert.id ? updatedAlert : a);
    setAlerts(updatedAlerts);
    api.saveAlerts(updatedAlerts);
  };

  const NavItem: React.FC<{
    targetView: View;
    icon: React.ReactElement;
    label: string;
  }> = ({ targetView, icon, label }) => (
    <button
      onClick={() => setView(targetView)}
      className={`flex items-center space-x-3 p-3 rounded-lg w-full text-left transition-colors duration-200 ${
        view === targetView
          ? 'bg-sentinel-cyan text-sentinel-blue font-semibold'
          : 'hover:bg-sentinel-steel'
      }`}
    >
      {icon}
      <span className="hidden md:inline">{label}</span>
    </button>
  );

  if (isTrapped) {
    useEffect(() => {
        const timer = setTimeout(() => {
            window.location.href = window.location.pathname;
        }, 3000); // 3-second delay

        return () => clearTimeout(timer);
    }, []); // Run only once when the component mounts

    return (
      <div className="flex flex-col justify-center items-center h-screen bg-black text-red-500 font-mono">
        <div className="text-center p-4">
          <p className="text-6xl font-bold animate-pulse">[!]</p>
          <h1 className="text-4xl md:text-6xl mt-4">403 FORBIDDEN</h1>
          <p className="text-lg md:text-2xl mt-4">Access Denied.</p>
          <p className="text-xs md:text-sm mt-8 text-gray-600">[TRIPWIRE ALERT TRIGGERED - YOUR ACTIVITY HAS BEEN LOGGED]</p>
          <p className="text-sm mt-4 text-sentinel-silver animate-pulse">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

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
        <button 
          onClick={() => setCreateModalOpen(true)}
          className="w-full bg-sentinel-cyan text-sentinel-blue font-bold py-3 px-4 rounded-lg flex items-center justify-center space-x-2 hover:bg-opacity-80 transition-all duration-200"
        >
          {ICONS.plus}
          <span className="hidden md:inline">New Token</span>
        </button>
      </nav>

      <main className="flex-1 p-4 md:p-8 overflow-y-auto">
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-sentinel-cyan"></div>
          </div>
        ) : (
          <>
            {view === 'dashboard' && <Dashboard alerts={alerts} onUpdateAlert={handleUpdateAlert} />}
            {view === 'tokens' && <TokenManager tokens={tokens} onUpdateToken={handleUpdateToken} onDeleteToken={handleDeleteToken} />}
          </>
        )}
      </main>
      
      <CreateTokenModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setCreateModalOpen(false)} 
        onCreate={handleCreateToken}
      />
    </div>
  );
};

export default App;
