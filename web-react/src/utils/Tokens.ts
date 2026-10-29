/* eslint-disable max-lines*/
// eslint-disable-next-line
import { AxiosResponse } from 'axios';

import { apiRequest } from './AxiosRequest.ts';
import Cookies from 'js-cookie';

export const clearTokens = () => {
  Cookies.remove('access_token', { path: '/' });
  Cookies.remove('access_expires', { path: '/' });
  Cookies.remove('refresh_token', { path: '/' });
  Cookies.remove('refresh_expires', { path: '/' });
};

const storeTokens = (data: any) => {
  Cookies.set('access_token', data.access_token, { path: '/', maxAge: data.expires_in });
  const accessExpires = new Date(Date.now() / 1000 + data.expires_in * 1000).toUTCString();
  Cookies.set('access_expires', accessExpires, { path: '/', maxAge: data.expires_in });
  Cookies.set('refresh_token', data.refresh_token, { path: '/', maxAge: data.refresh_expires_in });
  const refreshExpires = new Date(Date.now() / 1000 + data.refresh_expires_in * 1000).toUTCString();
  Cookies.set('refresh_expires', refreshExpires, { path: '/', maxAge: data.refresh_expires_in });
};

export const checkTokens = async () => {
  const refreshToken = Cookies.get('refresh_token');

  try {
    const response: AxiosResponse = await apiRequest.post(
      '/api/v1/auth/refresh',
      JSON.stringify({
        token: refreshToken
      }),
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    );
    if (response.status >= 400) {
      const error = await response.data;
      throw error.detail;
    }
    const data = await response.data;
    clearTokens();
    storeTokens(data);
  } catch (error) {
    console.error(error);
  }
};

export const checkAccessToken = async () => {
  const accessToken = Cookies.get('access_token');
  const accessExpires = Cookies.get('access_expires');
  const now = Date.now() / 1000;

  if (accessToken && accessExpires) {
    const expires = parseInt(accessExpires, 10);
    if (expires >= now) {
      return true;
    }
  }

  return false;
};

export const createFormData = async (username: string, password: string) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  return formData;
};

export const fetchTokens = async (username: string, password: string) => {
  const formData = await createFormData(username, password);
  const response: AxiosResponse = await apiRequest.post(
    '/api/v1/auth/token',
    formData,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  );
  if (response.status >= 400) {
    const error = await response.data;
    throw error.detail;
  }
  const data = await response.data;
  storeTokens(data);
};

export const handleRegister = async (username: string, password: string) => {
  const formData = await createFormData(username, password);
  const response: AxiosResponse = await apiRequest.post(
    '/api/v1/auth/register',
    formData,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  );
  if (response.status >= 200 && response.status < 300) {
    console.log('User registered successfully!');
  } else {
    const errorData = await response.data;
    console.error(`Error: ${errorData.detail}`);
  }
};
