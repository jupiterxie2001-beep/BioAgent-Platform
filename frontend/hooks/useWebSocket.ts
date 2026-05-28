// ============================================================
// useWebSocket Hook — WebSocket 连接与实时进度
// ============================================================

"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface WebSocketMessage {
  type: "progress" | "result" | "error" | "complete";
  data: unknown;
}

interface ProgressData {
  step: string;
  progress: number; // 0–100
  message: string;
}

export function useWebSocket(url?: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [lastResult, setLastResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = url ?? `ws://${window.location.hostname}:8000/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("WebSocket connected");
      setConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const msg: WebSocketMessage = JSON.parse(event.data);
        switch (msg.type) {
          case "progress":
            setProgress(msg.data as ProgressData);
            break;
          case "result":
            setLastResult(msg.data);
            break;
          case "error":
            setError(String(msg.data));
            break;
          case "complete":
            setProgress(null);
            break;
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onerror = (event) => {
      console.error("WebSocket error:", event);
      setError("WebSocket connection error");
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setConnected(false);
      setProgress(null);
    };

    wsRef.current = ws;
  }, [url]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    connected,
    progress,
    lastResult,
    error,
    send,
    connect,
    disconnect,
  };
}