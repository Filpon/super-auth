import React, { FC, useContext } from 'react';
import { Link } from 'react-router-dom';
import { Button, Nav, Navbar } from 'react-bootstrap';
import { useNavigate } from 'react-router';

import { logout } from '../../utils/Auth.ts';
import { AuthContextApp } from '../../App.tsx';

import { ReactComponent as HomePicture } from './pictures/Home.svg';

/**
 * Functional component that represents project navbar
 *
 * @returns TSX element representing project navbar
 */
export const NavBar: FC = () => {
  const navigate = useNavigate();
  const { authenticated, setAuthentication } = useContext(AuthContextApp);

  const clickLogout = () => {
    logout().finally(() => {
      setAuthentication(false);
      navigate('/');
    });
  };

  return (
    <Navbar className="justify-content-between">
      <Nav>
        <Nav.Item>
          <Navbar.Brand as={Link} to="/">
            <HomePicture width="30" height="30" className="pb-1" fill="blue" />
            <span className="mt-3">Home</span>
          </Navbar.Brand>
        </Nav.Item>
      </Nav>
      {authenticated ? (
        <>
          <Nav>
            <Nav.Item>
              <Nav.Link as={Link} to="/fetch-events">
                Events
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link as={Link} to="/create-event">
                Create Event
              </Nav.Link>
            </Nav.Item>
          </Nav>
          <Nav>
            <Button
              variant="outline-primary"
              className="ml-auto"
              onClick={clickLogout}
            >
              Logout
            </Button>
          </Nav>
        </>
      ) : (
        <></>
      )}
    </Navbar>
  );
};
