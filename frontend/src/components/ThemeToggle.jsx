import React from 'react';
import { Button } from 'react-bootstrap';
import { useTheme } from '../context/ThemeContext'; 

const SunIcon = () => <>☀️</>;
const MoonIcon = () => <>🌙</>;

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant={theme === 'dark' ? 'outline-light' : 'outline-dark'}
      size="sm"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      className="d-flex align-items-center" 
    >
      {theme === 'light' ? <MoonIcon /> : <SunIcon />}
      <span className="ms-2 d-none d-md-inline"> { }
         {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
      </span>
    </Button>
  );
}

export default ThemeToggle;