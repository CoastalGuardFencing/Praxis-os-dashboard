import { render, screen } from '@testing-library/react';
import App from './App';

test('renders PraxisOS dashboard', () => {
  render(<App />);
  const dashboardElement = screen.getByText(/PraxisOS/i);
  expect(dashboardElement).toBeInTheDocument();
});

test('renders executive briefing', () => {
  render(<App />);
  const briefingElement = screen.getByText(/Executive Briefing/i);
  expect(briefingElement).toBeInTheDocument();
});
