// src/FetchEvents.tsx
import React, { useEffect, useState } from 'react';
import moment from 'moment';
import { Table, Container, InputGroup, FormControl } from 'react-bootstrap';

import { fetchEvents } from '../../utils/Events.ts';

import { Event } from './index.ts';

/**
 * Functional component that fetches event for authenticated user
 *
 * @returns TSXX element representing the component fetching
 */
export const FetchEvents: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(undefined);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    const fetchEventsComponent = async () => {
      try {
        const eventsData = await fetchEvents();
        setEvents(eventsData);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEventsComponent();
  }, []);

  const filteredEvents = events.filter((event) =>
    event.name.toLowerCase().includes(filter.toLowerCase()),
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error fetching events: {error.message}</div>;

  return (
    <Container>
      <h1>Events</h1>
      <InputGroup className="mb-3">
        <FormControl
          placeholder="Filter by name"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </InputGroup>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {filteredEvents.map((event) => (
            <tr key={event.id}>
              <td>{event.name}</td>
              <td>{moment(event.date).format('DD.MM.YYYY')}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};
