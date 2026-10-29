import { FC, useEffect, useState } from 'react';
import { Container, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { isAuthenticated } from '../../utils/Auth.ts';
import './styles/HomePage.scss';

export const Home: FC = () => {
  const [authenticated, setAuthenticated] = useState(false);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const checkAuthentication = async () => {
      const result = await isAuthenticated();

      if (!cancelled) {
        setAuthenticated(result);
        setChecked(true);
      }
    };

    void checkAuthentication();

    return () => {
      cancelled = true;
    };
  }, []);

  document.title = 'Events';

  if (!checked) {
    return (
      <Container className="home-page-container">
        Authorization check
      </Container>
    );
  }

  return (
    <Container className="home-page-container">
      <h1>Hello</h1>
      <p>This is Super-Auth project page!</p>
      {authenticated ? (
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