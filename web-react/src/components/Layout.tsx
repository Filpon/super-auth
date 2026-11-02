import Container from '@mui/material/Container';
import React, { ReactNode } from 'react';

import NavBar from './public/NavBar.tsx';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => (
  <>
    <NavBar />
    <Container maxWidth="md">{children}</Container>
  </>
);

export default Layout;
