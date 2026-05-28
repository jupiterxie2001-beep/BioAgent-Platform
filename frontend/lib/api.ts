// ============================================================
// API Client - 统一封装后端接口调用
// ============================================================

const BACKEND_BASE = "/api/v1";

interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
  status: "success" | "error";
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${BACKEND_BASE}${endpoint}`;
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const errorBody = await res.text();
      return { status: "error", error: `HTTP ${res.status}: ${errorBody}` };
    }

    const data = await res.json();
    return { data, status: "success" };
  } catch (err) {
    return {
      status: "error",
      error: err instanceof Error ? err.message : "Unknown error",
    };
  }
}

// ---- Chat ----

export async function sendChatMessage(
  message: string,
  projectId?: string
): Promise<ApiResponse<ChatResponse>> {
  return request<ChatResponse>("/agent/run", {
    method: "POST",
    body: JSON.stringify({
      task: message,
      projectId: projectId ?? undefined,
      use_mock: true,
    }),
  });
}

// ---- Tools ----

export interface ToolInfo {
  name: string;
  description: string;
  category: string;
  parameters: Record<string, unknown>;
}

export async function getAvailableTools(): Promise<ApiResponse<ToolInfo[]>> {
  return request<ToolInfo[]>("/agent/tools");
}

// ---- File Upload ----

export interface FileInfoResponse {
  filename: string;
  size: number;
  rows: number;
  columns: number;
  file_path: string;
}

export async function uploadFile(
  file: File
): Promise<ApiResponse<FileInfoResponse>> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const url = `${BACKEND_BASE}/files/upload`;
    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errorBody = await res.text();
      return { status: "error", error: `HTTP ${res.status}: ${errorBody}` };
    }

    const data = await res.json();
    return { data, status: "success" };
  } catch (err) {
    return {
      status: "error",
      error: err instanceof Error ? err.message : "Unknown error",
    };
  }
}

// ---- Analysis ----

export interface AnalysisParams {
  tool_name: string;
  parameters: Record<string, unknown>;
}

export async function runAnalysis(
  params: AnalysisParams
): Promise<ApiResponse<unknown>> {
  return request("/agent/run", {
    method: "POST",
    body: JSON.stringify({
      task: `Run ${params.tool_name} with parameters: ${JSON.stringify(params.parameters)}`,
      use_mock: true,
    }),
  });
}

// ---- Projects ----

export interface ProjectData {
  id: string;
  project_name: string;
  description: string;
  created_at: string;
  updated_at: string;
  datasets: unknown[];
  analysis_jobs: unknown[];
}

export interface ProjectListResponse {
  total: number;
  projects: ProjectData[];
}

export async function getProjects(): Promise<ApiResponse<ProjectListResponse>> {
  return request<ProjectListResponse>("/projects");
}

export async function createProject(
  projectName: string,
  description: string = ""
): Promise<ApiResponse<ProjectData>> {
  return request<ProjectData>("/projects", {
    method: "POST",
    body: JSON.stringify({ project_name: projectName, description }),
  });
}

export async function deleteProject(id: string): Promise<ApiResponse<null>> {
  return request<null>(`/projects/${id}`, { method: "DELETE" });
}

export async function updateProject(
  id: string,
  data: { project_name?: string; description?: string }
): Promise<ApiResponse<ProjectData>> {
  return request<ProjectData>(`/projects/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// ---- Files ----

export interface FileData {
  id: string;
  dataset_name: string;
  file_path: string;
  dataset_type: string;
  file_size: number;
  file_format: string;
  sample_count: number;
  gene_count: number;
  data_type: string;
  uploaded_at: string;
}

export interface FileListResponse {
  total: number;
  files: FileData[];
}

export async function getFiles(): Promise<ApiResponse<FileListResponse>> {
  return request<FileListResponse>("/files");
}

export async function deleteFileRecord(id: string): Promise<ApiResponse<null>> {
  return request<null>(`/files/${id}`, { method: "DELETE" });
}

// ---- Analysis Jobs ----

export interface AnalysisJobData {
  id: string;
  project_id: string;
  status: string;
  progress: number;
  result_summary: string;
  error_message: string;
  result_path: string;
  created_at: string;
  completed_at: string | null;
}

export interface AnalysisJobListResponse {
  total: number;
  jobs: AnalysisJobData[];
}

export async function getAnalysisJobs(
  projectId?: string,
  status?: string
): Promise<ApiResponse<AnalysisJobListResponse>> {
  const params = new URLSearchParams();
  if (projectId) params.set("project_id", projectId);
  if (status) params.set("status", status);
  const qs = params.toString();
  return request<AnalysisJobListResponse>(`/analysis/jobs${qs ? `?${qs}` : ""}`);
}

export async function getAnalysisJobDetail(
  jobId: string
): Promise<ApiResponse<AnalysisJobData>> {
  return request<AnalysisJobData>(`/analysis/jobs/${jobId}`);
}

export async function getAnalysisReport(
  jobId: string
): Promise<ApiResponse<string>> {
  return request<string>(`/analysis/jobs/${jobId}/report`);
}

export async function runAnalysisJob(params: {
  expression_file_path: string;
  control_group: string;
  treatment_group: string;
  project_id?: string;
}): Promise<ApiResponse<{ job_id: string; status: string; message: string }>> {
  return request("/analysis/run", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

// ---- Types ----

export interface ChatResponse {
  workflow: unknown;
  execution: unknown;
  results: unknown;
  interpretation: InterpretationResult;
  report: string;
}

export interface InterpretationResult {
  results_summary: string;
  figure_legends: string;
  methods: string;
  discussion: string;
}