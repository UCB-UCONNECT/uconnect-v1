import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import Chat from './components/Chat';
import Login from './components/login';
import Comunicado from './components/Comunicado';
import ProtectedRoute from './components/ProtectedRoute';
import { logout as apiLogout } from './services/api';
import MuralComunicados from './components/MuralComunicados';

/**
 * Componente Wrapper para a página de Login.
 * Ele recebe a função de navegação e a passa para o componente Login,
 * redirecionando o usuário para o chat após o sucesso.
 */
const LoginPage = () => {
  const navigate = useNavigate();
  const handleLoginSuccess = () => {
    navigate('/chat'); // Redireciona para /chat após o login bem-sucedido
  };
  return <Login onLoginSuccess={handleLoginSuccess} />;
};

/**
 * Componente Wrapper para a página de Chat.
 * Lida com a lógica de logout, redirecionando o usuário para o login.
 */
const ChatPage = () => {
  const navigate = useNavigate();
  const handleLogout = async () => {
    await apiLogout();
    navigate('/login'); // Redireciona para /login após o logout
  };
  return <Chat onLogout={handleLogout} />;
};

/**
 * Componente principal da aplicação que gerencia o roteamento.
 */
function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          {/* Rota Pública: Qualquer um pode acessar a página de login */}
          <Route path="/login" element={<LoginPage />} />

          {/* Agrupamento de Rotas Protegidas */}
          {/* O `ProtectedRoute` verificará a autenticação antes de renderizar qualquer rota filha. */}
          <Route element={<ProtectedRoute />}>
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/comunicados/novo" element={<Comunicado />}/>
            <Route path="/comunicados" element={<MuralComunicados />}/>
            {/* Adicione outras rotas que precisam de login aqui, ex: <Route path="/perfil" element={<Perfil />} /> */}
          </Route>

          {/* Rota Padrão: Redireciona para /login se a rota não for encontrada */}
          <Route path="*" element={<Navigate to="/login" replace />} />

          
          
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

