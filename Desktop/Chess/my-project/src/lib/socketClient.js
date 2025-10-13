import { io } from 'socket.io-client';

let socket;

export function getSocket() {
  if (typeof window === 'undefined') {
    return {
      on: () => {},
      off: () => {},
      emit: () => {},
      disconnect: () => {},
      connected: false
    };
  }

  if (!socket) {
  const origin = window.location.origin;
  const preferredTransports = ['polling', 'websocket'];
  console.log('[socketClient] connecting to', origin, 'path /api/socket using transports', preferredTransports);
  socket = io(origin, { path: '/api/socket', transports: preferredTransports, timeout: 30000 });

  socket.on('connect', () => console.log('[socketClient] connected', socket.id));
  socket.on('connect_error', (err) => {
    console.error('[socketClient] connect_error', err);
    // try localhost fallback
    const fallback = 'http://localhost:4000';
    if (origin !== fallback) {
      console.warn('[socketClient] attempting fallback to', fallback);
      socket = io(fallback, { transports: preferredTransports, timeout: 30000 });
      socket.on('connect', () => console.log('[socketClient] connected to fallback', socket.id));
      socket.on('connect_error', (e) => console.error('[socketClient] fallback connect_error', e));
    }
  });
  }

  return socket;
}
