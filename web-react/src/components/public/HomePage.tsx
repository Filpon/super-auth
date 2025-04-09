import { FC } from 'react';
import { Container, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import { isAuthenticated } from '../../utils/Auth.ts';
import './styles/HomePage.scss';

/**
 * Functional component that represents project home page
 *
 * @returns TSX element representing the home page container
 */
export const Home: FC = () => {
  document.title = 'Events';

  return (
    <Container className="home-page-container">
      <h1>Hello</h1>
      <p>This is Super-Auth project page!</p>
      {isAuthenticated() ? (
        <Link to="/create-event">
          <Button>Create Event</Button>
        </Link>
      ) : (
        <Link to="/login">
          <Button>Login</Button>
        </Link>
      )}
    </Container>
  );
};
