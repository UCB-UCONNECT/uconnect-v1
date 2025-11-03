// src/services/api.js
const API_URL = "http://localhost:8000";

/* ==================== GERENCIAMENTO DE TOKEN ==================== */

const getToken = () => sessionStorage.getItem("access_token");
const setToken = (token) => sessionStorage.setItem("access_token", token);
const removeToken = () => sessionStorage.removeItem("access_token");

const getHeaders = (includeAuth = true) => {
  const headers = { "Content-Type": "application/json" };
  if (includeAuth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Erro HTTP ${response.status}`);
  }
  if (response.status !== 204) {
    return response.json();
  }
  return null;
};

/* ==================== AUTENTICAÇÃO ==================== */

export const login = async (registration, password) => {
  const response = await fetch(`${API_URL}/auth/login/`, {
    method: "POST",
    headers: getHeaders(false),
    body: JSON.stringify({
      registration: registration.trim(),
      password: password.trim(),
    }),
  });

  const data = await handleResponse(response);
  setToken(data.access_token);
  return data;
};

export const logout = async () => {
  try {
    await fetch(`${API_URL}/auth/logout/`, {
      method: "POST",
      headers: getHeaders(),
    });
  } finally {
    removeToken();
  }
};

export const validateSession = async () => {
  try {
    const response = await fetch(`${API_URL}/auth/validate/`, {
      method: "GET",
      headers: getHeaders(),
    });
    return await handleResponse(response);
  } catch (error) {
    removeToken();
    throw error;
  }
};

/* ==================== USUÁRIOS ==================== */

export const getCurrentUser = async () => {
  const response = await fetch(`${API_URL}/users/me/`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const updateProfile = async (userData) => {
  const response = await fetch(`${API_URL}/users/me/`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
};

// Listar usuários para o modal de novo chat
export const listUsers = async (query = "") => {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  const response = await fetch(`${API_URL}/users/${qs}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse(response);
};

/* ==================== EVENTOS ==================== */

const eventToBackend = (event) => ({
  title: event.title || event.titulo,
  date: event.date,
  hora: event.hora || null,
  description: event.descricao || event.description || "",
  local: event.local || null,
  academicGroupId: event.academicGroupId || event.local || null,
});

const eventFromBackend = (event) => {
  let horaStr = "";
  let startTimeStr = "";
  let endTimeStr = "";

  if (event.startTime) {
    startTimeStr = event.startTime.substring(0, 5);
    horaStr = startTimeStr;

    if (event.endTime) {
      endTimeStr = event.endTime.substring(0, 5);
      horaStr += ` - ${endTimeStr}`;
    }
  }

  return {
    id: event.id,
    title: event.title,
    date: event.eventDate,
    timestamp: event.timestamp,
    hora: horaStr,
    startTime: startTimeStr,
    endTime: endTimeStr,
    description: event.description || "",
    descricao: event.description || "",
    local: event.academicGroupId || "",
    academicGroupId: event.academicGroupId || "",
  };
};

export const getEvents = async () => {
  const response = await fetch(`${API_URL}/events/`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  const data = await handleResponse(response);
  return data.map(eventFromBackend);
};

export const getEvent = async (eventId) => {
  const response = await fetch(`${API_URL}/events/${eventId}/`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const createEvent = async (event) => {
  const response = await fetch(`${API_URL}/events/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(eventToBackend(event)),
  });
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const updateEvent = async (eventId, event) => {
  const response = await fetch(`${API_URL}/events/${eventId}/`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(eventToBackend(event)),
  });
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const deleteEvent = async (eventId) => {
  const response = await fetch(`${API_URL}/events/${eventId}/`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse(response);
};

/* ==================== CHAT ==================== */

// Lista conversas
export const getConversations = async () => {
  const response = await fetch(`${API_URL}/chats/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

// Mensagens da conversa — aceita options (ex.: { signal })
export const getMessages = async (chatId, options = {}) => {
  const response = await fetch(`${API_URL}/chats/${chatId}/messages`, {
    method: "GET",
    headers: getHeaders(),
    ...options,
  });
  return handleResponse(response);
};

// Enviar mensagem
export const sendMessage = async (chatId, messageContent) => {
  const response = await fetch(`${API_URL}/chats/${chatId}/messages`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ content: messageContent }),
  });
  return handleResponse(response);
};

// Marcar como lidas
export const markAllMessagesAsRead = async (chatId) => {
  const response = await fetch(`${API_URL}/chats/${chatId}/read`, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse(response);
};

// Criar conversa
export const createConversation = async (participantIds, title) => {
  const body = { participant_ids: participantIds };
  if (title) body.title = title;

  const response = await fetch(`${API_URL}/chats/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(response);
};

// **Excluir conversa** (ADICIONADO)
export const deleteConversation = async (chatId) => {
  const response = await fetch(`${API_URL}/chats/${chatId}/`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse(response);
};
/* ==================== PUBLICAÇÕES (MURAL / POSTS) ==================== */
// lista posts para o mural
export const getAnnouncements = async (params = {}) => {
  const qs = new URLSearchParams();
  if (params.type) qs.set("type", params.type); // opcional, se o backend ignorar tudo bem
  const url = `${API_URL}/posts/${qs.toString() ? `?${qs}` : ""}`;
  const resp = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse(resp);
};

// cria post (comunicado)
export const sendAnnouncement = async (payload) => {
  const resp = await fetch(`${API_URL}/posts/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      title: payload.title || "Comunicado",
      content: payload.message || payload.content || "",
    }),
  });
  return handleResponse(resp);
};

export const updateAnnouncement = async (id, payload) => {
  const resp = await fetch(`${API_URL}/posts/${id}`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(resp);
};

export const deleteAnnouncement = async (id) => {
  const resp = await fetch(`${API_URL}/posts/${id}`, { method: "DELETE", headers: getHeaders() });
  return handleResponse(resp);
};

/* ==================== CATÁLOGOS PARA FILTROS (CURSOS / MATÉRIAS / TURMAS) ==================== */
// ajuste os endpoints se o backend usar nomes diferentes
export const getCourses = async (q = "") => {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  const resp = await fetch(`${API_URL}/courses/${qs}`, { method: "GET", headers: getHeaders() });
  return handleResponse(resp);
};

export const getSubjects = async (q = "") => {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  const resp = await fetch(`${API_URL}/subjects/${qs}`, { method: "GET", headers: getHeaders() });
  return handleResponse(resp);
};

export const getClasses = async (q = "") => {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  const resp = await fetch(`${API_URL}/classes/${qs}`, { method: "GET", headers: getHeaders() });
  return handleResponse(resp);
};

/* ==================== UTILITÁRIOS ==================== */

export const isAuthenticated = () => !!getToken();

export { getToken, setToken, removeToken }