// ============================================================
// ChatMessage 组件 — 单条聊天消息渲染
// ============================================================

"use client";

import React, { useMemo } from "react";
import { Bot, User } from "lucide-react";
import { AnalysisResultCard } from "./AnalysisResultCard";
import type { ChatMessage as ChatMessageType } from "@/lib/store";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  const renderedContent = useMemo(() => {
    if (isUser) return message.content;

    // Simple markdown rendering for assistant messages
    return renderMarkdown(message.content);
  }, [message, isUser]);

  return (
    <div
      className={`flex gap-4 px-4 py-5 ${
        isUser
          ? "flex-row-reverse bg-transparent"
          : "bg-gray-50/50 border-b border-gray-100"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${
          isUser
            ? "bg-primary-500 text-white"
            : "bg-gradient-to-br from-primary-500 to-primary-700 text-white"
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 ${isUser ? "text-right" : "text-left"}`}>
        <div className="text-xs text-gray-400 mb-1">
          {isUser ? "You" : "BioAgent"} · {formatTime(message.timestamp)}
        </div>

        {/* User message */}
        {isUser && (
          <div className="inline-block max-w-[85%] bg-primary-500 text-white rounded-2xl rounded-tr-md px-4 py-2.5 shadow-sm">
            <p className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </p>
          </div>
        )}

        {/* Assistant message */}
        {!isUser && (
          <div className="markdown max-w-none">{renderedContent}</div>
        )}

        {/* Analysis Result Card */}
        {message.analysisResult && (
          <div className="mt-4">
            <AnalysisResultCard result={message.analysisResult} />
          </div>
        )}
      </div>
    </div>
  );
}

// ---- Simple Markdown Render ----

function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Heading
    const headingMatch = line.match(/^(#{1,6})\s+(.+)/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const headingSizes: Record<number, string> = {
        1: "text-2xl font-bold mt-6 mb-3",
        2: "text-xl font-bold mt-5 mb-2",
        3: "text-lg font-bold mt-4 mb-2",
        4: "text-base font-semibold mt-3 mb-1",
        5: "text-sm font-semibold mt-2 mb-1",
        6: "text-xs font-semibold mt-2 mb-1",
      };
      elements.push(
        React.createElement(
          `h${level}`,
          { key: `h-${i}`, className: headingSizes[level] },
          headingMatch[2]
        )
      );
      i++;
      continue;
    }

    // Code block
    if (line.startsWith("```")) {
      const language = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      elements.push(
        <pre key={`code-${i}`} className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-3">
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
      continue;
    }

    // Table
    if (line.startsWith("|")) {
      const tableRows: string[][] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        const cells = lines[i]
          .split("|")
          .slice(1, -1)
          .map((c) => c.trim());
        tableRows.push(cells);
        i++;
      }

      if (tableRows.length >= 2) {
        const header = tableRows[0];
        const body = tableRows.slice(2); // skip separator row (|---|)
        elements.push(
          <div key={`table-${i}`} className="overflow-x-auto my-4">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  {header.map((h, idx) => (
                    <th
                      key={idx}
                      className="bg-gray-100 border border-gray-300 px-3 py-2 text-left font-semibold"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {body.map((row, ri) => (
                  <tr key={ri}>
                    {row.map((cell, ci) => (
                      <td
                        key={ci}
                        className="border border-gray-300 px-3 py-1.5"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        continue;
      }
    }

    // Bold / Italic inline
    const formatted = line
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Empty line
    if (!line.trim()) {
      elements.push(<div key={`br-${i}`} className="h-3" />);
      i++;
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={`p-${i}`} className="my-2 text-sm leading-relaxed text-gray-700">
        {line}
      </p>
    );

    i++;
  }

  return <>{elements}</>;
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}