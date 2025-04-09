/* eslint-disable max-lines */
import React, { useEffect, useState, useContext } from 'react'; // useContext
import { Form, Card, Container, Button, Row } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { AxiosError } from 'axios';

import { fetchTokens } from '../../utils/Tokens.ts';
import { AuthContextApp } from '../../App.tsx';
import './styles/Login.scss';
import './styles/Spinner.scss';
import { ErrorModal } from '../ErrorModal.tsx';

import { Snowflakes } from './Snowflakes.tsx';
import { ReactComponent as VisibleInput } from './pictures/VisibleInput.svg';
import { ReactComponent as InvisibleInput } from './pictures/InvisibleInput.svg';

/**
 * Functional component that represents project login page
 *
 * @returns TSX element representing the login page container
 */
export const Login = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [message, setMessage] = useState('');
  const [showError, setShowError] = useState(false);
  const [loading, setLoading] = useState(false);
  const { setAuthentication } = useContext(AuthContextApp);
  const [error, setError] = useState<any>(undefined);
  const [isDisabled, setDisabled] = useState<boolean>(true);
  const [isVisible, setIsVisible] = useState(false);

  const handleCloseError = () => setShowError(false);

  const navigate = useNavigate();

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    setShowError(false);
    setDisabled(true);
    try {
      await fetchTokens(username, password);
      setAuthentication(true);
      navigate('/');
    } catch (err) {
      const error = err as AxiosError;
      if (error.response && error.response.status === 401) {
        setError('Wrong login or password. Please try again');
        setShowError(true);
      } else if (error.response && error.response.status === 500) {
        setError('Server error');
        setShowError(true);
      } else if (error?.code === 'ECONNABORTED') {
        setError('Connection to server is not established');
        setShowError(true);
      } else if (error?.code === 'ERR_NETWORK') {
        setError('Server domain network error');
        setShowError(true);
      } else {
        console.log(error);
        setError('Something went wrong. Try later');
        setShowError(true);
      }
    } finally {
      setDisabled(false);
    }
  };

  const navigateToRegister = async () => {
    setMessage('Navigating to the registration page');
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000)); // 2 seconds delay
    setLoading(false);
    navigate('/register');
  };

  const toggleVisibility = async () => {
    await new Promise((resolve) => setTimeout(resolve, 100)); // Delay simulation
    setIsVisible((prev) => !prev); // Toggle visibility
  };

  useEffect(() => {
    document.title = 'Login';
    if (username.length > 0 && password.length > 0) {
      setDisabled(false);
      setShowError(false);
    } else {
      setDisabled(true);
    }
  }, [username, password]);

  return (
    <Container className="login-container">
      <Snowflakes />
      <Card className="login-card">
        <Card.Body className="login-body">
          {loading ? (
            <>
              {message && (
                <Container className="login-to-register-message">
                  {message}
                </Container>
              )}
              {loading && <Container className="spinner" />}
            </>
          ) : (
            <Form className="form-card">
              <Form.Group controlId="formBasicEmail">
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </Form.Group>
              <Form.Group controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type={isVisible ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Button
                  variant="outline-secondary"
                  onClick={toggleVisibility}
                  className="visibility-switcher"
                >
                  {isVisible ? <VisibleInput /> : <InvisibleInput />}
                </Button>
              </Form.Group>
              <ErrorModal
                show={showError}
                handleClose={handleCloseError}
                errorMessage={error}
              />
              <Button disabled={isDisabled} onClick={handleClick} type="submit">
                Login
              </Button>
              <Row className="login-to-register-p">
                Don't have an account?{' '}
                <Row
                  className="login-to-register-span"
                  onClick={navigateToRegister}
                >
                  Register
                </Row>
              </Row>
            </Form>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};
