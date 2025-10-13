import { Server } from "socket.io";
import { Chess } from "chess.js";

const games = new Map(); // room -> Chess instance
const users = new Map(); // socketId -> { user, room }
const roomsSet = new Set();

function updateStatus(io, game, room) {
  if (game.isCheckmate()) {
    io.to(room).emit("gameOver", { winner: game.turn() === 'w' ? 'Black' : 'White', reason: 'checkmate' });
  } else if (game.isDraw()) {
    io.to(room).emit("gameOver", { winner: null, reason: 'draw' });
  } else if (game.inCheck()) {
    io.to(room).emit("inCheck", game.turn());
  } else {
    io.to(room).emit("updateStatus", game.turn());
  }
}

export default function SocketHandler(req, res) {
  console.log('[server] /api/socket route invoked', req.method, req.url);
  if (!res.socket.server.io) {
    console.log("✅ Initializing Socket.IO server...");
    const io = new Server(res.socket.server, {
      path: '/api/socket',
      cors: { origin: '*' }
    });

    res.socket.server.io = io;

    io.on('connection', (socket) => {
      console.log('socket connected', socket.id);

      // send available rooms and counts
      socket.emit('roomsList', Array.from(roomsSet));

      socket.on('createRoom', ({ user, room }, cb) => {
        console.log('[server] createRoom request', { socket: socket.id, user, room });
        if (!room) {
          console.log('[server] createRoom failed: missing room');
          return cb?.('Room id required');
        }
        if (roomsSet.has(room)) {
          console.log('[server] createRoom failed: already exists', room);
          return cb?.('Room already exists');
        }

        roomsSet.add(room);
        socket.join(room);
        users.set(socket.id, { user, room });
        games.set(room, new Chess());

        io.to(room).emit('roomJoined', { room, user, players: [user] });
        io.emit('roomsList', Array.from(roomsSet));
        console.log(`[server] ${user} created and joined room ${room}`);
        cb?.(null, { room });
      });

      socket.on('joinRoom', ({ user, room }, cb) => {
        console.log('[server] joinRoom request', { socket: socket.id, user, room });
        if (!roomsSet.has(room)) {
          console.log('[server] joinRoom failed: room not found', room);
          return cb?.('Room not found');
        }
        const roomInfo = io.sockets.adapter.rooms.get(room);
        if (roomInfo && roomInfo.size >= 2) {
          console.log('[server] joinRoom failed: room full', room);
          return cb?.('Room is full');
        }

        // ensure username uniqueness in room
        for (const [id, info] of users.entries()) {
          if (info.room === room && info.user === user) {
            console.log('[server] joinRoom failed: username taken', user);
            return cb?.('Username taken');
          }
        }

        socket.join(room);
        users.set(socket.id, { user, room });

        const players = [];
        const roomSockets = io.sockets.adapter.rooms.get(room) || new Set();
        for (const id of roomSockets) {
          const u = users.get(id);
          if (u) players.push(u.user);
        }

        // if 2 players present, ensure a game exists
        if (!games.has(room)) games.set(room, new Chess());

        io.to(room).emit('roomJoined', { room, user, players });
        io.emit('roomsList', Array.from(roomsSet));
        console.log(`[server] ${user} joined room ${room}`);
        cb?.(null, { room });
      });

      socket.on('makeMove', ({ room, move }, cb) => {
        const game = games.get(room);
        if (!game) return cb?.('Game not found');

        const result = game.move(move);
        if (!result) return cb?.('Illegal move');

        io.to(room).emit('movePlayed', { fen: game.fen(), pgn: game.pgn(), moves: game.history(), gameOver: game.isGameOver() });
        updateStatus(io, game, room);
        cb?.(null, result);
      });

      socket.on('sendMessage', ({ room, user, message }) => {
        console.log('[server] sendMessage', { socket: socket.id, room, user, message });
        io.to(room).emit('receiveMessage', { user, message, time: Date.now() });
      });

      socket.on('disconnect', () => {
        const info = users.get(socket.id);
        if (!info) return;
        const { room, user } = info;

        users.delete(socket.id);
        socket.leave(room);

        const roomInfo = io.sockets.adapter.rooms.get(room);
        if (!roomInfo || roomInfo.size === 0) {
          roomsSet.delete(room);
          games.delete(room);
        }

        io.to(room).emit('playerLeft', { user });
        io.emit('roomsList', Array.from(roomsSet));
        console.log(`${user} disconnected from ${room}`);
      });
    });

    console.log('Socket.IO initialized');
  }

  res.end();
}
