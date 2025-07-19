import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const [lang, setLang] = useState('en');

  const handleSend = async () => {
    setError('');
    if (!input.trim()) {
      setError(texts[lang].emptyError);
      return;
    }

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/analyze-log', { log: input, lang });
      const aiMessage = { role: 'ai', content: res.data.explanation };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const fallback = err.response
        ? `Error ${err.response.status}: ${err.response.data.detail}`
        : texts[lang].networkError;
      setMessages((prev) => [...prev, { role: 'ai', content: fallback }]);
    }
  };

  const texts = {
    en: {
      title: '🪲 BugSage: AI Debug Assistant',
      placeholder: 'Paste your error log here...',
      button: 'Analyze Log',
      resultHeading: 'AI Analysis:',
      emptyError: 'Please enter an error log.',
      networkError: 'Network error or server not reachable.',
    },
    hi: {
      title: '🪲 बगसेज: एआई डिबग सहायक',
      placeholder: 'अपना एरर लॉग यहाँ चिपकाएँ...',
      button: 'लॉग विश्लेषण करें',
      resultHeading: 'एआई विश्लेषण:',
      emptyError: 'कृपया एरर लॉग दर्ज करें।',
      networkError: 'नेटवर्क समस्या या सर्वर उपलब्ध नहीं है।',
    },
    fr: {
      title: '🪲 BugSage : Assistant de débogage IA',
      placeholder: 'Collez votre journal d’erreur ici...',
      button: 'Analyser le journal',
      resultHeading: 'Analyse IA :',
      emptyError: 'Veuillez entrer un journal d’erreur.',
      networkError: 'Erreur réseau ou serveur injoignable.',
    },
  };

return (
  <div className="App">
    <div className="min-h-screen bg-gray-50 flex flex-col items-center">

      {/* Header */}
      <div className="fixed top-0 w-full bg-gray-50 z-10 shadow">
        <div className="flex justify-between items-center max-w-5xl mx-auto p-4">
          <h1 className="text-xl font-bold">{texts[lang].title}</h1>
          <select
            className="border p-2 rounded"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="fr">Français</option>
          </select>
        </div>
      </div>

      {/* Chat + Input Area */}
      <div className="flex flex-col pt-20 pb-28 px-4 w-full max-w-3xl flex-1 overflow-hidden">

        {/* Chat area */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto ">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className="flex items-start space-x-3 max-w-[80%]">
                {msg.role === 'user' ? (
                  <>
                    <div className="bg-blue-100 text-gray-800 px-4 py-2 rounded-lg text-right">
                      <p className="text-sm font-semibold text-right">You</p>
                      <p>{msg.content}</p>
                    </div>
                    <img
                      src="https://i.pravatar.cc/40?u=user"
                      alt="User"
                      className="w-8 h-8 rounded-full"
                    />
                  </>
                ) : (
                  <>
                    <div className="text-2xl mt-1">🪲</div>
                    <div className="bg-green-100 text-gray-800 px-4 py-2 rounded-lg">
                      <p className="text-sm font-semibold">BugSage AI</p>
                      <p>{msg.content}</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Error Message */}
        {error && <div className="mt-2 text-red-600">{error}</div>}
      </div>

      {/* Input field fixed at bottom */}
      <div className="fixed bottom-0 w-full bg-gray-50 border-t z-10">
        <div className="max-w-3xl mx-auto flex gap-2 p-4">
          <textarea
            className="flex-1 p-3 border rounded h-20 resize-none"
            placeholder={texts[lang].placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            className="bg-blue-600 text-white px-5 rounded hover:bg-blue-700"
            onClick={handleSend}
          >
            {texts[lang].button}
          </button>
        </div>
      </div>

    </div>
  </div>
);

}

export default App;
