"use client";
import React, { useEffect, useRef, useState } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { getSocket } from '@/lib/socketClient';

export default function ChessGame() {
  const [username, setUsername] = useState('Player' + Math.floor(Math.random() * 1000));
  const [roomInput, setRoomInput] = useState('');
  const [room, setRoom] = useState(null);
  const [players, setPlayers] = useState([]);
  const [fen, setFen] = useState(new Chess().fen());
  const [messages, setMessages] = useState([]);
  const [chatText, setChatText] = useState('');
  const [status, setStatus] = useState('Not connected');
  const socket = useRef(null);
  const [connected, setConnected] = useState(false);
  const chess = useRef(new Chess());
  const [boardSize, setBoardSize] = useState(480);
  const boardWrapRef = useRef(null);

  useEffect(() => {
    socket.current = getSocket();
    const s = socket.current;

  s.on('connect', () => { setStatus('Connected'); setConnected(true); console.log('[client] socket connected', s.id); });
    s.on('roomsList', (list) => console.log('rooms', list));

    s.on('roomJoined', ({ room: r, user, players }) => {
      setRoom(r);
      setPlayers(players || []);
      setStatus(`In room ${r}`);
      chess.current = new Chess();
      setFen(chess.current.fen());
    });

    s.on('movePlayed', (data) => {
      if (data?.fen) {
        chess.current.load(data.fen);
        setFen(data.fen);
      }
    });

    s.on('receiveMessage', (payload) => {
      setMessages((m) => [...m, payload]);
    });

    s.on('playerLeft', ({ user }) => {
      setStatus((s) => s + ` - ${user} left`);
    });

    return () => {
      try {
        s.off('connect');
        s.off('roomsList');
        s.off('roomJoined');
        s.off('movePlayed');
        s.off('receiveMessage');
        s.off('playerLeft');
      } catch (e) {}
    };
  }, []);

  useEffect(() => {
    function update() {
      const wrapWidth = boardWrapRef.current?.clientWidth || window.innerWidth - 100;
      const w = Math.min(600, Math.max(240, wrapWidth));
      setBoardSize(w);
    }
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  function createRoom() {
    if (!roomInput) return setStatus('Enter a room id');
    if (!connected) return setStatus('Socket not connected');
    console.log('emit createRoom', { user: username, room: roomInput });
    socket.current.emit('createRoom', { user: username, room: roomInput }, (err, res) => {
      console.log('[client] createRoom callback', { err, res });
      if (err) return setStatus('Create room error: ' + err);
      setStatus('Room created: ' + res.room);
    });
  }

  function joinRoom() {
    if (!roomInput) return setStatus('Enter a room id');
    if (!connected) return setStatus('Socket not connected');
    console.log('emit joinRoom', { user: username, room: roomInput });
    socket.current.emit('joinRoom', { user: username, room: roomInput }, (err, res) => {
      console.log('[client] joinRoom callback', { err, res });
      if (err) return setStatus('Join error: ' + err);
      setStatus('Joined: ' + res.room);
    });
  }

  function onDrop(source, target) {
    if (!room) return false;
    const move = { from: source, to: target, promotion: 'q' };
    const result = chess.current.move(move);
    if (!result) return false;
    setFen(chess.current.fen());
    socket.current.emit('makeMove', { room, move }, (err, res) => {
      if (err) {
        setStatus('Move error: ' + err);
        // revert
        chess.current.undo();
        setFen(chess.current.fen());
      }
    });
    return true;
  }

  function sendMessage() {
    if (!room || !chatText) return;
    if (!connected) return setStatus('Socket not connected');
    console.log('[client] sendMessage', { room, user: username, message: chatText });
    socket.current.emit('sendMessage', { room, user: username, message: chatText });
    setChatText('');
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <input className="border p-2 mr-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="border p-2 mr-2" placeholder="room id" value={roomInput} onChange={(e) => setRoomInput(e.target.value)} />
        <button onClick={createRoom} className="bg-blue-500 text-white px-3 py-1 mr-2">Create</button>
        <button onClick={joinRoom} className="bg-green-500 text-white px-3 py-1">Join</button>
        <div className="mt-2">Status: {status} — Socket: {connected ? 'connected' : 'disconnected'}</div>
      </div>

      <div className="flex gap-6">
        <div ref={boardWrapRef} style={{ width: '100%', maxWidth: 720 }}>
          <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={boardSize} />
        </div>

        <div className="w-80">
          <h3 className="font-bold">Players</h3>
          <ul>
            {players.map((p, i) => <li key={i}>{p}</li>)}
          </ul>

          <hr className="my-2" />

          <h3 className="font-bold">Chat</h3>
          <div className="h-64 overflow-y-auto border p-2 mb-2">
            {messages.map((m, i) => (
              <div key={i} className="mb-1"><strong>{m.user}:</strong> {m.message}</div>
            ))}
          </div>
          <input className="border p-2 w-full mb-2" value={chatText} onChange={(e) => setChatText(e.target.value)} />
          <button onClick={sendMessage} className="bg-indigo-500 text-white px-3 py-1">Send</button>
        </div>
      </div>
    </div>
  );
}
