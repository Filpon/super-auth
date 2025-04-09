import React, { useState } from 'react';
import { AxiosError } from 'axios';
import { Form, Container, Button } from 'react-bootstrap';

import { createEvent } from '../../utils/Events.ts';
import './styles/Events.scss';

/**
 * Functional component that creates event.
 *
 * @returns TSX element representing the form and submitted data
 */
export const CreateEvent: React.FC = () => {
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (name === '' || date === '') {
      setMessage('Please fill in all fields');
      return;
    }
    try {
      await createEvent(name, date);
      setMessage('Event was created sucessfully');
      setName('');
      setDate('');
    } catch (err) {
      const error = err as AxiosError;
      console.log(error?.code);
      if (error?.code === 'ERR_BAD_REQUEST' && error?.status === 409) {
        setMessage('Event already exists in system');
      } else if (error?.code === 'ERR_NETWORK') {
        setMessage('Server domain network error');
      } else {
        setMessage('Something went wrong. Try later');
      }
    }
  };

  return (
    <Form className="form" onSubmit={handleSubmit}>
      <Form.Group controlId="formName">
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          placeholder="Please enter event name"
          value={name}
          className="form-input"
          onChange={(e) => {
            if (message !== '') {
              setMessage('');
            }
            setName(e.target.value);
          }}
          required
        />
      </Form.Group>
      <Form.Group className="mt-3" controlId="formDate">
        <Form.Label>Date</Form.Label>
        <Form.Control
          type="date"
          placeholder="Please enter event date"
          value={date}
          className="form-input"
          onChange={(e) => {
            if (message !== '') {
              setMessage('');
            }
            setDate(e.target.value);
          }}
          required
        />
      </Form.Group>
      <Button className="mt-3" type="submit">
        Create Event
      </Button>
      <Container className="message">{message}</Container>
    </Form>
  );
};

export default CreateEvent;
