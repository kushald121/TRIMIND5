const http = require('http');
const { Server } = require('socket.io');
const { Chess } = require('chess.js');

const PORT = process.env.SOCKET_PORT ? Number(process.env.SOCKET_PORT) : 4000;

const server = http.createServer((req,res)=>{
  res.writeHead(200,{'Content-Type':'text/plain'});
  res.end('socket server');
});

const io = new Server(server, { cors: { origin: '*' } });

const games = new Map();
const users = new Map();
const roomsSet = new Set();

function updateStatus(io, game, room) {
  if (game.isCheckmate()) io.to(room).emit('gameOver', { winner: game.turn() === 'w' ? 'Black' : 'White' });
  else if (game.isDraw()) io.to(room).emit('gameOver', { winner: null });
  else if (game.inCheck()) io.to(room).emit('inCheck', game.turn());
  else io.to(room).emit('updateStatus', game.turn());
}

io.on('connection', (socket)=>{
  console.log('[fallback] socket connected', socket.id);
  socket.emit('roomsList', Array.from(roomsSet));

  socket.on('createRoom', ({user,room}, cb)=>{
    console.log('[fallback] createRoom', {user,room});
    if (!room) return cb?.('Room id required');
    if (roomsSet.has(room)) return cb?.('Room exists');
    roomsSet.add(room);
    socket.join(room);
    users.set(socket.id, { user, room });
    games.set(room, new Chess());
    io.to(room).emit('roomJoined', { room, user, players:[user] });
    io.emit('roomsList', Array.from(roomsSet));
    cb?.(null, { room });
  });

  socket.on('joinRoom', ({user,room}, cb)=>{
    console.log('[fallback] joinRoom', {user,room});
    if (!roomsSet.has(room)) return cb?.('Room not found');
    const roomInfo = io.sockets.adapter.rooms.get(room);
    if (roomInfo && roomInfo.size >= 2) return cb?.('Room full');
    socket.join(room);
    users.set(socket.id, { user, room });
    const players = [];
    const roomSockets = io.sockets.adapter.rooms.get(room) || new Set();
    for (const id of roomSockets) { const u = users.get(id); if (u) players.push(u.user); }
    if (!games.has(room)) games.set(room, new Chess());
    io.to(room).emit('roomJoined', { room, user, players });
    io.emit('roomsList', Array.from(roomsSet));
    cb?.(null, { room });
  });

  socket.on('makeMove', ({room, move}, cb)=>{
    const game = games.get(room);
    if (!game) return cb?.('Game not found');
    const result = game.move(move);
    if (!result) return cb?.('Illegal move');
    io.to(room).emit('movePlayed', { fen: game.fen(), pgn: game.pgn(), moves: game.history(), gameOver: game.isGameOver() });
    updateStatus(io, game, room);
    cb?.(null, result);
  });

  socket.on('sendMessage', ({room,user,message})=>{
    console.log('[fallback] message', {room,user,message});
    io.to(room).emit('receiveMessage', { user, message, time: Date.now() });
  });

  socket.on('disconnect', ()=>{
    const info = users.get(socket.id);
    if (!info) return;
    const { room, user } = info;
    users.delete(socket.id);
    socket.leave(room);
    const roomInfo = io.sockets.adapter.rooms.get(room);
    if (!roomInfo || roomInfo.size === 0) { roomsSet.delete(room); games.delete(room); }
    io.to(room).emit('playerLeft', { user });
    io.emit('roomsList', Array.from(roomsSet));
    console.log('[fallback] disconnected', socket.id, user, room);
  });
});

server.listen(PORT, ()=> console.log(`Fallback Socket.IO server listening on ${PORT}`));
