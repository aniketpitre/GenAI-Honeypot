
import React from 'react';
import { Alert } from '../types';
import { ICONS } from '../constants';

interface AlertCardProps {
  alert: Alert;
  onClick: () => void;
}

const StatusIndicator: React.FC<{ status: Alert['status'] }> = ({ status }) => {
  const statusConfig = {
    New: { color: 'bg-sentinel-red', text: 'New' },
    Investigating: { color: 'bg-yellow-400', text: 'Investigating' },
    'False Positive': { color: 'bg-green-400', text: 'False Positive' },
    Resolved: { color: 'bg-blue-400', text: 'Resolved' },
  };
  const config = statusConfig[status];
  return (
    <div className="flex items-center space-x-2">
      <span className={`w-3 h-3 rounded-full ${config.color}`}></span>
      <span className="text-sm font-semibold">{config.text}</span>
    </div>
  );
};

const AlertCard: React.FC<AlertCardProps> = ({ alert, onClick }) => {
  const timeAgo = (date: string) => {
    const seconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";
    return Math.floor(seconds) + " seconds ago";
  }

  return (
    <div 
        onClick={onClick} 
        className="bg-sentinel-navy rounded-lg p-4 cursor-pointer border border-transparent hover:border-sentinel-cyan transition-all duration-200 shadow-lg flex flex-col justify-between space-y-4 animate-[fadeIn_0.5s_ease-in-out]"
        style={{ animationFillMode: 'forwards', opacity: 0 }}
    >
      <div className="flex justify-between items-start">
        <h3 className="font-bold text-lg text-sentinel-light pr-2">{alert.tokenName}</h3>
        <div className="flex-shrink-0">
          <StatusIndicator status={alert.status} />
        </div>
      </div>
      
      <div className="space-y-2 text-sm text-sentinel-silver">
        <div className="flex items-center space-x-2">
          <div className="text-sentinel-cyan">{ICONS.alert}</div>
          <span className="font-mono text-sentinel-red">{alert.ip}</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sentinel-cyan">{ICONS.mapPin}</div>
          <span>{alert.geolocation.city || 'Unknown City'}, {alert.geolocation.country || 'Unknown Country'}</span>
        </div>
      </div>

      <div className="text-xs text-sentinel-steel flex items-center space-x-2">
          <div className="text-sentinel-silver">{ICONS.clock}</div>
          <span>{timeAgo(alert.timestamp)}</span>
      </div>
    </div>
  );
};

export default AlertCard;
