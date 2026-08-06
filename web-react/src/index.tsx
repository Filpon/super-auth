import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App.tsx';
import * as serviceWorker from './serviceWorker.ts';
import './styles.scss';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element was not found');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

serviceWorker.unregister();
