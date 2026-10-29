// eslint-disable-next-line
import { AxiosResponse } from 'axios';

import { apiRequest } from './AxiosRequest.ts';
import Cookies from 'js-cookie';

export const createEvent = async (name: string, date: string) => {
  const accessToken: string | undefined = Cookies.get('access_token');
  const refreshToken: string | undefined = Cookies.get('refresh_token');

  if (accessToken && refreshToken) {
    const response: AxiosResponse = await apiRequest.post(
      '/api/v1/events/create',
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
  const accessToken: string | null = Cookies.get('access_token');
  const refreshToken = Cookies.get('refresh_token');

  if (accessToken && refreshToken) {
    const response: AxiosResponse = await apiRequest.get('/api/v1/events', {
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
