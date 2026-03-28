"use client";
import { useState, useEffect } from 'react';
import { FileUpload } from '@/components/file-upload';
import { ChatInterface } from '@/components/chat-interface';
import { Trash2, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Home() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [loadingDocs, setLoadingDocs] = useState<boolean>(true);
  const [deletingDoc, setDeletingDoc] = useState<string | null>(null);

  // Fetch documents function
  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/documents');
      if (response.data && response.data.documents) {
        setDocuments(response.data.documents);
      }
    } catch (error) {
      console.error("Failed to fetch documents", error);
    } finally {
      setLoadingDocs(false);
    }
  };

  // Initial fetch on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSuccess = (taskId: string) => {
    console.log(`Successfully processed document with task: ${taskId}`);
    // Refresh document list after successful upload processing
    fetchDocuments();
  };

  const handleDeleteDocument = async (filename: string) => {
    try {
      setDeletingDoc(filename);
      await axios.delete(`http://localhost:8000/api/documents/${encodeURIComponent(filename)}`);
      // Update local state instead of doing a full refetch for snappier UI
      setDocuments(prev => prev.filter(doc => doc !== filename));
    } catch (error) {
      console.error(`Failed to delete document ${filename}`, error);
      alert('Failed to delete the document. Please ensure the backend is running.');
    } finally {
      setDeletingDoc(null);
    }
  };

  return (
    <div className="flex bg-background min-h-screen font-sans">
      <div className="flex-1 flex flex-col">
        {/* Main Header */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b px-8 py-4">
          <h2 className="text-2xl font-bold">
            Welcome to BuildSight Central
          </h2>
          <p className="text-muted-foreground mt-2 max-w-2xl text-center">
            Securely upload and query complex architectural PDFs, building codes, and zoning manuals. 
            Get AI-driven insights extracted directly from your verified sources.
          </p>
        </header>

        {/* Main Content */}
        <div className="flex-1 p-8">
          {/* Upload Section */}
          <div className="w-full max-w-3xl mx-auto">
            <FileUpload onSuccess={handleUploadSuccess} />
          </div>

          {/* Document Overview Section */}
          <div className="mt-16">
            <h3 className="text-xl font-semibold mb-6 flex items-center">
              <span className="bg-primary/10 text-primary p-2 rounded-lg mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
              </span>
              Recent Documents
            </h3>
            
            {loadingDocs ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-32 rounded-xl bg-muted animate-pulse border"></div>
                ))}
              </div>
            ) : documents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {documents.map((docName, index) => (
                  <div key={index} className="group flex flex-col justify-between p-5 rounded-xl border bg-card hover:border-primary/50 hover:shadow-md transition-all relative">
                    <div>
                      <div className="flex justify-between items-start mb-4">
                        <div className="p-2 bg-primary/10 rounded-lg text-primary">
                          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        </div>
                        <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">Ready</span>
                      </div>
                      <h4 className="font-medium text-sm truncate pr-8" title={docName}>{docName}</h4>
                      <p className="text-xs text-muted-foreground mt-1">Vectorized & embedded</p>
                    </div>
                    
                    {/* Delete overlay that appears on hover */}
                    <button 
                      onClick={() => handleDeleteDocument(docName)}
                      disabled={deletingDoc === docName}
                      className="absolute top-4 right-4 p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md opacity-0 group-hover:opacity-100 transition-all disabled:opacity-100"
                      title="Delete document"
                    >
                      {deletingDoc === docName ? (
                        <Loader2 className="h-4 w-4 animate-spin text-destructive" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center rounded-xl border border-dashed text-muted-foreground">
                <p>No documents uploaded yet. Start by uploading a PDF above.</p>
              </div>
            )}
          </div>
          
          {/* AI Chat Interface Section */}
          <div className="mt-16 pb-16">
            <h3 className="text-xl font-semibold mb-6 flex items-center">
              <span className="bg-primary/10 text-primary p-2 rounded-lg mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
              </span>
              Analyze Documents
            </h3>
            
            <div className="max-w-4xl mx-auto">
              <ChatInterface />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
