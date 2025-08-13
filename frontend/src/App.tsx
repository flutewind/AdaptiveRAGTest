// src/App.tsx
import React, { useState, useRef } from 'react';

// 定义类型
interface Message {
  type: 'user' | 'ai';
  content: string;
}

interface ChatResponse {
  messages: Message[];
  source_documents?: string[];
}

function App() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    // 添加用户消息
    const userMsg: Message = { type: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setQuestion('');

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: ChatResponse = await res.json();

      // 添加 AI 回复（取最后一个 AI 消息）
      const aiMsg: Message = {
        type: 'ai',
        content: data.messages?.[1]?.content || data.answer || 'No response'
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (err) {
      const errorMsg: Message = {
        type: 'ai',
        content: '❌ 无法连接到后端。请确保 Python 服务已启动：uvicorn backend.main:app --reload'
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <h1>💬 Adaptive RAG 问答系统</h1>
          <p>基于 LangGraph 的自适应检索增强生成</p>
        </header>

        <div className="messages">
          {messages.length === 0 ? (
            <p className="welcome">欢迎！请输入你的问题，AI 将为你解答。</p>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}`}>
                <div className="avatar">{msg.type === 'user' ? '👤' : '🤖'}</div>
                <div className="content">
                  <p>{msg.content}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="message ai">
              <div className="avatar">🤖</div>
              <div className="content">
                <p>AI 正在思考中...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="输入你的问题..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? '发送中...' : '发送'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;