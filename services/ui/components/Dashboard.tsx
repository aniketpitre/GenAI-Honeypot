
import React, { useState } from 'react';
import { Alert } from '../types';
import AlertCard from './AlertCard';
import IncidentDetailModal from './IncidentDetailModal';

interface DashboardProps {
  alerts: Alert[];
  onUpdateAlert: (alert: Alert) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ alerts, onUpdateAlert }) => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  return (
    <div className="h-full flex flex-col">
      <h1 className="text-3xl font-bold text-sentinel-light mb-6">Live Alert Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 overflow-y-auto pr-2">
        {alerts.map(alert => (
          <AlertCard key={alert.id} alert={alert} onClick={() => setSelectedAlert(alert)} />
        ))}
      </div>
      {selectedAlert && (
        <IncidentDetailModal 
          isOpen={!!selectedAlert} 
          onClose={() => setSelectedAlert(null)} 
          alert={selectedAlert}
          onUpdate={onUpdateAlert}
        />
      )}
    </div>
  );
};

export default Dashboard;
