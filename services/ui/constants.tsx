
import React from 'react';
import { HoneyToken, Alert, TokenType, TokenStatus } from './types';

export const MOCK_TOKENS: HoneyToken[] = [
  {
    id: 'token-1',
    name: 'Q4 Financials - Sharepoint',
    type: TokenType.URL,
    value: 'https://tripwire.app/trap?token_id=token-1',
    displayUrl: 'https://acmecorp.sharepoint.com/sites/finance/Shared%20Documents/Q4-Financials-FINAL-CONFIDENTIAL.xlsx?authkey=AbCDeFgHiJkLmNoPqRsTuVwXyZ',
    createdAt: '2023-10-15T10:00:00Z',
    alertCount: 3,
    status: TokenStatus.Active,
  },
  {
    id: 'token-2',
    name: 'AWS Root Credentials Backup',
    type: TokenType.URL,
    value: 'https://tripwire.app/trap?token_id=token-2',
    displayUrl: 'https://s3-us-west-2.amazonaws.com/acme-corp-backups-private/root-credentials.csv',
    createdAt: '2023-11-01T14:30:00Z',
    alertCount: 1,
    status: TokenStatus.Active,
  },
  {
    id: 'token-3',
    name: 'Project Chimera Source Code.docx',
    type: TokenType.File,
    value: 'https://tripwire.sentinel/webhook/pxl-a3b4c5d6e7f8',
    createdAt: '2023-11-20T09:00:00Z',
    alertCount: 0,
    status: TokenStatus.Disabled,
  },
];

export const MOCK_ALERTS: Alert[] = [
  {
    id: 'alert-1',
    tokenId: 'token-1',
    tokenName: 'Q4 Financials - Sharepoint',
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    ip: '198.51.100.14',
    geolocation: { city: 'Moscow', country: 'RU', lat: 55.7558, lon: 37.6173 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    requestHeaders: { 'Accept-Language': 'ru-RU,ru;q=0.9' },
    notes: 'Initial access, seems automated.',
    status: 'Investigating',
  },
  {
    id: 'alert-2',
    tokenId: 'token-2',
    tokenName: 'AWS Root Credentials Backup',
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    ip: '203.0.113.88',
    geolocation: { city: 'Amsterdam', country: 'NL', lat: 52.3676, lon: 4.9041 },
    userAgent: 'curl/7.64.1',
    requestHeaders: { 'User-Agent': 'curl/7.64.1', 'Accept': '*/*' },
    notes: '',
    status: 'New',
  },
    {
    id: 'alert-3',
    tokenId: 'token-1',
    tokenName: 'Q4 Financials - Sharepoint',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    ip: '192.0.2.1',
    geolocation: { city: 'San Francisco', country: 'US', lat: 37.7749, lon: -122.4194 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    requestHeaders: { 'Accept-Language': 'en-US,en;q=0.9' },
    notes: 'Marked as false positive, internal security scan.',
    status: 'False Positive',
  },
];

export const ICONS = {
    shield: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-sentinel-cyan w-8 h-8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>,
    dashboard: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>,
    key: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>,
    plus: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>,
    alert: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>,
    mapPin: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>,
    clock: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>,
    ip: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 0-3 3v2H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2V4a3 3 0 0 0-3-3z"></path><path d="M9 10h6"></path><path d="M12 14v-4"></path></svg>,
    edit: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>,
    trash: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>,
    close: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>,
    brain: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a4.5 4.5 0 0 0-4.5 4.5c0 1.25.46 2.4 1.23 3.24-.95.4-1.73 1-2.32 1.76-.78.99-1.33 2.21-1.33 3.5A6.5 6.5 0 0 0 12 22a6.5 6.5 0 0 0 6.5-6.5c0-1.29-.55-2.51-1.33-3.5-.59-.76-1.37-1.36-2.32-1.76.77-.84 1.23-1.99 1.23-3.24A4.5 4.5 0 0 0 12 2z"></path><path d="M12 13a2.5 2.5 0 0 0-2.5 2.5c0 1.54.62 2.92 1.67 3.92.54.52 1.18.9 1.83 1.08"></path><path d="M12 13a2.5 2.5 0 0 1 2.5 2.5c0 .38-.08.74-.23 1.08"></path><path d="M16 12.5c.83.82 1.5 1.88 1.5 3"></path><path d="M8 12.5c-.83.82-1.5 1.88-1.5 3"></path><path d="M12 2v4"></path><path d="M16.2 4.8a4.5 4.5 0 0 1-8.4 0"></path></svg>,
    copy: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>,
    check: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>,
};