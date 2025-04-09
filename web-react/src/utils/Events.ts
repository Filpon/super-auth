// eslint-disable-next-line
import { AxiosResponse } from 'axios';

import { apiRequest } from './AxiosRequest.ts';

export const createEvent = async (name: string, date: string) => {
  const accessToken: string | null = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');

  if (accessToken && refreshToken) {
    const response: AxiosResponse = await apiRequest.post(
      '/api/events/create',
      JSON.stringify({
        name,
        date: new Date(date),
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
      },
    );
    if (response.status >= 200 && response.status < 300) {
      console.log('Event was created sucessfully');
    } else {
      const errorData = await response.data;
      console.error(`Error: ${errorData.detail}`);
    }
  }
};

export const fetchEvents = async () => {
  const accessToken: string | null = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');

  if (accessToken && refreshToken) {
    const response: AxiosResponse = await apiRequest.get('/api/events', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
    });
    if (response.status >= 200 && response.status < 300) {
      console.log('Events were loaded sucessfully');
    } else {
      const errorData = await response.data;
      console.error(`Error: ${errorData.detail}`);
    }
    return await response.data;
  }
};
