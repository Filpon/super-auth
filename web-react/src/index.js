import React from 'react';
import './index.css';
import './styles.scss';
import * as serviceWorker from './serviceWorker.js';
import { createRoot } from 'react-dom/client'; // Correct import for React 18
import { App } from './App.tsx';

const rootElement = document.getElementById('root');

// Checking localStorage availability
try {
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem('key', 'value');
    // const value = localStorage.getItem('key');
  }
} catch (error) {
  console.error('Error accessing localStorage:', error);
}

const root = createRoot(rootElement); // Create a root

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

serviceWorker.unregister();
