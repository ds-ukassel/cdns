import _cdns from 'cdns.json' with {type: 'json'};

export interface CDN {
    name: string;
    domains?: string[];
    headers?: Record<string, string | null>[];
    asns?: number[];

    // TODO ranges
}

export const cdns: CDN[] = _cdns;
export * from './domains.js';
export * from './headers.js';
