/* eslint-disable */
import React from 'react';
import { render } from '@testing-library/react';
import { App } from './App.tsx';

test('renders learn react link', () => {
  const { getByText } = render(<App />);
  const linkElement = getByText(/secured/i);
  expect(linkElement).toBeInTheDocument();
});
