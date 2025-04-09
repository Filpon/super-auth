import axios from 'axios';

export const apiRequest = axios.create({
  baseURL: `${process.env.REACT_APP_BACKEND_URL}${process.env.REACT_APP_DOMAIN_NAME}`,
  timeout: 5000,
});
