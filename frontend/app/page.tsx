// ============================================================
// 主页面 — BioAgent 聊天界面
// ============================================================

"use client";

import React, { useState, useRef } from "react";
import { Send, PanelLeftClose, PanelLeft, Menu, Settings2 } from "lucide-react";
import { ChatMessage } from "@/components/ChatMessage";
import { FileUpload } from "@/components/FileUpload";
import { ToolPanel } from "@/components/ToolPanel";
import { useChat } from "@/hooks/useChat";
import { useStore } from "@/lib/store";

export default function Home() {
  const { chatMessages, send, bottomRef } = useChat();
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const {
    sidebarOpen,
    toggleSidebar,
    toolPanelOpen,
    toggleToolPanel,
    currentProject,
  } = useStore();

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || isSending) return;

    setInputValue("");
    setIsSending(true);

    await send(text);

    setIsSending(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* ---- Left Sidebar: Chat History ---- */}
      <div
        className={`flex-shrink-0 border-r border-gray-200 bg-gray-50/80 flex flex-col transition-all duration-300 overflow-hidden ${
          sidebarOpen ? "w-64" : "w-0"
        }`}
      >
        {/* Sidebar header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <span className="text-sm font-semibold text-gray-700">Projects</span>
          <button
            onClick={toggleSidebar}
            className="p-1 hover:bg-gray-200 rounded transition-colors"
          >
            <PanelLeftClose className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* Project list */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="px-3 py-2 rounded-lg bg-white border border-primary-200 shadow-sm">
            <p className="text-sm font-medium text-primary-700">
              {currentProject?.name ?? "Default Project"}
            </p>
            <p className="text-xs text-gray-400 mt-0.5">Bioinformatics Agent</p>
          </div>
          <div className="px-3 py-2 rounded-lg border border-transparent hover:bg-white hover:border-gray-200 hover:shadow-sm cursor-pointer transition-all">
            <p className="text-sm text-gray-600">Demo: RNA-seq Study</p>
            <p className="text-xs text-gray-400 mt-0.5">3 analyses completed</p>
          </div>
          <div className="px-3 py-2 rounded-lg border border-transparent hover:bg-white hover:border-gray-200 hover:shadow-sm cursor-pointer transition-all">
            <p className="text-sm text-gray-600">Project: scRNA-seq</p>
            <p className="text-xs text-gray-400 mt-0.5">1 analysis completed</p>
          </div>
        </div>

        {/* New project button */}
        <div className="p-3 border-t border-gray-200">
          <button className="w-full py-2 text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors">
            + New Project
          </button>
        </div>
      </div>

      {/* ---- Center: Chat Area ---- */}
      <div className="flex-1 flex flex-col min-w-0 bg-gray-50/30">
        {/* Top bar */}
        <header className="flex-shrink-0 flex items-center justify-between px-5 py-3 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button
                onClick={toggleSidebar}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <PanelLeft className="w-5 h-5 text-gray-500" />
              </button>
            )}
            <div>
              <h1 className="text-base font-semibold text-gray-800">
                BioAgent Platform
              </h1>
              <p className="text-xs text-gray-400">
                AI-Powered Bioinformatics Assistant
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!toolPanelOpen && (
              <button
                onClick={toggleToolPanel}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <Settings2 className="w-4 h-4" />
                Tools
              </button>
            )}
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-gray-500">Online</span>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {chatMessages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="flex-shrink-0 border-t border-gray-200 bg-white px-4 py-3">
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask BioAgent to analyze your data... e.g., Perform DEG analysis comparing treatment vs control"
              rows={1}
              className="flex-1 resize-none px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none max-h-32"
              disabled={isSending}
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isSending}
              className="flex-shrink-0 p-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              {isSending ? (
                <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line. BioAgent can analyze
            RNA-seq data, perform enrichment, and generate visualizations.
          </p>
        </div>
      </div>

      {/* ---- Right Panel: File Upload & Tools ---- */}
      <div
        className={`flex-shrink-0 border-l border-gray-200 bg-white flex flex-col transition-all duration-300 overflow-hidden ${
          toolPanelOpen ? "w-80" : "w-72"
        }`}
      >
        {toolPanelOpen ? (
          <ToolPanel />
        ) : (
          <FileUpload />
        )}
      </div>
    </div>
  );
}