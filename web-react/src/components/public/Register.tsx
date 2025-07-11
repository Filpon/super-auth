/* eslint-disable max-lines */
import React, { useState } from 'react';
import { Form, Card, Container, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AxiosError } from 'axios';

import { handleRegister } from '../../utils/Tokens.ts';
import './styles/Login.scss';
import { ErrorModal } from '../ErrorModal.tsx';

import { Snowflakes } from './Snowflakes.tsx';
// eslint-disable-next-line
import { ReactComponent as VisibleInput } from './pictures/VisibleInput.svg'; // @ts-ignore
// eslint-disable-next-line
import { ReactComponent as InvisibleInput } from './pictures/InvisibleInput.svg'; // @ts-ignore

/**
 * Functional component that represents registration functional
 *
 * @returns TSX element representing registration functional
 */
export const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showError, setShowError] = useState(false);
  const [error, setError] = useState<any>(undefined);
  const [isDisabled, setDisabled] = useState<boolean>(false);
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  const [isVisible, setIsVisible] = useState(false);
  const [isConfirmVisible, setIsConfirmVisible] = useState(false);
  const navigate = useNavigate();

  const handleCloseError = () => setShowError(false);

  // Regular expression allows only alphanumeric characters and underscores for username
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  // Regular expression for password (at least 6 characters, can include letters, numbers, and special characters)
  const passwordRegex = /^[a-zA-Z0-9!@#$%^&*()_+={}$$$$:;"'<>,.?~`-]{6,}$/;

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputUsername = e.target.value;
    setUsername(inputUsername);
    // Validate username
    if (usernameRegex.test(inputUsername)) {
      setUsernameError('');
    } else {
      setUsernameError(
        'Username\n- should not be empty;\n- contains latin letters, numbers, and underscores',
      );
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputPassword = e.target.value;
    setPassword(inputPassword);
    // Validate password
    if (passwordRegex.test(inputPassword)) {
      setPasswordError('');
    } else {
      setPasswordError(
        'Password\n- should not be empty;\n at least 6 characters long;\nincludes latin letters, numbers, and special characters',
      );
    }
  };

  const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputConfirmPassword = e.target.value;
    setConfirmPassword(inputConfirmPassword);
    // Validate confirm password
    if (inputConfirmPassword !== password) {
      setConfirmPasswordError('Passwords do not match');
    } else {
      setConfirmPasswordError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setShowError(false);
    setDisabled(true);
    try {
      await handleRegister(username, password);
      setMessage('Navigating to login page');
      setLoading(true);
      toast.success('Registration sucessfull!', {
        position: 'top-center',
        autoClose: 4000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      await new Promise((resolve) => setTimeout(resolve, 4000)); // 4 seconds delay
      setLoading(false);
      navigate('/');
    } catch (err) {
      setError(err);
      const error = err as AxiosError;
      console.error(error?.code);
      if (error.response && error.response.status === 409) {
        setError('Username already exists');
        setShowError(true);
      } else if (error.response && error.response.status === 500) {
        setError('Server connection error');
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

  const toggleVisibility = async () => {
    await new Promise((resolve) => setTimeout(resolve, 100)); // Delay simulation
    setIsVisible((prev) => !prev); // Toggle visibility
  };

  const toggleConfirmVisibility = async () => {
    await new Promise((resolve) => setTimeout(resolve, 100)); // Delay simulation
    setIsConfirmVisible((prev) => !prev); // Toggle visibility for confirm password
  };

  const isFormValid =
    usernameRegex.test(username) && passwordRegex.test(password);

  return (
    <Container className="login-container">
      <Snowflakes />
      <Card className="login-card">
        <Card.Body
          style={{
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <ToastContainer />
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
            <Form className="form-card" onSubmit={handleSubmit}>
              <Form.Group controlId="formBasicEmail">
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type="text"
                  value={username}
                  onChange={handleUsernameChange}
                  isInvalid={!!usernameError}
                />
                <Form.Control.Feedback type="invalid">
                  {usernameError}
                </Form.Control.Feedback>
              </Form.Group>
              <Form.Group controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type={isVisible ? 'text' : 'password'}
                  value={password}
                  onChange={handlePasswordChange}
                  isInvalid={!!passwordError}
                />
                <Button
                  variant="outline-secondary"
                  onClick={toggleVisibility}
                  className="visibility-switcher"
                >
                  {isVisible ? <VisibleInput /> : <InvisibleInput />}
                </Button>
                <Form.Control.Feedback type="invalid">
                  {passwordError}
                </Form.Control.Feedback>
              </Form.Group>
              <Form.Group controlId="formConfirmPassword">
                <Form.Label>Confirm Password</Form.Label>
                <Form.Control
                  type={isConfirmVisible ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={handleConfirmPasswordChange}
                  isInvalid={!!confirmPasswordError}
                />
                <Button
                  variant="outline-secondary"
                  onClick={toggleConfirmVisibility}
                  className="visibility-switcher"
                >
                  {isConfirmVisible ? <VisibleInput /> : <InvisibleInput />}
                </Button>
                <Form.Control.Feedback type="invalid">
                  {confirmPasswordError}
                </Form.Control.Feedback>
              </Form.Group>
              <ErrorModal
                show={showError}
                handleClose={handleCloseError}
                errorMessage={error}
              />
              <Button disabled={!isFormValid || isDisabled} type="submit">
                Register
              </Button>
            </Form>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};
