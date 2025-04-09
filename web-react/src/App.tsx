import './App.css';
import React, { FC, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Home, NavBar, Login, Register } from './components/public/index.ts';
import { PersonalRoute } from './components/personal/PersonalRoute.tsx';
import { CreateEvent } from './components/personal/CreateEvent.tsx';
import { FetchEvents } from './components/personal/FetchEvents.tsx';
import { isAuthenticated, peridodicRefreshAuthCheck } from './utils/Auth.ts';
import { AuthContext } from './utils/Auth.ts';

export const AuthContextApp = AuthContext;

export const App: FC = () => {
  const [authenticated, setAuthentication] =
    useState<boolean>(isAuthenticated());

  peridodicRefreshAuthCheck(100);

  return (
    <AuthContextApp.Provider value={{ authenticated, setAuthentication }}>
      <BrowserRouter basename="/">
        <NavBar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          PersonalRoute
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
