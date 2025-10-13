import React from 'react';

export default function GameInfo({ room, players }) {
  return (
    <div>
      <h3 className="text-lg font-bold">Room</h3>
      <div>{room || '—'}</div>
      <h3 className="mt-2 text-lg font-bold">Players</h3>
      <ul>
        {players?.map((p, idx) => <li key={idx}>{p}</li>)}
      </ul>
    </div>
  );
}
