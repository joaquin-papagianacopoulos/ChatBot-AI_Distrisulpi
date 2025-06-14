import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isUploading: boolean;
  uploadedFiles: Array<{ id: string; filename: string }>;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  isUploading,
  uploadedFiles
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700">
          {isUploading ? 'Uploading...' : 'Drop files here or click to upload'}
        </p>
        <p className="text-sm text-gray-500">
          Supports PDF, Excel files
        </p>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-700">Uploaded Files:</h3>
          {uploadedFiles.map((file) => (
            <div key={file.id} className="flex items-center space-x-2 p-2 bg-green-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <File className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-700">{file.filename}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;