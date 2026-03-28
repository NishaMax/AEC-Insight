import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import { Card } from './ui/card';
import { v4 as uuidv4 } from 'uuid'; // We'll need a simple session ID

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatInterface() {
  const [sessionId] = useState(() => uuidv4()); // Generate unique session per mount
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Welcome to BuildSight RAG. Ask me anything about your uploaded architectural documents!' }
  ]);
  const [inputStr, setInputStr] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputStr.trim() || isLoading) return;

    const userMessage = inputStr;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputStr('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        query: userMessage,
        session_id: sessionId
      });
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.content }]);
    } catch (_error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection to BuildSight RAG API failed. Make sure the backend server is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-[600px] border shadow-sm w-full mx-auto bg-card rounded-xl overflow-hidden mt-8">
      {/* Header */}
      <div className="bg-primary/5 border-b p-4 flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          Document Query Chat
        </h3>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50/50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="h-5 w-5 text-primary" />
              </div>
            )}
            
            <div className={`px-4 py-3 rounded-2xl max-w-[80%] ${
              msg.role === 'user' 
                ? 'bg-primary text-primary-foreground rounded-tr-none' 
                : 'bg-white border shadow-sm rounded-tl-none text-card-foreground'
            }`}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                <User className="h-5 w-5 text-slate-600" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div className="px-4 py-4 rounded-2xl bg-white border shadow-sm rounded-tl-none flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t">
        <form onSubmit={handleSendMessage} className="flex gap-2 relative">
          <input
            type="text"
            value={inputStr}
            onChange={(e) => setInputStr(e.target.value)}
            disabled={isLoading}
            placeholder="Ask a question about your documents..."
            className="flex-1 px-4 py-3 bg-muted/50 border rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50 transition-all pr-12"
          />
          <button
            type="submit"
            disabled={!inputStr.trim() || isLoading}
            className="absolute right-1.5 top-1.5 bottom-1.5 p-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 disabled:opacity-50 transition-colors flex items-center justify-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </Card>
  );
}
