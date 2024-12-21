import { render, screen } from '@testing-library/react';
import App from './App';

test('renders vehicle monitoring title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Vehicle Monitoring System/i);
  expect(titleElement).toBeInTheDocument();
});
