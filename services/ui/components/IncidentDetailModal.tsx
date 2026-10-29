
import React, { useState } from 'react';
import { Alert } from '../types';
import { ICONS } from '../constants';
import Modal from './common/Modal';

interface IncidentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: Alert;
  onUpdate: (alert: Alert) => void;
}

const IncidentDetailModal: React.FC<IncidentDetailModalProps> = ({ isOpen, onClose, alert, onUpdate }) => {
  const [notes, setNotes] = useState(alert.notes);
  const [status, setStatus] = useState(alert.status);

  const handleSave = () => {
    onUpdate({ ...alert, notes, status });
    onClose();
  };
  
  const StatusButton: React.FC<{
      incidentStatus: 'New' | 'Investigating' | 'False Positive' | 'Resolved';
      label: string;
      color: string;
    }> = ({ incidentStatus, label, color }) => (
    <button
      onClick={() => setStatus(incidentStatus)}
      className={`px-3 py-1 text-sm rounded-full font-semibold transition-all duration-200 ${
        status === incidentStatus ? `${color} text-sentinel-blue` : 'bg-sentinel-steel/50 hover:bg-sentinel-steel'
      }`}
    >
      {label}
    </button>
  );
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Incident Details">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-sentinel-light mb-2">Geolocation</h3>
            <div className="aspect-video bg-sentinel-blue rounded-lg overflow-hidden border border-sentinel-steel">
              <iframe
                width="100%"
                height="100%"
                loading="lazy"
                allowFullScreen
                src={`https://maps.google.com/maps?q=${alert.geolocation.lat},${alert.geolocation.lon}&z=6&output=embed&t=k&styles=invert_color:true|visibility:simplified`}
                className="filter invert hue-rotate-180 contrast-125"
              ></iframe>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-sentinel-light mb-2">Incident Management</h3>
            <div className="p-4 bg-sentinel-blue rounded-lg border border-sentinel-steel space-y-4">
               <div className="flex flex-wrap gap-2">
                 <StatusButton incidentStatus="Investigating" label="Investigating" color="bg-yellow-400" />
                 <StatusButton incidentStatus="False Positive" label="False Positive" color="bg-green-400" />
                 <StatusButton incidentStatus="Resolved" label="Resolved" color="bg-blue-400" />
               </div>
               <div>
                 <label htmlFor="notes" className="block text-sm font-medium text-sentinel-silver mb-1">Analyst Notes</label>
                 <textarea
                    id="notes"
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full bg-sentinel-blue border border-sentinel-steel rounded-md p-2 focus:ring-2 focus:ring-sentinel-cyan focus:outline-none font-mono"
                    placeholder="Add investigation notes here..."
                 ></textarea>
               </div>
            </div>
          </div>
        </div>
        {/* Right Column */}
        <div className="space-y-4">
            <h3 className="text-lg font-semibold text-sentinel-light mb-2">Raw Technical Data</h3>
            <div className="p-4 bg-sentinel-blue rounded-lg border border-sentinel-steel font-mono text-sm text-sentinel-silver space-y-2 overflow-x-auto">
              <p><span className="text-sentinel-cyan">Token Name:</span> {alert.tokenName}</p>
              <p><span className="text-sentinel-cyan">Timestamp:</span> {new Date(alert.timestamp).toUTCString()}</p>
              <p><span className="text-sentinel-cyan">Source IP:</span> {alert.ip}</p>
              <p><span className="text-sentinel-cyan">User-Agent:</span> {alert.userAgent}</p>
              <div>
                <p className="text-sentinel-cyan">Headers:</p>
                <pre className="pl-4 whitespace-pre-wrap break-all">{JSON.stringify(alert.requestHeaders, null, 2)}</pre>
              </div>
            </div>
        </div>
      </div>
      <div className="mt-6 flex justify-end">
          <button onClick={handleSave} className="px-6 py-2 rounded-md bg-sentinel-cyan text-sentinel-blue font-bold hover:bg-opacity-80 transition-colors">
            Save & Close
          </button>
      </div>
    </Modal>
  );
};

export default IncidentDetailModal;
