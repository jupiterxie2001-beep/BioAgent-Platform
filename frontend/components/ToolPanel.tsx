// ============================================================
// ToolPanel 组件 — 工具列表和参数配置
// ============================================================

"use client";

import React, { useState, useEffect } from "react";
import {
  Beaker,
  Dna,
  BarChart3,
  ChevronRight,
  Play,
  Settings2,
  X,
} from "lucide-react";
import { useStore } from "@/lib/store";

interface ToolInfo {
  name: string;
  description: string;
  category: string;
  icon: React.ReactNode;
  parameters: ToolParam[];
}

interface ToolParam {
  name: string;
  type: "text" | "number" | "select";
  label: string;
  default?: string;
  options?: string[];
}

const MOCK_TOOLS: ToolInfo[] = [
  {
    name: "DEG Analysis",
    description: "Identify differentially expressed genes between groups",
    category: "RNA-seq",
    icon: <Dna className="w-5 h-5" />,
    parameters: [
      { name: "control_group", type: "text", label: "Control Group", default: "control" },
      { name: "treatment_group", type: "text", label: "Treatment Group", default: "treatment" },
      { name: "log2fc_threshold", type: "number", label: "log2FC Threshold", default: "1.0" },
      { name: "padj_threshold", type: "number", label: "Adj. P Threshold", default: "0.05" },
      {
        name: "method",
        type: "select",
        label: "Method",
        default: "DESeq2",
        options: ["DESeq2", "edgeR", "limma"],
      },
    ],
  },
  {
    name: "GO Enrichment",
    description: "Gene Ontology enrichment analysis",
    category: "Enrichment",
    icon: <Beaker className="w-5 h-5" />,
    parameters: [
      { name: "organism", type: "select", label: "Organism", default: "Human", options: ["Human", "Mouse", "Rat"] },
      {
        name: "ontology",
        type: "select",
        label: "Ontology",
        default: "BP",
        options: ["BP", "CC", "MF"],
      },
      { name: "pvalue_cutoff", type: "number", label: "P-value Cutoff", default: "0.05" },
    ],
  },
  {
    name: "KEGG Enrichment",
    description: "KEGG pathway enrichment analysis",
    category: "Enrichment",
    icon: <Beaker className="w-5 h-5" />,
    parameters: [
      { name: "organism", type: "select", label: "Organism", default: "hsa", options: ["hsa", "mmu", "rno"] },
      { name: "pvalue_cutoff", type: "number", label: "P-value Cutoff", default: "0.05" },
    ],
  },
  {
    name: "Volcano Plot",
    description: "Generate interactive volcano plot",
    category: "Visualization",
    icon: <BarChart3 className="w-5 h-5" />,
    parameters: [
      { name: "log2fc_threshold", type: "number", label: "log2FC Threshold", default: "1.0" },
      { name: "padj_threshold", type: "number", label: "Adj. P Threshold", default: "0.05" },
      { name: "label_genes", type: "text", label: "Top N Genes to Label", default: "10" },
    ],
  },
  {
    name: "Heatmap",
    description: "Generate clustered expression heatmap",
    category: "Visualization",
    icon: <BarChart3 className="w-5 h-5" />,
    parameters: [
      { name: "top_n", type: "number", label: "Top N DEGs", default: "50" },
      { name: "cluster_method", type: "select", label: "Clustering", default: "ward", options: ["ward", "complete", "average"] },
    ],
  },
];

export function ToolPanel() {
  const { toolPanelOpen, toggleToolPanel } = useStore();
  const [selectedTool, setSelectedTool] = useState<ToolInfo | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [running, setRunning] = useState(false);

  const handleSelectTool = (tool: ToolInfo) => {
    setSelectedTool(tool);
    const defaults: Record<string, string> = {};
    tool.parameters.forEach((p) => {
      defaults[p.name] = p.default ?? "";
    });
    setParamValues(defaults);
  };

  const handleParamChange = (name: string, value: string) => {
    setParamValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleRun = async () => {
    setRunning(true);
    // Simulate running
    await new Promise((r) => setTimeout(r, 1500));
    setRunning(false);
    setSelectedTool(null);
  };

  if (!toolPanelOpen) {
    return (
      <button
        onClick={toggleToolPanel}
        className="absolute right-4 top-4 p-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
        title="Open Tool Panel"
      >
        <Settings2 className="w-5 h-5 text-gray-600" />
      </button>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700">Analysis Tools</h3>
        <button
          onClick={toggleToolPanel}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Tool list or config */}
      {!selectedTool ? (
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {MOCK_TOOLS.map((tool) => (
            <button
              key={tool.name}
              onClick={() => handleSelectTool(tool)}
              className="w-full flex items-center gap-3 px-3 py-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50/50 transition-all text-left group"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 group-hover:bg-primary-100 group-hover:text-primary-600">
                {tool.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800">{tool.name}</p>
                <p className="text-xs text-gray-500 truncate">{tool.description}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-primary-500" />
            </button>
          ))}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-4">
            <h4 className="text-base font-semibold text-gray-800">
              {selectedTool.name}
            </h4>
            <p className="text-sm text-gray-500 mt-1">{selectedTool.description}</p>
          </div>

          {/* Parameters */}
          <div className="space-y-4">
            {selectedTool.parameters.map((param) => (
              <div key={param.name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {param.label}
                </label>
                {param.type === "select" ? (
                  <select
                    value={paramValues[param.name] ?? ""}
                    onChange={(e) => handleParamChange(param.name, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                  >
                    {param.options?.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={param.type}
                    value={paramValues[param.name] ?? ""}
                    onChange={(e) => handleParamChange(param.name, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                  />
                )}
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-6">
            <button
              onClick={() => setSelectedTool(null)}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Back
            </button>
            <button
              onClick={handleRun}
              disabled={running}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {running ? (
                <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {running ? "Running..." : "Run"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}