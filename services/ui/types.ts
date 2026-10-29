export type TokenType = 'url' | 'pixel' | 'document';
export type TokenStatus = 'active' | 'disabled';
export type AlertStatus = 'New' | 'Investigating' | 'False Positive' | 'Resolved';

export const TOKEN_TYPE_LABELS: Record<TokenType, string> = {
  url: 'Fake URL',
  pixel: 'Tracking Pixel',
  document: 'Word Document',
};

export interface HoneyToken {
  id: string;
  name: string;
  type: TokenType;
  status: TokenStatus;
  value: string; // URL that fires the canary
  decoy_url: string | null; // deceptive URL shown to the person planting the token
  created_at: string;
  alert_count: number;
}

export interface Alert {
  id: number;
  token_id: string;
  token_name: string;
  timestamp: string;
  ip: string;
  city: string;
  country: string;
  lat: number;
  lon: number;
  user_agent: string;
  request_path: string;
  request_headers: Record<string, string>;
  notes: string;
  status: AlertStatus;
}

export type View = 'dashboard' | 'tokens';
