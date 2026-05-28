"use client";

// ============================================================
// ReportViewer — 分析报告查看器（四段式 Markdown 渲染）
// ============================================================

import { useState, useMemo } from "react";
import {
  FileText,
  Download,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Microscope,
  Beaker,
  MessageSquare,
} from "lucide-react";

// ---- Simple Markdown Renderer ----

function renderMarkdown(text: string): string {
  if (!text) return "";

  let html = text
    // Code blocks (must be before inline code)
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
      return `<pre class="bg-gray-100 rounded-lg p-4 my-3 overflow-x-auto text-sm font-mono"><code>${escapeHtml(code.trim())}</code></pre>`;
    })
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
    // Headers
    .replace(/^#### (.+)$/gm, '<h4 class="text-base font-semibold mt-4 mb-2">$1</h4>')
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-5 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-gray-800">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-8 mb-4 text-gray-900">$1</h1>')
    // Bold (**) — must come after headers
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    // Italic (*)
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Unordered lists
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc my-0.5">$1</li>')
    // Horizontal rules
    .replace(/^---$/gm, '<hr class="my-4 border-gray-200" />')
    // Paragraphs (double newlines)
    .replace(/\n\n/g, '<br /><br />');

  return html;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ---- Report Section Interface ----

interface ReportSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  content: string;
}

interface ReportViewerProps {
  reportMarkdown?: string;
  sections?: {
    results?: string;
    figure_legends?: string;
    methods?: string;
    discussion?: string;
  };
  title?: string;
}

export default function ReportViewer({
  reportMarkdown,
  sections,
  title = "Bioinformatics Analysis Report",
}: ReportViewerProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    results: true,
    figures: true,
    methods: false,
    discussion: true,
  });
  const [copied, setCopied] = useState(false);

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const reportSections: ReportSection[] = useMemo(() => {
    if (sections) {
      return [
        {
          id: "results",
          title: "Results",
          icon: <BarChart3 size={18} className="text-green-600" />,
          content: sections.results || "",
        },
        {
          id: "figures",
          title: "Figure Legends",
          icon: <Microscope size={18} className="text-purple-600" />,
          content: sections.figure_legends || "",
        },
        {
          id: "methods",
          title: "Methods",
          icon: <Beaker size={18} className="text-blue-600" />,
          content: sections.methods || "",
        },
        {
          id: "discussion",
          title: "Discussion",
          icon: <MessageSquare size={18} className="text-orange-600" />,
          content: sections.discussion || "",
        },
      ];
    }
    return [];
  }, [sections]);

  const handleCopy = async () => {
    const text = reportMarkdown || reportSections.map((s) => `## ${s.title}\n\n${s.content}`).join("\n\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportPDF = () => {
    // For now, offer the markdown download
    const text = reportMarkdown || reportSections.map((s) => `## ${s.title}\n\n${s.content}`).join("\n\n");
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "analysis_report.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // If full markdown provided, parse it into sections
  const parsedFullReport = useMemo(() => {
    if (!reportMarkdown) return null;

    const lines = reportMarkdown.split("\n");
    const sections: { title: string; id: string; icon: React.ReactNode; content: string }[] = [];
    let currentSection: { title: string; id: string; icon: React.ReactNode; content: string[] } | null = null;

    const iconMap: Record<string, React.ReactNode> = {
      results: <BarChart3 size={18} className="text-green-600" />,
      abstract: <FileText size={18} className="text-gray-600" />,
      "figure legends": <Microscope size={18} className="text-purple-600" />,
      methods: <Beaker size={18} className="text-blue-600" />,
      discussion: <MessageSquare size={18} className="text-orange-600" />,
      "supplementary information": <FileText size={18} className="text-gray-500" />,
    };

    for (const line of lines) {
      const h2Match = line.match(/^## (.+)/);
      if (h2Match) {
        if (currentSection) {
          sections.push({
            ...currentSection,
            content: currentSection.content.join("\n"),
          });
        }
        const title = h2Match[1];
        const id = title.toLowerCase().replace(/\s+/g, "_");
        currentSection = {
          title,
          id,
          icon: iconMap[title.toLowerCase()] || <FileText size={18} className="text-gray-600" />,
          content: [],
        };
      } else if (currentSection) {
        currentSection.content.push(line);
      }
    }

    if (currentSection) {
      sections.push({
        ...currentSection,
        content: currentSection.content.join("\n"),
      });
    }

    return sections;
  }, [reportMarkdown]);

  const displaySections = reportSections.length > 0 ? reportSections : parsedFullReport || [];

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText size={20} className="text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 text-sm">{title}</h3>
            <p className="text-xs text-gray-500">AI-Generated Analysis Report</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
            {copied ? "Copied" : "Copy"}
          </button>
          <button
            onClick={handleExportPDF}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 border border-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download size={14} />
            Export PDF
          </button>
        </div>
      </div>

      {/* Sections */}
      <div className="divide-y divide-gray-100">
        {displaySections.map((section) => {
          const isExpanded = expandedSections[section.id] ?? true;
          return (
            <div key={section.id} className="group">
              {/* Section Header */}
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  {section.icon}
                  <span className="font-medium text-gray-700 text-sm">{section.title}</span>
                  {section.content && (
                    <span className="text-xs text-gray-400">
                      ({section.content.split("\n").filter(Boolean).length} lines)
                    </span>
                  )}
                </div>
                {isExpanded ? (
                  <ChevronUp size={18} className="text-gray-400" />
                ) : (
                  <ChevronDown size={18} className="text-gray-400" />
                )}
              </button>

              {/* Section Content */}
              {isExpanded && section.content && (
                <div className="px-6 pb-5">
                  <div
                    className="prose prose-sm max-w-none text-gray-700 leading-relaxed text-sm"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(section.content) }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-5 py-3 bg-gray-50 border-t border-gray-100 text-center">
        <p className="text-xs text-gray-400">
          Generated by BioAgent Platform — AI-powered bioinformatics analysis
        </p>
      </div>
    </div>
  );
}