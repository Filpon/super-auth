/* eslint-disable */
import { Navigate } from 'react-router';
import { useContext } from 'react';

import { AuthContextApp } from '../../App.tsx';

interface ProtectedRouteProps {
  element: React.ReactNode;
}

export const useAuth = () => {
  const context = useContext(AuthContextApp);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const PersonalRoute: React.FC<ProtectedRouteProps> = ({ element }) => {
  const { authenticated } = useAuth();

  return authenticated ? <>{element}</> : <Navigate to="/login" />;
};
