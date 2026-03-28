import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import axios from 'axios';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface FileUploadProps {
  onSuccess?: (taskId: string) => void;
  className?: string;
}

export function FileUpload({ onSuccess, className }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSuccess(true);
      if (onSuccess) {
        onSuccess(response.data.task_id);
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred during upload.');
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setUploading(false);
    }
  }, [onSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  return (
    <Card className={cn('w-full border-dashed border-2', isDragActive ? 'border-primary bg-primary/5' : 'border-muted', className)}>
      <CardContent
        {...getRootProps()}
        className="flex flex-col items-center justify-center py-12 px-6 text-center cursor-pointer min-h-[250px]"
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
            <p className="text-sm text-muted-foreground">Uploading document...</p>
          </div>
        ) : success ? (
          <div className="flex flex-col items-center gap-4 text-green-600">
            <CheckCircle className="h-12 w-12" />
            <p className="text-sm font-medium">Document uploaded successfully!</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 text-muted-foreground transition-colors hover:text-foreground">
            <UploadCloud className="h-12 w-12" />
            <div className="space-y-1">
              <p className="text-sm font-medium">
                Drag & drop your architecture document here
              </p>
              <p className="text-xs">
                or click to browse (PDF only)
              </p>
            </div>
            {error && (
              <div className="flex items-center gap-2 text-destructive mt-4 text-sm">
                <AlertCircle className="h-4 w-4" />
                <p>{error}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
