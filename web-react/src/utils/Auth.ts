import { createContext } from 'react';

import { apiRequest } from './AxiosRequest.ts';
import { checkRefreshToken, checkAccessToken, clearTokens } from './Tokens.ts';

export const AuthContext = createContext({
  authenticated: false,
  // eslint-disable-next-line
  setAuthentication: (auth: boolean) => {},
});

export const isAuthenticated = () => {
  return localStorage.getItem('access_token') !== null;
};

export const peridodicRefreshAuthCheck = (seconds = 120) => {
  const interval = setInterval(() => {
    if (isAuthenticated()) checkRefreshToken();
  }, seconds * 1000);
  return () => clearInterval(interval);
};

export const logout = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  clearTokens();

  await apiRequest.post(
    '/api/v1/auth/logout',
    JSON.stringify({ token: refreshToken }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    },
  );
};

export const authorized_fetch = async (
  url: string,
  headers: any,
  options: any,
) => {
  if (isAuthenticated()) {
    await checkAccessToken();
    const token = localStorage.getItem('access_token');
    headers['Authorization'] = 'Bearer ' + token;
  }

  let response = await fetch(url, {
    headers,
    ...options,
  });

  response = await checkStatus(response);
  return await response.json();
};

const checkStatus = async (response: Response) => {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
    const error = await response.json();
    throw error.detail;
  }
};
