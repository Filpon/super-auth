/* eslint-disable max-lines*/
// eslint-disable-next-line
import { AxiosResponse } from 'axios';

import { apiRequest } from './AxiosRequest.ts';

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('access_expires');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('refresh_expires');
};

const storeTokens = (data: any) => {
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('access_expires', Date.now() / 1000 + data.expires_in);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem(
    'refresh_expires',
    Date.now() / 1000 + data.refresh_expires_in,
  );
};

export const checkRefreshToken = async () => {
  const refreshExpires = localStorage.getItem('refresh_expires');
  const refreshToken = localStorage.getItem('refresh_token');
  const now = Date.now() / 1000;

  if (refreshToken && refreshExpires) {
    if (now > parseFloat(refreshExpires) - 180) {
      clearTokens();
      try {
        const response: AxiosResponse = await apiRequest.post(
          '/api/auth/refresh',
          JSON.stringify({
            token: refreshToken,
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
        storeTokens(data);
      } catch (error) {
        console.error(error);
      }
    }
  }
};

export const checkAccessToken = async () => {
  const accessToken: string | null = localStorage.getItem('access_token');
  const accessExpires: string | null = localStorage.getItem('access_expires');
  const now = Date.now() / 1000;

  if (accessToken && accessExpires) {
    if (now > parseFloat(accessExpires) - 180) {
      clearTokens();
      try {
        const response: any = await apiRequest.post(
          '/api/auth/refresh',
          JSON.stringify({
            token: accessToken,
          }),
          {
            headers: {
              'Content-Type': 'application/json',
            },
          },
        );
        if (response.status >= 400) {
          const error = await response.json();
          throw error.detail;
        }
        const data = await response.json();
        console.log(data);
        storeTokens(data);
      } catch (error) {
        console.error(error);
      }
    }
  }
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
    '/api/auth/token',
    formData,
  );
  if (response.status >= 400) {
    const error = await response.data;
    throw error.detail;
  }
  const data = await response.data;
  storeTokens(data);
};

export const handleRegister = async (username: string, password: string) => {
  console.log(username);
  const formData = await createFormData(username, password);
  console.log(formData);
  const response: AxiosResponse = await apiRequest.post(
    '/api/auth/register',
    formData,
  );
  console.log(response);
  if (response.status >= 200 && response.status < 300) {
    console.log('User registered successfully!');
  } else {
    const errorData = await response.data;
    console.error(`Error: ${errorData.detail}`);
  }
};
