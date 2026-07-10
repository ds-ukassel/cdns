/**
 * Matches the given response headers against the CDN header matchers.
 * @param headers the response headers. Keys must be lowercase.
 * @param matchers the CDN header matchers.
 * @returns all matching headers from the response headers.
 *   If this object is empty, no matchers matched the response headers.
 */
export function matchHeaders(
  headers: Record<string, string>,
  matchers: Record<string, string | null>[],
): Record<string, string> {
  const result: Record<string, string> = {};
  for (const matcher of matchers) {
    if (!matches(headers, matcher)) {
      continue;
    }
    for (const key of Object.keys(matcher)) {
      result[key] = headers[key.toLowerCase()]!;
    }
  }
  return result;
}

/**
 * Checks if the given response headers match the given CDN header matcher.
 * @param headers the response headers. Keys must be lowercase.
 * @param matcher the CDN header matcher.
 * @returns true if the response headers match the CDN header matcher, false otherwise.
 */
export function matches(headers: Record<string, string>, matcher: Record<string, string | null>): boolean {
  for (const [key, expectedValue] of Object.entries(matcher)) {
    const headerValue = headers[key.toLowerCase()];
    if (expectedValue === null) { // any value is acceptable
      if (headerValue === undefined) {
        return false;
      }
    } else if (headerValue !== expectedValue) {
      return false;
    }
  }
  return true;
}
