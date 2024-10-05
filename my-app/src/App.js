import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [scores, setScores] = useState(null);
  const [message, setMessage] = useState('');

  const handleGetScores = async () => {
    try {
      // Make an API request to the FastAPI backend to get scores
      const response = await axios.get('http://127.0.0.1:8000/get_scores', {
        params: {
          username: username,
        },
      });

      // Set the scores to the response data
      setScores(response.data);
      setMessage('');
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setMessage('User not found');
        setScores(null);
      } else {
        setMessage('An error occurred. Please try again.');
        setScores(null);
      }
    }
  };

  return (
    <div className="App">
      <h1>Blackjack Scores</h1>
      <div className="input-container">
        <input
          type="text"
          placeholder="Enter username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button onClick={handleGetScores}>Get Scores</button>
      </div>

      {message && <div className="message">{message}</div>}

      {scores && (
        <div className="scores">
          <h2>Scores for {scores.username}</h2>
          <p>Wins: {scores.wins}</p>
          <p>Losses: {scores.losses}</p>
        </div>
      )}
    </div>
  );
}

export default App;
