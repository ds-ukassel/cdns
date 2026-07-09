
export function compileDomains(domains: string[]): RegExp {
    return new RegExp(domains.map(d => domain2pattern(d)).join('|'), 'i');
}

export function compileDomain(domain: string): RegExp {
    return new RegExp(domain2pattern(domain), 'i');
}

function domain2pattern(domain: string): string {
    return '^' + domain
        .replace(/\./g, '\\.')
        .replace(/\*\*/g, '.*')
        .replace(/\*/g, '[^.]+')
        + '$'
    ;
}
