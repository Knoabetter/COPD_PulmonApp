export const authFetch = (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = localStorage.getItem('auth_token') ?? '';
  const isFormData = options.body instanceof FormData;
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
      ...(!isFormData && options.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
};
