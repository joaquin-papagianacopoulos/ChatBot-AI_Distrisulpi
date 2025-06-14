import React, { useState } from 'react';
import Head from 'next/head';
import FileUpload from '../components/FileUpload';
import ChatInterface from '../components/ChatInterface';
import { uploadFile, sendMessage, convertFile } from '../lib/api';
import { Download, RefreshCw } from 'lucide-react';

interface UploadedFile {
  id: string;
  filename: string;
}

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | undefined>();
  const [isUploading, setIsUploading] = useState(false);
  const [conversionFormat, setConversionFormat] = useState('excel');
  const [conversionInstructions, setConversionInstructions] = useState('');
  const [isConverting, setIsConverting] = useState(false);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const result = await uploadFile(file);
      const newFile = { id: result.file_id, filename: result.filename };
      setUploadedFiles(prev => [...prev, newFile]);
      setSelectedFileId(result.file_id);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (message: string, fileId?: string): Promise<string> => {
    try {
      const response = await sendMessage({ message, file_id: fileId });
      return response.response;
    } catch (error) {
      throw new Error('Failed to send message');
    }
  };

  const handleConversion = async () => {
    if (!selectedFileId) return;
    
    setIsConverting(true);
    try {
      const blob = await convertFile({
        file_id: selectedFileId,
        target_format: conversionFormat,
        instructions: conversionInstructions || undefined
      });
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `converted_file.${conversionFormat === 'excel' ? 'xlsx' : 'pdf'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Conversion failed:', error);
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <>
      <Head>
        <title>AI Chatbot File Converter</title>
        <meta name="description" content="Convert files with AI assistance" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
            AI Chatbot File Converter
          </h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Upload Files</h2>
                <FileUpload
                  onFileUpload={handleFileUpload}
                  isUploading={isUploading}
                  uploadedFiles={uploadedFiles}
                />
              </div>
              
              {uploadedFiles.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold mb-4">Select File</h2>
                  <select
                    value={selectedFileId || ''}
                    onChange={(e) => setSelectedFileId(e.target.value || undefined)}
                    className="w-full border border-gray-300 rounded-lg p-2 mb-4"
                  >
                    <option value="">Select a file...</option>
                    {uploadedFiles.map((file) => (
                      <option key={file.id} value={file.id}>
                        {file.filename}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {selectedFileId && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold mb-4">Convert File</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Convert to:
                      </label>
                      <select
                        value={conversionFormat}
                        onChange={(e) => setConversionFormat(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-2"
                      >
                        <option value="excel">Excel (.xlsx)</option>
                        <option value="pdf">PDF</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        AI Instructions (optional):
                      </label>
                      <textarea
                        value={conversionInstructions}
                        onChange={(e) => setConversionInstructions(e.target.value)}
                        placeholder="e.g., 'Remove empty rows', 'Sort by date', 'Add totals column'"
                        className="w-full border border-gray-300 rounded-lg p-2"
                        rows={3}
                      />
                    </div>
                    
                    <button
                      onClick={handleConversion}
                      disabled={isConverting}
                      className="w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                    >
                      {isConverting ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          <span>Converting...</span>
                        </>
                      ) : (
                        <>
                          <Download className="h-4 w-4" />
                          <span>Convert & Download</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md h-96 lg:h-[600px]">
                <div className="h-full">
                  <div className="p-4 border-b">
                    <h2 className="text-xl font-semibold">AI Assistant</h2>
                    {selectedFileId && (
                      <p className="text-sm text-gray-500">
                        Chatting about: {uploadedFiles.find(f => f.id === selectedFileId)?.filename}
                      </p>
                    )}
                  </div>
                  <div className="h-full">
                    <ChatInterface
                      onSendMessage={handleSendMessage}
                      selectedFileId={selectedFileId}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}