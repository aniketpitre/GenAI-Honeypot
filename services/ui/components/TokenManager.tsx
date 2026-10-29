
import React, { useState } from 'react';
import { HoneyToken, TokenStatus } from '../types';
import { ICONS } from '../constants';

interface TokenManagerProps {
  tokens: HoneyToken[];
  onUpdateToken: (token: HoneyToken) => void;
  onDeleteToken: (tokenId: string) => void;
}

const TokenManager: React.FC<TokenManagerProps> = ({ tokens, onUpdateToken, onDeleteToken }) => {
  const [copiedTokenId, setCopiedTokenId] = useState<string | null>(null);

  const handleStatusToggle = (token: HoneyToken) => {
    const newStatus = token.status === TokenStatus.Active ? TokenStatus.Disabled : TokenStatus.Active;
    onUpdateToken({ ...token, status: newStatus });
  };

  const handleCopy = (token: HoneyToken) => {
    navigator.clipboard.writeText(token.value).then(() => {
      setCopiedTokenId(token.id);
      setTimeout(() => setCopiedTokenId(null), 2000); // Reset after 2 seconds
    }).catch(err => {
      console.error('Failed to copy text: ', err);
    });
  };
  
  return (
    <div>
      <h1 className="text-3xl font-bold text-sentinel-light mb-6">Token Manager</h1>
      <div className="bg-sentinel-navy rounded-lg overflow-x-auto shadow-lg">
        <table className="w-full text-left">
          <thead className="bg-sentinel-steel/20">
            <tr>
              <th className="p-4 min-w-[200px]">Name / Type</th>
              <th className="p-4 min-w-[300px] hidden md:table-cell">Token Value</th>
              <th className="p-4">Alerts</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {tokens.map(token => (
              <tr key={token.id} className="border-t border-sentinel-steel/30 hover:bg-sentinel-steel/10">
                <td className="p-4">
                  <div className="font-semibold">{token.name}</div>
                  <div className="text-xs text-sentinel-silver">{token.type}</div>
                </td>
                <td className="p-4 text-sentinel-silver hidden md:table-cell">
                   <div className="flex items-center space-x-2">
                       <input 
                         type="text" 
                         readOnly 
                         value={token.value} 
                         title={token.value}
                         className="w-full bg-sentinel-blue border border-sentinel-steel rounded-md p-1 font-mono text-xs truncate" 
                       />
                       <button onClick={() => handleCopy(token)} className="p-2 hover:bg-sentinel-steel rounded-full flex-shrink-0" title={copiedTokenId === token.id ? "Copied!" : "Copy URL"}>
                         {copiedTokenId === token.id ? 
                            <span className="text-sentinel-cyan">{ICONS.check}</span> : 
                            ICONS.copy
                         }
                       </button>
                   </div>
                </td>
                <td className="p-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-sm font-semibold ${token.alertCount > 0 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                        {token.alertCount}
                    </span>
                </td>
                <td className="p-4">
                  <button onClick={() => handleStatusToggle(token)} className="flex items-center space-x-2">
                    <div className={`w-4 h-4 rounded-full ${token.status === TokenStatus.Active ? 'bg-sentinel-cyan' : 'bg-sentinel-silver'}`}></div>
                    <span>{token.status}</span>
                  </button>
                </td>
                <td className="p-4 text-right">
                  <div className="flex justify-end space-x-2">
                    <button className="p-2 hover:bg-sentinel-steel rounded-full">{ICONS.edit}</button>
                    <button onClick={() => onDeleteToken(token.id)} className="p-2 hover:bg-sentinel-steel rounded-full text-sentinel-red">{ICONS.trash}</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TokenManager;