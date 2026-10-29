
import React, { useState } from 'react';
import { Alert, Stats } from '../types';
import AlertCard from './AlertCard';
import IncidentDetailModal from './IncidentDetailModal';

interface DashboardProps {
  alerts: Alert[];
  stats: Stats | null;
  onUpdateAlert: (alert: Alert) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ alerts, stats, onUpdateAlert }) => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  return (
    <div className="h-full flex flex-col">
      <h1 className="text-3xl font-bold text-sentinel-light mb-6">Live Alert Dashboard</h1>
      {stats && (
        <div className="mb-6 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {([
              ['New alerts', stats.new_alerts, stats.new_alerts > 0 ? 'text-sentinel-red' : ''],
              ['Last 24h', stats.alerts_24h, ''],
              ['Total alerts', stats.total_alerts, ''],
              ['Active tokens', stats.active_tokens, 'text-sentinel-cyan'],
            ] as [string, number, string][]).map(([label, value, cls]) => (
              <div key={label} className="bg-sentinel-navy rounded-lg p-4">
                <div className="text-xs uppercase tracking-wide text-sentinel-silver">{label}</div>
                <div className={`text-3xl font-bold ${cls}`}>{value}</div>
              </div>
            ))}
          </div>
          {stats.top_sources.length > 0 && (
            <div className="bg-sentinel-navy rounded-lg p-4">
              <div className="text-xs uppercase tracking-wide text-sentinel-silver mb-2">Top sources</div>
              <ul className="space-y-1 font-mono text-sm">
                {stats.top_sources.map((s) => (
                  <li key={s.ip} className="flex justify-between">
                    <span>{s.ip}{s.country ? ` (${s.country})` : ''}</span>
                    <span className="text-sentinel-silver">
                      {s.alerts} alert{s.alerts === 1 ? '' : 's'}
                      {s.distinct_tokens > 1 && <span className="ml-2 text-sentinel-red font-bold">{s.distinct_tokens} different tokens</span>}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
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
