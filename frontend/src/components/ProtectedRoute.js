// Em src/components/ProtectedRoute.js
import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { isAuthenticated, validateSession, removeToken, getToken } from '../services/api';

const ProtectedRoute = () => {
  const [status, setStatus] = useState('checking'); // checking | ok | unauth

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setStatus('unauth');
      return;
    }

    // Valida sessão no backend para evitar tokens antigos
    validateSession()
      .then(() => setStatus('ok'))
      .catch(() => {
        removeToken();
        setStatus('unauth');
      });
  }, []);

  if (status === 'checking') {
    return null; // opcional: pode renderizar um spinner simples
  }

  if (status === 'unauth' || !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
