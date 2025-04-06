import React, { createContext, useState, useEffect, useMemo, useContext } from 'react';
import PropTypes from 'prop-types';

const ThemeContext = createContext();

const getInitialTheme = () => {
  
  const storedTheme = localStorage.getItem('cryptoTheme');
  if (storedTheme) {
    return storedTheme;
  }
  
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  
  return 'light';
};

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getInitialTheme); 

  useEffect(() => {
    
    document.body.setAttribute('data-bs-theme', theme);
    
    localStorage.setItem('cryptoTheme', theme);
  }, [theme]);

  
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

ThemeProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};