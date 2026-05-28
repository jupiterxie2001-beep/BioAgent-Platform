// ============================================================
// FileUpload 组件 — 拖拽上传区域
// ============================================================

"use client";

import React, { useState, useCallback, useRef } from "react";
import { Upload, FileText, X, CheckCircle2, Loader2 } from "lucide-react";
import { useStore } from "@/lib/store";

export function FileUpload() {
  const { uploadedFiles, addFile, removeFile } = useStore();
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const files = Array.from(e.dataTransfer.files);
      await processFiles(files);
    },
    []
  );

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files ?? []);
      await processFiles(files);
      if (inputRef.current) inputRef.current.value = "";
    },
    []
  );

  async function processFiles(files: File[]) {
    const accepted = files.filter((f) => {
      const ext = f.name.split(".").pop()?.toLowerCase();
      return ["csv", "tsv", "txt", "xlsx", "xls"].includes(ext ?? "");
    });

    if (accepted.length === 0) return;

    setUploading(true);

    // Simulate upload
    for (const file of accepted) {
      await new Promise((r) => setTimeout(r, 600));
      addFile({
        name: file.name,
        format: file.name.split(".").pop() ?? "unknown",
        size: file.size,
        rows: Math.floor(Math.random() * 20000) + 5000,
        columns: Math.floor(Math.random() * 50) + 5,
      });
    }

    setUploading(false);
  }

  const totalSamples = uploadedFiles.length > 0
    ? uploadedFiles.reduce((s, f) => s + (f.rows ?? 0), 0)
    : 0;
  const totalGenes = uploadedFiles.length > 0
    ? uploadedFiles.reduce((s, f) => s + (f.columns ?? 0), 0)
    : 0;

  return (
    <div className="flex flex-col h-full">
      <h3 className="px-4 py-3 text-sm font-semibold text-gray-700 border-b border-gray-200">
        File Upload
      </h3>

      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`m-4 p-6 border-2 border-dashed rounded-xl text-center cursor-pointer transition-all ${
          isDragging
            ? "border-primary-400 bg-primary-50"
            : "border-gray-300 hover:border-primary-300 hover:bg-gray-50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.tsv,.txt,.xlsx,.xls"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
            <span className="text-sm text-gray-500">Uploading...</span>
          </div>
        ) : (
          <>
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600 font-medium">
              Drag & drop files here
            </p>
            <p className="text-xs text-gray-400 mt-1">
              or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-3">
              Supported: CSV, TSV, TXT, XLSX
            </p>
          </>
        )}
      </div>

      {/* File info summary */}
      {uploadedFiles.length > 0 && (
        <div className="px-4 pb-3">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span>
              {uploadedFiles.length} file{uploadedFiles.length > 1 ? "s" : ""} uploaded
            </span>
          </div>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <div className="text-lg font-semibold text-gray-800">
                {uploadedFiles.length}
              </div>
              <div className="text-xs text-gray-500">Files</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <div className="text-lg font-semibold text-gray-800">
                {totalSamples.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Samples</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <div className="text-lg font-semibold text-gray-800">
                {totalGenes.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Genes</div>
            </div>
          </div>

          {/* File list */}
          <div className="space-y-1.5 max-h-60 overflow-y-auto">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg group hover:bg-gray-100 transition-colors"
              >
                <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 truncate">{file.name}</p>
                  <p className="text-xs text-gray-400">
                    {formatSize(file.size)} · {file.format.toUpperCase()}
                  </p>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all"
                >
                  <X className="w-3.5 h-3.5 text-gray-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}