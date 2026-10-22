/**
 * Formats API errors (including Pydantic 422 arrays) into user-friendly strings,
 * preventing Minified React Error #31 caused by rendering raw objects in JSX.
 */
export function formatApiError(error: any, fallback = 'Произошла ошибка при выполнении операции'): string {
  if (!error) return fallback;
  if (typeof error === 'string') return error;

  const detail = error.response?.data?.detail ?? error.detail ?? error.message;
  if (!detail) return fallback;

  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((d: any) => {
        if (typeof d === 'string') return d;
        const loc = Array.isArray(d.loc)
          ? d.loc.filter((x: any) => x !== 'body' && typeof x === 'string').join('.')
          : '';
        const msg = d.msg || d.message || JSON.stringify(d);
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join('; ');
  }

  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  return String(detail);
}
