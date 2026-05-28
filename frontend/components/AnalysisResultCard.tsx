// ============================================================
// AnalysisResultCard — 分析结果卡片组件
// ============================================================

"use client";

import React, { useState, useCallback } from "react";
import { ChevronDown, ChevronUp, Download, Table2, BarChart3 } from "lucide-react";
import type { AnalysisResult, DEGResult, EnrichmentResult } from "@/lib/store";

interface AnalysisResultCardProps {
  result: AnalysisResult;
}

export function AnalysisResultCard({ result }: AnalysisResultCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<"table" | "chart">("table");
  const [degPage, setDegPage] = useState(0);
  const [enrichPage, setEnrichPage] = useState(0);
  const pageSize = 10;

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 bg-gradient-to-r from-primary-50 to-blue-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
          <h3 className="font-semibold text-gray-800">{result.title}</h3>
          <span className="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full uppercase">
            {result.type}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {expanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Summary */}
      {result.summary && (
        <div className="px-5 py-3 text-sm text-gray-600 bg-white border-b border-gray-100">
          {result.summary}
        </div>
      )}

      {expanded && (
        <>
          {/* Tabs */}
          <div className="flex border-b border-gray-200 bg-gray-50">
            <button
              onClick={() => setActiveTab("table")}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors ${
                activeTab === "table"
                  ? "text-primary-600 border-b-2 border-primary-500 bg-white"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <Table2 className="w-4 h-4" /> Data Table
            </button>
            <button
              onClick={() => setActiveTab("chart")}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors ${
                activeTab === "chart"
                  ? "text-primary-600 border-b-2 border-primary-500 bg-white"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <BarChart3 className="w-4 h-4" /> Charts
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            {activeTab === "table" && result.type === "deg" && result.degResults && (
              <DEGDataTable data={result.degResults} page={degPage} onPageChange={setDegPage} />
            )}
            {activeTab === "table" && result.type === "enrichment" && result.enrichmentResults && (
              <EnrichmentDataTable
                data={result.enrichmentResults}
                page={enrichPage}
                onPageChange={setEnrichPage}
              />
            )}
            {activeTab === "chart" && result.type === "deg" && (
              <ChartPlaceholders
                charts={["Volcano Plot", "Heatmap", "PCA Plot", "MA Plot"]}
              />
            )}
            {activeTab === "chart" && result.type === "enrichment" && (
              <ChartPlaceholders
                charts={["Bar Plot (GO)", "Dot Plot (KEGG)", "Enrichment Map"]}
              />
            )}
            {activeTab === "chart" && result.type === "visualization" && (
              <ChartPlaceholders
                charts={result.figures?.map((_, i) => `Figure ${i + 1}`) ?? ["Plot 1"]}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ---- DEG Data Table ----

function DEGDataTable({
  data,
  page,
  onPageChange,
}: {
  data: DEGResult[];
  page: number;
  onPageChange: (p: number) => void;
}) {
  const totalPages = Math.ceil(data.length / 10);
  const paged = data.slice(page * 10, page * 10 + 10);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border-b border-gray-200 font-semibold">Gene</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">log2FC</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">P-value</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">Adj. P</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">Base Mean</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr
                key={i}
                className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
              >
                <td className="p-2 font-medium text-gray-800">{row.gene_name}</td>
                <td
                  className={`p-2 text-right ${
                    row.log2fc > 0 ? "text-red-600" : "text-blue-600"
                  }`}
                >
                  {row.log2fc.toFixed(2)}
                </td>
                <td className="p-2 text-right text-gray-600">{row.pvalue.toExponential(2)}</td>
                <td className="p-2 text-right text-gray-600">{row.padj.toExponential(2)}</td>
                <td className="p-2 text-right text-gray-600">{row.base_mean.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
          <span>
            Showing {page * 10 + 1}-{Math.min(page * 10 + 10, data.length)} of {data.length}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => onPageChange(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              Prev
            </button>
            <button
              onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ---- Enrichment Data Table ----

function EnrichmentDataTable({
  data,
  page,
  onPageChange,
}: {
  data: EnrichmentResult[];
  page: number;
  onPageChange: (p: number) => void;
}) {
  const totalPages = Math.ceil(data.length / 10);
  const paged = data.slice(page * 10, page * 10 + 10);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border-b border-gray-200 font-semibold">Term</th>
              <th className="text-left p-2 border-b border-gray-200 font-semibold">Category</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">P-value</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">Adj. P</th>
              <th className="text-right p-2 border-b border-gray-200 font-semibold">Count</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr
                key={i}
                className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
              >
                <td className="p-2 font-medium text-gray-800">{row.term}</td>
                <td className="p-2">
                  <span className="text-xs px-1.5 py-0.5 bg-gray-100 rounded">{row.category}</span>
                </td>
                <td className="p-2 text-right text-gray-600">{row.pvalue.toExponential(2)}</td>
                <td className="p-2 text-right text-gray-600">{row.padj.toExponential(2)}</td>
                <td className="p-2 text-right text-gray-600">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
          <span>
            Showing {page * 10 + 1}-{Math.min(page * 10 + 10, data.length)} of {data.length}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => onPageChange(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              Prev
            </button>
            <button
              onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ---- Chart Placeholders ----

function ChartPlaceholders({ charts }: { charts: string[] }) {
  const colors = [
    "from-red-100 to-red-50 border-red-200",
    "from-blue-100 to-blue-50 border-blue-200",
    "from-green-100 to-green-50 border-green-200",
    "from-purple-100 to-purple-50 border-purple-200",
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {charts.map((name, i) => (
        <div
          key={i}
          className={`bg-gradient-to-br ${colors[i % colors.length]} border rounded-xl p-6 flex flex-col items-center justify-center min-h-[200px]`}
        >
          <BarChart3 className="w-8 h-8 text-gray-400 mb-2" />
          <span className="text-sm font-medium text-gray-600">{name}</span>
          <span className="text-xs text-gray-400 mt-1">Click to view interactive plot</span>
        </div>
      ))}
    </div>
  );
}