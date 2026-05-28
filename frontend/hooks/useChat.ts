// ============================================================
// useChat Hook — 聊天逻辑封装
// ============================================================

"use client";

import { useCallback, useRef, useEffect } from "react";
import { useStore } from "@/lib/store";
import { sendChatMessage, ChatResponse } from "@/lib/api";

export function useChat() {
  const { chatMessages, sendMessage, appendToLastMessage, setAnalysisResult, uploadedFiles } =
    useStore();

  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Send message
  const send = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      // Add user message
      sendMessage("user", text);

      // Mock response — simulate backend call
      const trimmedText = text.toLowerCase();

      // Mock delay + response
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (trimmedText.includes("deg") || trimmedText.includes("差异") || trimmedText.includes("differential")) {
        const mockResult = generateMockDEGResult();
        sendMessage("assistant", mockResult.markdown);
        setAnalysisResult(
          chatMessages[chatMessages.length - 1]?.id ?? "",
          mockResult.analysisResult
        );
      } else if (trimmedText.includes("enrichment") || trimmedText.includes("富集") || trimmedText.includes("go") || trimmedText.includes("kegg")) {
        const mockResult = generateMockEnrichmentResult();
        sendMessage("assistant", mockResult.markdown);
        setAnalysisResult(
          chatMessages[chatMessages.length - 1]?.id ?? "",
          mockResult.analysisResult
        );
      } else if (trimmedText.includes("visual") || trimmedText.includes("可视化") || trimmedText.includes("plot") || trimmedText.includes("chart")) {
        sendMessage(
          "assistant",
          "I can generate the following visualizations for you:\n\n- **Volcano Plot**: highlights significantly up- and down-regulated genes\n- **Heatmap**: clustered expression matrix of top DEGs\n- **PCA Plot**: sample grouping and batch effect detection\n- **MA Plot**: mean-variance relationship\n\nPlease upload your expression data or specify which dataset to use, and I will generate the plots."
        );
      } else if (trimmedText.includes("upload") || trimmedText.includes("上传") || uploadedFiles.length === 0) {
        sendMessage(
          "assistant",
          "To begin analysis, please upload your expression data file (CSV/TSV/TXT/XLSX format). You can drag and drop files into the upload panel on the right, or click the upload button.\n\nOnce uploaded, you can ask me to perform analyses such as:\n- **Differential Expression Analysis**: identify DEGs between groups\n- **GO/KEGG Enrichment**: functional annotation of gene lists\n- **Data Visualization**: volcano plots, heatmaps, PCA, etc."
        );
      } else {
        sendMessage(
          "assistant",
          "I understand your request. Here are the analyses I can help with:\n\n1. **Differential Expression Analysis** (DEG)\n2. **GO/KEGG Enrichment Analysis** \n3. **Data Visualization** (Volcano plot, Heatmap, PCA)\n\nPlease specify which analysis you would like to perform, and provide details such as group labels, control/treatment conditions, etc."
        );
      }
    },
    [sendMessage, setAnalysisResult, chatMessages, uploadedFiles]
  );

  return {
    chatMessages,
    send,
    bottomRef,
  };
}

// ---- Mock Data Generators ----

function generateMockDEGResult() {
  const degData = [
    { gene_id: "ENSG00000139618", gene_name: "BRCA2", log2fc: 3.45, pvalue: 1.2e-8, padj: 5.6e-7, base_mean: 4521.3 },
    { gene_id: "ENSG00000141510", gene_name: "TP53", log2fc: -2.89, pvalue: 2.3e-7, padj: 8.9e-6, base_mean: 8734.1 },
    { gene_id: "ENSG00000133703", gene_name: "KRAS", log2fc: 2.12, pvalue: 4.5e-6, padj: 1.2e-4, base_mean: 3210.5 },
    { gene_id: "ENSG00000146648", gene_name: "EGFR", log2fc: 1.98, pvalue: 8.7e-6, padj: 2.1e-4, base_mean: 6789.2 },
    { gene_id: "ENSG00000157764", gene_name: "BRAF", log2fc: -1.76, pvalue: 1.5e-5, padj: 3.4e-4, base_mean: 2901.7 },
    { gene_id: "ENSG00000134982", gene_name: "APC", log2fc: -1.45, pvalue: 2.8e-5, padj: 5.2e-4, base_mean: 5432.8 },
    { gene_id: "ENSG00000121879", gene_name: "PIK3CA", log2fc: 1.32, pvalue: 4.2e-5, padj: 7.8e-4, base_mean: 4321.6 },
    { gene_id: "ENSG00000136997", gene_name: "MYC", log2fc: 2.78, pvalue: 5.9e-5, padj: 9.1e-4, base_mean: 3567.4 },
    { gene_id: "ENSG00000169083", gene_name: "AR", log2fc: -1.21, pvalue: 7.3e-5, padj: 1.1e-3, base_mean: 2890.3 },
    { gene_id: "ENSG00000134086", gene_name: "VHL", log2fc: 1.15, pvalue: 9.1e-5, padj: 1.4e-3, base_mean: 2345.9 },
  ];

  const upCount = degData.filter((d) => d.log2fc > 0).length;
  const downCount = degData.filter((d) => d.log2fc < 0).length;

  const markdown = `## Differential Expression Analysis Results

**Summary**: Identified **${upCount} up-regulated** and **${downCount} down-regulated** genes (|log2FC| > 1, padj < 0.05).

### Top Differentially Expressed Genes

${generateMarkdownTable(degData)}

### Key Findings

- **BRCA2** (log2FC = 3.45, padj = 5.6e-7) is the most significantly up-regulated gene, suggesting DNA repair pathway activation
- **TP53** (log2FC = -2.89, padj = 8.9e-6) shows strong down-regulation, consistent with tumor suppressor inactivation
- Oncogene **MYC** (log2FC = 2.78) is highly up-regulated, indicating proliferative signaling

### Visualization

The following plots have been generated:
- **Volcano Plot**: [volcano_plot.png] — highlights DEGs with |log2FC| > 1 & padj < 0.05
- **Heatmap**: [heatmap.png] — clustered expression of top 50 DEGs
- **PCA Plot**: [pca_plot.png] — clear separation between treatment and control groups`;

  return {
    markdown,
    analysisResult: {
      type: "deg" as const,
      title: "Differential Expression Analysis",
      degResults: degData,
      summary: `Found ${upCount} up-regulated and ${downCount} down-regulated genes`,
    },
  };
}

function generateMockEnrichmentResult() {
  const enrichmentData = [
    { term: "DNA repair", category: "GO:BP", pvalue: 1.2e-8, padj: 3.5e-6, count: 45, gene_ratio: "45/200" },
    { term: "Cell cycle", category: "GO:BP", pvalue: 5.6e-7, padj: 8.2e-5, count: 38, gene_ratio: "38/200" },
    { term: "Apoptotic process", category: "GO:BP", pvalue: 2.3e-6, padj: 2.1e-4, count: 32, gene_ratio: "32/200" },
    { term: "p53 signaling pathway", category: "KEGG", pvalue: 4.5e-6, padj: 3.4e-4, count: 28, gene_ratio: "28/200" },
    { term: "PI3K-Akt signaling", category: "KEGG", pvalue: 1.2e-5, padj: 6.7e-4, count: 35, gene_ratio: "35/200" },
    { term: "Nucleus", category: "GO:CC", pvalue: 8.9e-5, padj: 2.3e-3, count: 52, gene_ratio: "52/200" },
    { term: "Protein binding", category: "GO:MF", pvalue: 3.4e-4, padj: 5.8e-3, count: 68, gene_ratio: "68/200" },
    { term: "MAPK signaling", category: "KEGG", pvalue: 5.6e-4, padj: 8.2e-3, count: 22, gene_ratio: "22/200" },
  ];

  const markdown = `## GO/KEGG Enrichment Analysis Results

### GO Biological Process

| Term | P-value | Adj. P-value | Count | Gene Ratio |
|------|---------|-------------|-------|------------|
| DNA repair | 1.2e-8 | 3.5e-6 | 45 | 45/200 |
| Cell cycle | 5.6e-7 | 8.2e-5 | 38 | 38/200 |
| Apoptotic process | 2.3e-6 | 2.1e-4 | 32 | 32/200 |

### KEGG Pathways

| Pathway | P-value | Adj. P-value | Count | Gene Ratio |
|---------|---------|-------------|-------|------------|
| p53 signaling pathway | 4.5e-6 | 3.4e-4 | 28 | 28/200 |
| PI3K-Akt signaling | 1.2e-5 | 6.7e-4 | 35 | 35/200 |
| MAPK signaling | 5.6e-4 | 8.2e-3 | 22 | 22/200 |

### Interpretation

- **DNA repair** and **Cell cycle** are the top enriched GO terms, consistent with genomic instability in cancer
- **p53 signaling** and **PI3K-Akt** pathways are significantly enriched, suggesting key cancer driver pathway activation
- These results align with the DEG findings (TP53 down-regulation, MYC up-regulation)`;

  return {
    markdown,
    analysisResult: {
      type: "enrichment" as const,
      title: "GO/KEGG Enrichment Analysis",
      enrichmentResults: enrichmentData,
      summary: "Top enriched terms: DNA repair, Cell cycle, p53 signaling pathway",
    },
  };
}

function generateMarkdownTable(data: Array<Record<string, unknown>>): string {
  if (data.length === 0) return "";
  const headers = Object.keys(data[0]);
  const headerRow = `| ${headers.join(" | ")} |`;
  const sepRow = `| ${headers.map(() => "---").join(" | ")} |`;
  const dataRows = data
    .map((row) => {
      const vals = headers.map((h) => {
        const v = row[h];
        if (typeof v === "number") {
          if (Math.abs(v as number) < 1e-4) return (v as number).toExponential(2);
          return (v as number).toFixed(4);
        }
        return String(v);
      });
      return `| ${vals.join(" | ")} |`;
    })
    .join("\n");
  return `${headerRow}\n${sepRow}\n${dataRows}`;
}