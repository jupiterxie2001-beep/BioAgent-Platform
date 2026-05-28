"use client";

// ============================================================
// ProjectManager — 项目管理组件（创建/切换/删除 + 分析时间线）
// ============================================================

import { useState, useEffect, useCallback } from "react";
import {
  FolderOpen,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Clock,
  Activity,
  CircleCheckBig,
  CircleAlert,
  Loader2,
  ChevronRight,
} from "lucide-react";

import {
  getProjects,
  createProject,
  deleteProject as deleteProjectApi,
  getAnalysisJobs,
} from "@/lib/api";
import { useStore, Project, AnalysisJob } from "@/lib/store";

// ---- Types ----

interface ProjectDetails {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  datasetCount: number;
  jobCount: number;
}

interface JobSummary {
  id: string;
  status: string;
  createdAt: string;
  summary: string;
}

// ---- Component ----

export default function ProjectManager() {
  const { currentProject, setProject, projects, setProjects } = useStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showTimeline, setShowTimeline] = useState<string | null>(null);
  const [timelineJobs, setTimelineJobs] = useState<JobSummary[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError("");
    try {
      const result = await getProjects();
      if (result.status === "success" && result.data) {
        const mapped: Project[] = result.data.projects.map((p: ProjectDetails) => ({
          id: p.id,
          name: p.name,
          description: p.description || "",
          createdAt: new Date(p.createdAt).getTime(),
          datasetCount: p.datasetCount,
          jobCount: p.jobCount,
        }));
        setProjects(mapped);
      } else {
        setError(result.error || "Failed to load projects");
      }
    } catch {
      setError("Network error loading projects");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newProjectName.trim()) return;
    setError("");
    try {
      const result = await createProject(newProjectName.trim(), newProjectDesc.trim());
      if (result.status === "success") {
        setIsCreating(false);
        setNewProjectName("");
        setNewProjectDesc("");
        await loadProjects();
      } else {
        setError(result.error || "Failed to create project");
      }
    } catch {
      setError("Network error creating project");
    }
  };

  const handleDelete = async (id: string) => {
    setError("");
    try {
      const result = await deleteProjectApi(id);
      if (result.status === "success") {
        if (currentProject?.id === id) {
          setProject(null);
        }
        await loadProjects();
      } else {
        setError(result.error || "Failed to delete project");
      }
    } catch {
      setError("Network error deleting project");
    }
  };

  const handleEditStart = (project: Project) => {
    setEditingId(project.id);
    setEditName(project.name);
  };

  const handleEditSave = async (id: string) => {
    if (!editName.trim()) return;
    // For now just update locally since updateProject is not in api.ts yet
    setEditingId(null);
    // TODO: Add updateProject API call
  };

  const handleSelectProject = (project: Project) => {
    setProject(project);
  };

  const loadTimeline = async (projectId: string) => {
    if (showTimeline === projectId) {
      setShowTimeline(null);
      return;
    }
    setShowTimeline(projectId);
    setTimelineLoading(true);
    try {
      const result = await getAnalysisJobs(projectId);
      if (result.status === "success" && result.data) {
        setTimelineJobs(
          result.data.jobs?.map((j: JobSummary) => ({
            id: j.id,
            status: j.status,
            createdAt: j.createdAt,
            summary: j.summary || "",
          })) || []
        );
      }
    } catch {
      setTimelineJobs([]);
    } finally {
      setTimelineLoading(false);
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CircleCheckBig size={14} className="text-green-500" />;
      case "running":
        return <Loader2 size={14} className="text-blue-500 animate-spin" />;
      case "failed":
        return <CircleAlert size={14} className="text-red-500" />;
      default:
        return <Clock size={14} className="text-gray-400" />;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <FolderOpen size={16} className="text-blue-600" />
            Projects
          </h2>
          <button
            onClick={() => setIsCreating(!isCreating)}
            className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-600 transition-colors"
            title="New Project"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
          {error}
        </div>
      )}

      {/* Create Form */}
      {isCreating && (
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="Project name"
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          />
          <input
            type="text"
            value={newProjectDesc}
            onChange={(e) => setNewProjectDesc(e.target.value)}
            placeholder="Description (optional)"
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              className="flex-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create
            </button>
            <button
              onClick={() => {
                setIsCreating(false);
                setNewProjectName("");
                setNewProjectDesc("");
              }}
              className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Project List */}
      <div className="flex-1 overflow-y-auto">
        {loading && projects.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={20} className="text-gray-400 animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="px-4 py-8 text-center text-xs text-gray-400">
            No projects yet. Click + to create one.
          </div>
        ) : (
          <div className="py-2">
            {projects.map((project) => (
              <div key={project.id}>
                <div
                  className={`group px-4 py-2.5 cursor-pointer transition-colors border-l-2 ${
                    currentProject?.id === project.id
                      ? "border-l-blue-600 bg-blue-50"
                      : "border-l-transparent hover:bg-gray-50"
                  }`}
                  onClick={() => handleSelectProject(project)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      {editingId === project.id ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="text"
                            value={editName}
                            onChange={(e) => setEditName(e.target.value)}
                            className="flex-1 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                            onClick={(e) => e.stopPropagation()}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleEditSave(project.id);
                              if (e.key === "Escape") setEditingId(null);
                            }}
                            autoFocus
                          />
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditSave(project.id);
                            }}
                            className="p-0.5 text-green-600 hover:bg-green-50 rounded"
                          >
                            <Check size={12} />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingId(null);
                            }}
                            className="p-0.5 text-gray-400 hover:bg-gray-100 rounded"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      ) : (
                        <>
                          <p className="text-sm font-medium text-gray-700 truncate">{project.name}</p>
                          <p className="text-xs text-gray-400 mt-0.5">
                            {(project as Project & { datasetCount?: number }).datasetCount ?? 0} datasets ·{" "}
                            {(project as Project & { jobCount?: number }).jobCount ?? 0} jobs
                          </p>
                        </>
                      )}
                    </div>

                    {/* Actions (visible on hover) */}
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          loadTimeline(project.id);
                        }}
                        className="p-1 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded transition-colors"
                        title="View timeline"
                      >
                        <Activity size={12} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditStart(project);
                        }}
                        className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="Rename"
                      >
                        <Edit2 size={12} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(project.id);
                        }}
                        className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                {showTimeline === project.id && (
                  <div className="ml-6 mr-2 mb-2 border-l-2 border-gray-200 pl-4 py-2">
                    {timelineLoading ? (
                      <div className="flex items-center gap-2 py-2 text-xs text-gray-400">
                        <Loader2 size={12} className="animate-spin" />
                        Loading jobs...
                      </div>
                    ) : timelineJobs.length === 0 ? (
                      <p className="text-xs text-gray-400 py-2">No analysis jobs yet.</p>
                    ) : (
                      <div className="space-y-2">
                        {timelineJobs.map((job) => (
                          <div key={job.id} className="flex items-start gap-2 py-1">
                            <div className="mt-0.5">{statusIcon(job.status)}</div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs text-gray-600 truncate">
                                {job.status === "completed"
                                  ? job.summary || "Analysis completed"
                                  : job.summary || `Job ${job.status}`}
                              </p>
                              <p className="text-xs text-gray-400 mt-0.5">
                                {new Date(job.createdAt).toLocaleString()}
                              </p>
                            </div>
                            <ChevronRight size={12} className="text-gray-300 mt-0.5 shrink-0" />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}