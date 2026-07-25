import React from 'react';

interface Attachment {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadProgress?: number;
}

interface AttachmentsProps {
  files: Attachment[];
  onRemove: (id: string) => void;
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
};

const getTypeIcon = (type: string) => {
  if (type.startsWith('image/')) return '🖼️';
  if (type.startsWith('text/')) return '📄';
  if (type.includes('pdf')) return '📕';
  if (type.includes('zip') || type.includes('tar') || type.includes('rar')) return '📦';
  if (type.includes('json') || type.includes('yaml') || type.includes('xml')) return '📋';
  if (type.includes('javascript') || type.includes('python') || type.includes('typescript')) return '💻';
  return '📎';
};

export default function Attachments({ files, onRemove }: AttachmentsProps) {
  if (files.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 pb-2">
      {files.map((file) => (
        <div
          key={file.id}
          className="group relative flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-3 py-1.5"
        >
          <span className="text-sm">{getTypeIcon(file.type)}</span>
          <div className="flex flex-col">
            <span className="text-xs font-medium text-gray-300 max-w-[150px] truncate">
              {file.name}
            </span>
            <span className="text-[10px] text-gray-500">{formatSize(file.size)}</span>
          </div>

          {file.uploadProgress !== undefined && file.uploadProgress < 100 && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-gray-800">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${file.uploadProgress}%` }}
              />
            </div>
          )}

          <button
            onClick={() => onRemove(file.id)}
            className="ml-1 rounded-full p-0.5 text-gray-500 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 transition-all"
            title="Remove file"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
