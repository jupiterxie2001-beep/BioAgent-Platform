from typing import Dict, Any, Optional
import os
import json
import pandas as pd
from app.core.config import settings

class LLMProvider:
    def __init__(self):
        self.use_local = not (settings.openai_api_key and settings.openai_api_base)
    
    def _generate_interpretation_local(self, results: Dict[str, Any], query: str) -> str:
        summary = []
        
        if 'deseq2_analysis' in results:
            deg_result = results['deseq2_analysis']
            n_genes = deg_result.get('n_genes', 0)
            n_significant = deg_result.get('n_significant', 0)
            
            summary.append(f"**差异表达分析结果**")
            summary.append(f"- 分析了 {n_genes} 个基因")
            summary.append(f"- 发现 {n_significant} 个显著差异表达基因")
            summary.append(f"- 阈值标准: padj < 0.05, |log2FC| > 1")
            
            if n_significant > 0:
                summary.append(f"\n**生物学意义**")
                summary.append(f"- 差异基因可能参与关键生物学过程")
                summary.append(f"- 上调基因可能代表激活的通路")
                summary.append(f"- 下调基因可能代表抑制的功能")
                
                summary.append(f"\n**后续分析建议**")
                summary.append(f"- 进行GO/KEGG富集分析")
                summary.append(f"- 构建蛋白质互作网络")
                summary.append(f"- 验证关键基因表达")
        
        if 'scanpy_pipeline' in results:
            sc_result = results['scanpy_pipeline']
            n_cells = sc_result.get('n_cells', 0)
            n_clusters = sc_result.get('n_clusters', 0)
            
            summary.append(f"**单细胞分析结果**")
            summary.append(f"- 分析了 {n_cells} 个细胞")
            summary.append(f"- 识别到 {n_clusters} 个细胞群")
            
            if n_clusters > 0:
                summary.append(f"\n**生物学意义**")
                summary.append(f"- 细胞群可能代表不同细胞类型")
                summary.append(f"- 后续可进行细胞类型注释")
                
                summary.append(f"\n**后续分析建议**")
                summary.append(f"- 进行细胞类型注释")
                summary.append(f"- 分析差异表达基因")
                summary.append(f"- 可视化细胞轨迹")
        
        if 'cell_type_annotation' in results:
            annotation_result = results['cell_type_annotation']
            annotations = annotation_result.get('annotations', {})
            
            summary.append(f"**细胞类型注释结果**")
            for cluster_id, ann in annotations.items():
                cell_type = ann.get('cell_type', 'Unknown')
                confidence = ann.get('confidence', 0)
                summary.append(f"- Cluster {cluster_id}: {cell_type} (置信度: {confidence:.2f})")
        
        if 'run_gsea' in results:
            gsea_result = results['run_gsea']
            n_enriched = gsea_result.get('n_enriched', 0)
            
            summary.append(f"**GSEA分析结果**")
            summary.append(f"- 发现 {n_enriched} 个显著富集通路")
            
            if n_enriched > 0:
                summary.append(f"\n**生物学意义**")
                summary.append(f"- 富集通路提示潜在的生物学机制")
                
                summary.append(f"\n**后续分析建议**")
                summary.append(f"- 深入分析关键通路")
                summary.append(f"- 验证关键基因表达")
        
        if 'run_go_enrichment' in results:
            go_result = results['run_go_enrichment']
            n_bp = go_result.get('n_bp', 0)
            n_cc = go_result.get('n_cc', 0)
            n_mf = go_result.get('n_mf', 0)
            
            summary.append(f"**GO富集分析结果**")
            summary.append(f"- 生物过程(BP): {n_bp} 个显著条目")
            summary.append(f"- 细胞组分(CC): {n_cc} 个显著条目")
            summary.append(f"- 分子功能(MF): {n_mf} 个显著条目")
            
            if n_bp + n_cc + n_mf > 0:
                summary.append(f"\n**生物学意义**")
                summary.append(f"- GO注释揭示基因功能特征")
                
                summary.append(f"\n**后续分析建议**")
                summary.append(f"- 重点关注与研究目的相关的功能")
                summary.append(f"- 结合其他组学数据综合分析")
        
        if not summary:
            summary.append("**分析结果**")
            summary.append(f"查询: {query}")
            summary.append(f"结果数据已生成，请查看详细报告。")
        
        return "\n".join(summary)
    
    def _generate_interpretation_llm(self, results: Dict[str, Any], query: str) -> str:
        try:
            from langchain_openai import ChatOpenAI
            from langchain.prompts import ChatPromptTemplate
            from langchain.schema.output_parser import StrOutputParser
            
            client = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
                model_name="gpt-4o-mini"
            )
            
            system_prompt = """
            You are a senior bioinformatics scientist with 10+ years of experience. 
            Explain the analysis results in clear, concise language that a biologist can understand.
            Focus on the biological meaning and implications.
            
            Output format:
            ## 分析摘要
            [Summary of key findings]
            
            ## 生物学解释
            [Biological interpretation based on results]
            
            ## 后续建议
            [Suggestions for follow-up analysis]
            
            ## 关键基因/通路列表
            [List of important genes or pathways identified]
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Analysis results: {results}\nUser query: {query}")
            ])
            
            chain = prompt | client | StrOutputParser()
            return chain.invoke({"results": json.dumps(results, ensure_ascii=False), "query": query})
        
        except Exception as e:
            return f"LLM解释失败，使用本地解释器: {str(e)}\n\n{self._generate_interpretation_local(results, query)}"
    
    def interpret_results(self, results: Dict[str, Any], query: str = "") -> str:
        if self.use_local:
            return self._generate_interpretation_local(results, query)
        else:
            return self._generate_interpretation_llm(results, query)
    
    def parse_user_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.use_local:
            return self._parse_query_local(query, context)
        else:
            return self._parse_query_llm(query, context)
    
    def _parse_query_local(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query_lower = query.lower()
        
        task_map = {
            '差异分析': 'deg_analysis',
            'deg': 'deg_analysis',
            'differential': 'deg_analysis',
            '差异表达': 'deg_analysis',
            '单细胞': 'sc_rna_seq',
            'scrna': 'sc_rna_seq',
            'sc-seq': 'sc_rna_seq',
            'single cell': 'sc_rna_seq',
            '富集分析': 'go_enrichment',
            'go': 'go_enrichment',
            'gsea': 'gsea_analysis',
            '通路分析': 'gsea_analysis',
            '火山图': 'plot_volcano',
            '热图': 'plot_heatmap',
            '可视化': 'visualization',
        }
        
        data_type = 'bulk_rna'
        task = 'unknown'
        
        for keyword, task_name in task_map.items():
            if keyword in query_lower:
                task = task_name
                if task_name == 'sc_rna_seq':
                    data_type = 'sc_rna'
                break
        
        return {
            "task": task,
            "data_type": data_type,
            "parameters": {},
            "reasoning": f"检测到关键词 '{query}', 匹配任务类型 '{task}'"
        }
    
    def _parse_query_llm(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            from langchain_openai import ChatOpenAI
            from langchain.prompts import ChatPromptTemplate
            from langchain.schema.output_parser import StrOutputParser
            
            client = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
                model_name="gpt-4o-mini"
            )
            
            system_prompt = """
            You are a bioinformatics analysis expert. Your task is to understand user's natural language query
            and convert it into a structured task description.
            
            Available analysis types:
            - bulk_rna_seq: Bulk RNA sequencing analysis
            - sc_rna_seq: Single-cell RNA sequencing analysis
            - deg_analysis: Differential expression analysis
            - go_enrichment: GO enrichment analysis
            - gsea_analysis: GSEA pathway analysis
            - visualization: Plotting and visualization
            
            Output format: JSON
            {
                "task": "task_name",
                "data_type": "bulk_rna|sc_rna",
                "parameters": {
                    "param1": "value1",
                    ...
                },
                "reasoning": "brief explanation of your reasoning"
            }
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "User query: {query}\nContext: {context}")
            ])
            
            chain = prompt | client | StrOutputParser()
            result = chain.invoke({"query": query, "context": context or {}})
            
            try:
                return json.loads(result)
            except:
                return {
                    "task": "unknown",
                    "data_type": "bulk_rna",
                    "parameters": {},
                    "reasoning": "Failed to parse query"
                }
        
        except Exception as e:
            return self._parse_query_local(query, context)
    
    def generate_report(self, results: Dict[str, Any], query: str = "") -> str:
        interpretation = self.interpret_results(results, query)
        
        report = f"""
# 生物信息学分析报告

## 分析请求
{query}

## 分析结果解释
{interpretation}

## 报告生成时间
{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*此报告由BioAgent AI智能体自动生成*
        """
        
        return report.strip()
    
    def chat_completion(self, messages: list) -> str:
        if self.use_local:
            return self._local_chat_completion(messages)
        else:
            return self._llm_chat_completion(messages)
    
    def _local_chat_completion(self, messages: list) -> str:
        last_message = messages[-1]['content'] if messages else ""
        
        if any(keyword in last_message.lower() for keyword in ['差异分析', 'deg', 'differential']):
            return "我可以帮您进行差异表达分析。请提供表达矩阵数据，我会使用DESeq2方法进行分析并生成火山图。"
        
        elif any(keyword in last_message.lower() for keyword in ['单细胞', 'scrna', 'single cell']):
            return "我可以帮您进行单细胞RNA-seq分析。请提供h5ad格式的数据，我会进行质量控制、细胞聚类和细胞类型注释。"
        
        elif any(keyword in last_message.lower() for keyword in ['富集分析', 'go', 'gsea', '通路']):
            return "我可以帮您进行功能富集分析。请提供差异基因列表，我会进行GO和GSEA分析。"
        
        elif any(keyword in last_message.lower() for keyword in ['帮助', 'help', '功能']):
            return """我是BioAgent生物信息学AI智能体，可以帮助您完成以下分析：
            - 差异表达分析（DEG）
            - 单细胞RNA-seq分析
            - GO/KEGG富集分析
            - GSEA通路分析
            - 可视化（火山图、热图、UMAP）
            
            请告诉我您想要分析的数据类型和具体需求。"""
        
        else:
            return "您好！我是BioAgent生物信息学AI智能体。请告诉我您需要进行什么类型的生物信息学分析？"
    
    def _llm_chat_completion(self, messages: list) -> str:
        try:
            from langchain_openai import ChatOpenAI
            from langchain.prompts import ChatPromptTemplate
            from langchain.schema.output_parser import StrOutputParser
            
            client = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
                model_name="gpt-4o-mini"
            )
            
            system_prompt = """
            You are BioAgent, a helpful bioinformatics AI assistant.
            You help users with their bioinformatics analysis needs.
            Be friendly, helpful, and provide clear explanations.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                *[(m['role'], m['content']) for m in messages]
            ])
            
            chain = prompt | client | StrOutputParser()
            return chain.invoke({})
        
        except Exception as e:
            return f"LLM服务不可用: {str(e)}\n\n{self._local_chat_completion(messages)}"
