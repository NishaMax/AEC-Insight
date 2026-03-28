"use client";

import { FileUpload } from "@/components/file-upload";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send, BookOpen, FileText } from "lucide-react";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to BuildSight RAG. Upload your architectural documents and ask questions below.' }
  ]);
  const [inputStr, setInputStr] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<{ id: string, name: string }[]>([]);

  const handleUploadSuccess = (taskId: string) => {
    setUploadedFiles(prev => [...prev, { id: taskId, name: `Document - ${taskId.substring(0,6)}` }]);
  };

  const handleSendMessage = () => {
    if (!inputStr.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: inputStr }]);
    
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'assistant', content: 'This is a simulated response based on your query.' }]);
    }, 1000);

    setInputStr('');
  };

  return (
    <div className="flex h-screen w-full bg-[#FAFAFA]">
      <aside className="w-80 border-r bg-white p-6 flex flex-col gap-6 h-full shadow-sm z-20">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2 text-primary">
            <BookOpen className="h-6 w-6" />
            BuildSight RAG
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Architectural Document Intelligence</p>
        </div>

        <div className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Upload Document</h2>
          <FileUpload onSuccess={handleUploadSuccess} />
        </div>

        <div className="flex-1 overflow-hidden flex flex-col">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Recent Documents</h2>
          <ScrollArea className="flex-1">
            <div className="space-y-2 pr-4">
              {uploadedFiles.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">No documents uploaded yet.</p>
              ) : (
                uploadedFiles.map(file => (
                  <div key={file.id} className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 cursor-pointer transition-colors">
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="text-sm font-medium truncate">{file.name}</span>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </aside>

      <main className="flex-1 flex flex-col h-full bg-white relative">
        <header className="h-16 border-b flex items-center px-8 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
          <h2 className="text-lg font-semibold tracking-tight">Document Chat</h2>
        </header>

        <ScrollArea className="flex-1 px-8 py-6">
          <div className="flex flex-col gap-6 max-w-4xl mx-auto pb-4">
            {messages.map((message, i) => (
              <div key={i} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div 
                  className={`
                    max-w-[85%] rounded-2xl px-6 py-4 shadow-sm
                    ${message.role === 'user' 
                      ? 'bg-primary text-primary-foreground rounded-br-sm' 
                      : 'bg-[#F4F4F5] text-foreground rounded-bl-sm border border-black/5'}
                  `}
                >
                  <p className="text-[15px] leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="p-6 bg-white border-t">
          <div className="max-w-4xl mx-auto relative flex items-center">
            <Input 
              value={inputStr}
              onChange={(e) => setInputStr(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask a question about your architecture documents..."
              className="pr-14 h-14 rounded-2xl bg-[#F4F4F5] border-transparent focus-visible:ring-primary focus-visible:bg-white transition-all text-[15px] shadow-sm"
            />
            <Button 
              size="icon" 
              onClick={handleSendMessage}
              disabled={!inputStr.trim()}
              className="absolute right-2 rounded-xl h-10 w-10 transition-transform active:scale-95"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-center text-xs text-muted-foreground mt-3">
            BuildSight handles complex engineering & architectural documents. Verify key technical data.
          </p>
        </div>
      </main>
    </div>
  );
}
