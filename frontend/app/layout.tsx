import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "BioAgent Platform — AI Bioinformatics Assistant",
  description:
    "AI-powered bioinformatics agent platform for biomedical researchers. Perform differential expression analysis, GO/KEGG enrichment, and interactive visualization.",
  keywords: [
    "bioinformatics",
    "RNA-seq",
    "differential expression",
    "DEG analysis",
    "GO enrichment",
    "KEGG pathway",
    "volcano plot",
    "heatmap",
    "AI agent",
  ],
  authors: [{ name: "BioAgent Team" }],
  openGraph: {
    title: "BioAgent Platform",
    description: "AI-powered bioinformatics agent platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-white text-gray-900 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}