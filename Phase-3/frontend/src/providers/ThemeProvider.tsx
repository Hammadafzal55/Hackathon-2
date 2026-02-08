'use client';

import React, { ReactNode } from 'react';
import { ThemeProvider as ThemeContextProvider } from '../context/ThemeContext';

interface Props {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: Props) => {
  return (
    <ThemeContextProvider>
      {children}
    </ThemeContextProvider>
  );
};