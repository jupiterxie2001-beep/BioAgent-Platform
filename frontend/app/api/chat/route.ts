// ============================================================
// Next.js API Route — /api/chat
// ============================================================

import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, projectId } = body;

    if (!message || typeof message !== "string") {
      return NextResponse.json(
        { error: "Message is required and must be a string" },
        { status: 400 }
      );
    }

    // Mock response for now — in production, call backend /api/v1/agent/run
    const mockResponse = {
      workflow: {
        name: "DEG Analysis",
        steps: [
          {
            step_id: "deg_analysis",
            tool_name: "DEGAnalysisTool",
            parameters: {
              expression_file_path: "/data/expression.csv",
              group_labels: ["control", "treatment"],
              control_group: "control",
              treatment_group: "treatment",
              output_dir: "/output/deg",
            },
          },
        ],
      },
      execution: {
        status: "completed",
        steps: [
          {
            step_id: "deg_analysis",
            status: "success",
            output: {
              deg_results: "/output/deg/results.csv",
              volcano_plot: "/output/deg/volcano.png",
              heatmap: "/output/deg/heatmap.png",
            },
          },
        ],
      },
      results: {
        deg_results: [
          {
            gene_id: "ENSG00000139618",
            gene_name: "BRCA2",
            log2fc: 3.45,
            pvalue: 1.2e-8,
            padj: 5.6e-7,
            base_mean: 4521.3,
          },
        ],
      },
      interpretation: {
        results_summary:
          "Identified 45 up-regulated and 32 down-regulated genes (|log2FC| > 1, padj < 0.05).",
        figure_legends:
          "Volcano plot highlights significant DEGs; heatmap shows clustered expression patterns.",
        methods:
          "Differential expression analysis performed using DESeq2 with default parameters.",
        discussion:
          "Results indicate activation of DNA repair pathways and down-regulation of tumor suppressors.",
      },
      report:
        "## Differential Expression Analysis Report\n\n### Summary\n\nWe identified 45 up-regulated and 32 down-regulated genes...",
    };

    return NextResponse.json({
      response: mockResponse,
      status: "success",
    });
  } catch (err) {
    console.error("Chat API error:", err);
    return NextResponse.json(
      { error: "Internal server error", status: "error" },
      { status: 500 }
    );
  }
}