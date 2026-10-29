
export enum TokenType {
  URL = 'Fake URL',
  File = 'Fake File',
}

export enum TokenStatus {
  Active = 'Active',
  Disabled = 'Disabled',
}

export interface HoneyToken {
  id: string;
  name: string;
  type: TokenType;
  value: string; // The honey URL or file pixel URL
  displayUrl?: string; // The deceptive URL for display purposes
  createdAt: string;
  alertCount: number;
  status: TokenStatus;
}

export interface Alert {
  id: string;
  tokenId: string;
  tokenName: string;
  timestamp: string;
  ip: string;
  geolocation: {
    city: string;
    country: string;
    lat: number;
    lon: number;
  };
  userAgent: string;
  requestHeaders: Record<string, string>;
  notes: string;
  status: 'New' | 'Investigating' | 'False Positive' | 'Resolved';
}

export type View = 'dashboard' | 'tokens';