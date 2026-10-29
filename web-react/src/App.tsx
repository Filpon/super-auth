import './App.css';
import React, { FC, useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Home, NavBar, Login, Register } from './components/public/index.ts';
import { PersonalRoute } from './components/personal/PersonalRoute.tsx';
import { CreateEvent } from './components/personal/CreateEvent.tsx';
import { FetchEvents } from './components/personal/FetchEvents.tsx';

import {
  AuthContext,
  isAuthenticated,
  periodicRefreshAuthCheck,
} from './utils/Auth.ts';

export const AuthContextApp = AuthContext;

export const App: FC = () => {
  const [authenticated, setAuthentication] = useState(false);
  const [authReady, setAuthReady] = useState(false);

  const configuredSeconds = Number(
    process.env.REACT_APP_REALM_ACCESS_TOKEN_EXPIRES_IN,
  );
  const seconds =
    Number.isFinite(configuredSeconds) && configuredSeconds > 0
      ? configuredSeconds
      : 60;

  useEffect(() => {
    let cancelled = false;

    const initializeAuth = async () => {
      const result = await isAuthenticated();

      if (!cancelled) {
        setAuthentication(result);
        setAuthReady(true);
      }
    };

    void initializeAuth();

    const stopPeriodicCheck = periodicRefreshAuthCheck(
      seconds,
      setAuthentication,
    );

    return () => {
      cancelled = true;
      stopPeriodicCheck();
    };
  }, [seconds]);

  if (!authReady) {
    return null;
  }

  return (
    <AuthContextApp.Provider
      value={{
        authenticated,
        setAuthentication,
      }}
    >
      <BrowserRouter basename="/">
        <NavBar />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />

          <Route
            path="/fetch-events"
            element={<PersonalRoute element={<FetchEvents />} />}
          />

          <Route
            path="/create-event"
            element={<PersonalRoute element={<CreateEvent />} />}
          />
        </Routes>
      </BrowserRouter>
    </AuthContextApp.Provider>
  );
};