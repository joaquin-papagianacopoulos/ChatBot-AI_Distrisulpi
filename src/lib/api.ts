import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface ChatMessage {
  message: string;
  file_id?: string;
}

export interface ConversionRequest {
  file_id: string;
  target_format: string;
  instructions?: string;
}

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const sendMessage = async (message: ChatMessage) => {
  const response = await api.post('/chat', message);
  return response.data;
};

export const convertFile = async (request: ConversionRequest) => {
  const response = await api.post('/convert', request, {
    responseType: 'blob',
  });
  
  return response.data;
};

export const getFiles = async () => {
  const response = await api.get('/files');
  return response.data;
};