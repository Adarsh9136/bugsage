import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const[log,setLog] = useState('');
  const[result, setResult] = useState('');

  const handleSubmit = async () =>{
    const res = await axios.post('http://127.0.0.1:8000/analyze-log',{log});
    setResult(res.data.message);
  };
  return (
    <div className="App">
      <div className='min-h-screen bg-grey-100 flex flex-col items-center p-8'>
        <h1 className='text-3xl font-bold mb-6'>🪲 BugSage: AI Debug Assistant</h1>
        <textarea 
          className='w-full max-w-2xl h-40 p-4 border-gray-300 rounded-md'
          value={log}
          onChange={(e) => setLog(e.target.value)}
          placeholder='Paste your error log here...'
        />
        <button 
          className='mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700'
          onClick={handleSubmit}
        >
          Analyze Log
        </button>
        {result &&(
          <div className='mt-6 bg-white shadow-md p-4 rounded max-w-2xl w-full'>
            <h2 className='font-semibold mb-2'>AI Analysis:</h2>
            <p>{result}</p>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
