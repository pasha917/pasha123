import { useState } from 'react';
import axios from 'axios';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chat', { message: input });
      const aiMessage = { text: response.data.reply, sender: 'ai' };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = { text: 'Sorry, I couldn\'t process your request.', sender: 'ai' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '20px auto', border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
      <h3>AI Chatbot</h3>
      <div style={{ height: '300px', overflowY: 'scroll', border: '1px solid #eee', padding: '10px', marginBottom: '10px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '10px', textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <strong>{msg.sender === 'user' ? 'You' : 'AI'}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div>AI is typing...</div>}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        placeholder="Ask me anything..."
        style={{ width: '70%', padding: '8px' }}
      />
      <button onClick={sendMessage} disabled={loading} style={{ padding: '8px' }}>
        Send
      </button>
    </div>
  );
}

export default Chatbot;