import { useContext } from 'react';

import { KeycloakContext } from '../../components/KeycloackContext.tsx';

const useKeycloak = () => {
  const context = useContext(KeycloakContext);
  if (!context) {
    throw new Error('Keycloak needs KeycloakProvider to use');
  }

  return context;
};

export default useKeycloak;
