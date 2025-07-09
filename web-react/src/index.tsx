import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App.tsx';
import * as serviceWorker from './serviceWorker.ts';
import './styles.scss';

// Checking localStorage availability
try {
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem('key', 'value');
    // const value = localStorage.getItem('key');
  }
} catch (error) {
  console.error('Error accessing localStorage:', error);
}

const root = ReactDOM.createRoot(document.getElementById('root')!);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

serviceWorker.unregister();
