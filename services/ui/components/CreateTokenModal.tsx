import React, { useState } from 'react';
import { TokenType, TOKEN_TYPE_LABELS } from '../types';
import { ICONS } from '../constants';
import { api } from '../services/api';
import Modal from './common/Modal';

interface CreateTokenModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (token: { name: string; type: TokenType; decoy_url?: string }) => Promise<void>;
}

const HINTS: Record<Exclude<TokenType, 'url'>, string> = {
  pixel: 'A unique 1x1 tracking pixel URL. Embed it in an email, web page or document; fetching it raises an alert.',
  document: 'A Word document that loads a remote image when opened. Download it from the Token Manager and plant it as bait.',
};

const CreateTokenModal: React.FC<CreateTokenModalProps> = ({ isOpen, onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [type, setType] = useState<TokenType>('url');
  const [prompt, setPrompt] = useState('');
  const [generatedUrls, setGeneratedUrls] = useState<string[]>([]);
  const [selectedUrl, setSelectedUrl] = useState('');
  const [isLoadingUrls, setIsLoadingUrls] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateUrls = async () => {
    if (!prompt) { setError('Please enter a prompt to generate URLs.'); return; }
    setIsLoadingUrls(true);
    setError('');
    setGeneratedUrls([]);
    try {
      const urls = await api.generateUrls(prompt);
      setGeneratedUrls(urls);
      if (urls.length > 0) setSelectedUrl(urls[0]);
    } catch (e) {
      setError('Failed to generate URLs. Please try again.');
      console.error(e);
    } finally {
      setIsLoadingUrls(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) { setError('Token name is required.'); return; }
    if (type === 'url' && !selectedUrl) { setError('Please generate and select a URL.'); return; }
    try {
      await onCreate({ name, type, decoy_url: type === 'url' ? selectedUrl : undefined });
      setName(''); setType('url'); setPrompt(''); setGeneratedUrls([]); setSelectedUrl(''); setError('');
    } catch {
      setError('Could not create the token.');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Honey Token">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="token-name" className="block text-sm font-medium text-sentinel-silver mb-2">Token Name</label>
          <input
            type="text" id="token-name" value={name} onChange={(e) => setName(e.target.value)}
            placeholder="e.g., 'Q4 Financials - Sharepoint'"
            className="w-full bg-sentinel-blue border border-sentinel-steel rounded-md p-2 focus:ring-2 focus:ring-sentinel-cyan focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-sentinel-silver mb-2">Token Type</label>
          <div className="flex space-x-4">
            {(Object.keys(TOKEN_TYPE_LABELS) as TokenType[]).map((t) => (
              <button
                key={t} type="button" onClick={() => setType(t)}
                className={`px-4 py-2 rounded-md transition-colors text-sm font-semibold ${
                  type === t ? 'bg-sentinel-cyan text-sentinel-blue' : 'bg-sentinel-steel/50 hover:bg-sentinel-steel'
                }`}
              >
                {TOKEN_TYPE_LABELS[t]}
              </button>
            ))}
          </div>
        </div>

        {type === 'url' ? (
          <div className="space-y-4 p-4 border border-dashed border-sentinel-steel rounded-md">
            <h3 className="font-semibold text-lg">AI-Powered Decoy URL</h3>
            <div>
              <label htmlFor="url-prompt" className="block text-sm font-medium text-sentinel-silver mb-2">Deception Prompt</label>
              <div className="flex space-x-2">
                <input
                  type="text" id="url-prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., A link to an exposed AWS S3 bucket"
                  className="flex-grow bg-sentinel-blue border border-sentinel-steel rounded-md p-2 focus:ring-2 focus:ring-sentinel-cyan focus:outline-none"
                />
                <button
                  type="button" onClick={handleGenerateUrls} disabled={isLoadingUrls}
                  className="bg-sentinel-steel px-4 py-2 rounded-md font-semibold hover:bg-sentinel-silver transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoadingUrls ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-sentinel-light"></div> : ICONS.brain}
                  <span className="ml-2">Generate</span>
                </button>
              </div>
            </div>
            {generatedUrls.length > 0 && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-sentinel-silver">Select a decoy URL (the trap link is generated for you):</label>
                {generatedUrls.map((url, index) => (
                  <div key={index} className="flex items-center bg-sentinel-blue p-2 rounded-md border border-sentinel-steel">
                    <input
                      type="radio" id={`url-option-${index}`} name="url-option" value={url}
                      checked={selectedUrl === url} onChange={(e) => setSelectedUrl(e.target.value)}
                      className="form-radio h-4 w-4 text-sentinel-cyan bg-sentinel-blue border-sentinel-steel focus:ring-sentinel-cyan"
                    />
                    <label htmlFor={`url-option-${index}`} className="ml-3 block text-sm font-mono text-sentinel-light truncate">{url}</label>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="p-4 bg-sentinel-blue border border-dashed border-sentinel-steel rounded-md font-mono text-sm text-sentinel-silver">
            <p className="font-bold mb-2 text-sentinel-light">{TOKEN_TYPE_LABELS[type]}</p>
            <p>{HINTS[type]}</p>
          </div>
        )}

        {error && <p className="text-sentinel-red text-sm">{error}</p>}

        <div className="flex justify-end space-x-4">
          <button type="button" onClick={onClose} className="px-4 py-2 rounded-md bg-sentinel-steel text-sentinel-light font-semibold hover:bg-sentinel-silver transition-colors">Cancel</button>
          <button type="submit" className="px-4 py-2 rounded-md bg-sentinel-cyan text-sentinel-blue font-bold hover:bg-opacity-80 transition-colors">Create Token</button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateTokenModal;
