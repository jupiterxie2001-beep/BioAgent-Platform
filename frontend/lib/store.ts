// ============================================================
// Zustand Store - 全局状态管理
// ============================================================

import { create } from "zustand";

// Types
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  isPartial?: boolean;
  analysisResult?: AnalysisResult;
}

export interface FileInfo {
  id: string;
  name: string;
  format: string;
  size: number;
  path?: string;
  rows?: number;
  columns?: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: number;
  datasetCount?: number;
  jobCount?: number;
}

export interface AnalysisJob {
  id: string;
  projectId: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  summary: string;
  errorMessage?: string;
  resultPath?: string;
  createdAt: string;
  completedAt?: string;
}

export interface DEGResult {
  gene_id: string;
  gene_name: string;
  log2fc: number;
  pvalue: number;
  padj: number;
  base_mean: number;
}

export interface EnrichmentResult {
  term: string;
  category: string;
  pvalue: number;
  padj: number;
  count: number;
  gene_ratio: string;
}

export interface AnalysisResult {
  type: "deg" | "enrichment" | "visualization";
  title: string;
  degResults?: DEGResult[];
  enrichmentResults?: EnrichmentResult[];
  figures?: string[]; // base64 or URLs
  summary?: string;
}

// Store
interface AppState {
  // Chat
  chatMessages: ChatMessage[];
  sendMessage: (role: "user" | "assistant", content: string) => void;
  appendToLastMessage: (content: string) => void;
  setAnalysisResult: (messageId: string, result: AnalysisResult) => void;
  clearMessages: () => void;

  // Project
  currentProject: Project | null;
  setProject: (project: Project | null) => void;
  projects: Project[];
  setProjects: (projects: Project[]) => void;

  // Analysis Jobs
  analysisJobs: AnalysisJob[];
  setAnalysisJobs: (jobs: AnalysisJob[]) => void;
  addAnalysisJob: (job: AnalysisJob) => void;
  updateAnalysisJob: (id: string, update: Partial<AnalysisJob>) => void;

  // Files
  uploadedFiles: FileInfo[];
  addFile: (file: FileInfo) => void;
  removeFile: (id: string) => void;

  // Analysis Results
  analysisResults: Record<string, AnalysisResult>;
  addResult: (id: string, result: AnalysisResult) => void;

  // UI
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  toolPanelOpen: boolean;
  toggleToolPanel: () => void;
}

let messageCounter = 0;
function generateId(): string {
  messageCounter += 1;
  return `msg_${Date.now()}_${messageCounter}`;
}

function generateFileId(): string {
  return `file_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useStore = create<AppState>((set, get) => ({
  // Chat
  chatMessages: [
    {
      id: generateId(),
      role: "assistant",
      content:
        "Welcome to BioAgent Platform. I am your AI-powered bioinformatics assistant. You can ask me to perform differential gene expression analysis, GO/KEGG enrichment, or data visualization. How can I help you today?",
      timestamp: Date.now(),
    },
  ],

  sendMessage: (role, content) => {
    const msg: ChatMessage = {
      id: generateId(),
      role,
      content,
      timestamp: Date.now(),
    };
    set((s) => ({ chatMessages: [...s.chatMessages, msg] }));
  },

  appendToLastMessage: (content) => {
    set((s) => {
      const msgs = [...s.chatMessages];
      if (msgs.length > 0 && msgs[msgs.length - 1].role === "assistant") {
        msgs[msgs.length - 1] = {
          ...msgs[msgs.length - 1],
          content: msgs[msgs.length - 1].content + content,
        };
      }
      return { chatMessages: msgs };
    });
  },

  setAnalysisResult: (messageId, result) => {
    set((s) => ({
      chatMessages: s.chatMessages.map((m) =>
        m.id === messageId ? { ...m, analysisResult: result } : m
      ),
    }));
  },

  clearMessages: () => set({ chatMessages: [] }),

  // Project
  currentProject: { id: "default", name: "Default Project", createdAt: Date.now() },
  setProject: (project) => set({ currentProject: project }),
  projects: [],
  setProjects: (projects) => set({ projects }),

  // Analysis Jobs
  analysisJobs: [],
  setAnalysisJobs: (jobs) => set({ analysisJobs: jobs }),
  addAnalysisJob: (job) =>
    set((s) => ({ analysisJobs: [...s.analysisJobs, job] })),
  updateAnalysisJob: (id, update) =>
    set((s) => ({
      analysisJobs: s.analysisJobs.map((j) =>
        j.id === id ? { ...j, ...update } : j
      ),
    })),

  // Files
  uploadedFiles: [],
  addFile: (file) =>
    set((s) => ({ uploadedFiles: [...s.uploadedFiles, { ...file, id: generateFileId() }] })),
  removeFile: (id) =>
    set((s) => ({ uploadedFiles: s.uploadedFiles.filter((f) => f.id !== id) })),

  // Analysis Results
  analysisResults: {},
  addResult: (id, result) =>
    set((s) => ({
      analysisResults: { ...s.analysisResults, [id]: result },
    })),

  // UI
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toolPanelOpen: false,
  toggleToolPanel: () => set((s) => ({ toolPanelOpen: !s.toolPanelOpen })),
}));