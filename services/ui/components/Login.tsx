import React, { useState } from 'react';
import { ICONS } from '../constants';

const Login: React.FC<{ onSubmit: (token: string) => void; error?: string }> = ({ onSubmit, error }) => {
  const [token, setToken] = useState('');
  return (
    <div className="flex h-screen items-center justify-center bg-sentinel-blue">
      <form
        onSubmit={(e) => { e.preventDefault(); if (token) onSubmit(token); }}
        className="bg-sentinel-navy p-8 rounded-lg shadow-2xl w-full max-w-sm space-y-4"
      >
        <div className="flex items-center space-x-3">{ICONS.shield}<h1 className="text-2xl font-bold">Tripwire</h1></div>
        <label htmlFor="admin-token" className="block text-sm text-sentinel-silver">Admin token</label>
        <input
          id="admin-token" type="password" autoFocus value={token} onChange={(e) => setToken(e.target.value)}
          className="w-full bg-sentinel-blue border border-sentinel-steel rounded-md p-2 focus:ring-2 focus:ring-sentinel-cyan focus:outline-none"
        />
        {error && <p className="text-sentinel-red text-sm">{error}</p>}
        <button type="submit" className="w-full bg-sentinel-cyan text-sentinel-blue font-bold py-2 rounded-md hover:bg-opacity-80">Sign in</button>
      </form>
    </div>
  );
};

export default Login;
