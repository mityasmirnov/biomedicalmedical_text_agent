"""
Retrieval-Augmented Generation (RAG) system for biomedical data.
"""

from typing import List, Dict, Any, Optional
from core.base import ProcessingResult
from core.logging_config import get_logger
from database.vector_manager import VectorManager
from database.sqlite_manager import SQLiteManager
from core.llm_client.openrouter_client import OpenRouterClient

log = get_logger(__name__)

class RAGSystem:
    """RAG system for answering questions about biomedical data."""
    
    def __init__(self, 
                 vector_manager: Optional[VectorManager] = None,
                 sqlite_manager: Optional[SQLiteManager] = None,
                 llm_client: Optional[OpenRouterClient] = None):
        
        self.vector_manager = vector_manager or VectorManager()
        self.sqlite_manager = sqlite_manager or SQLiteManager()
        self.llm_client = llm_client or OpenRouterClient()
        
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for RAG responses."""
        return """You are a biomedical research assistant specialized in analyzing patient data from scientific literature.

Your role is to answer questions about patient records, genetic information, clinical phenotypes, and treatments based on the provided context from medical literature.

Guidelines:
1. Base your answers ONLY on the provided context from the retrieved documents
2. If the context doesn't contain enough information, clearly state this limitation
3. Use precise medical terminology when appropriate
4. Cite specific patient cases or studies when relevant
5. Distinguish between facts from the literature and general medical knowledge
6. For genetic information, use standard nomenclature (HGNC gene symbols, HGVS mutation notation)
7. For phenotypes, use HPO terms when possible
8. Always indicate the source of information (PMID, patient ID, etc.)

Format your responses clearly with:
- Direct answer to the question
- Supporting evidence from the context
- Source citations
- Any limitations or caveats"""
    
    async def answer_question(self, 
                            question: str, 
                            max_context_docs: int = 5,
                            include_patient_records: bool = True) -> ProcessingResult[Dict[str, Any]]:
        """
        Answer a question using RAG approach.
        
        Args:
            question: The question to answer
            max_context_docs: Maximum number of documents to retrieve for context
            include_patient_records: Whether to include patient record data
            
        Returns:
            ProcessingResult containing the answer and metadata
        """
        try:
            log.info(f"Processing RAG question: {question[:100]}...")
            
            # Step 1: Retrieve relevant documents
            retrieval_result = await self._retrieve_context(question, max_context_docs)
            if not retrieval_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Context retrieval failed: {retrieval_result.error}"
                )
            
            context_docs = retrieval_result.data
            
            # Step 2: Retrieve relevant patient records if requested
            patient_context = []
            if include_patient_records:
                patient_result = await self._retrieve_patient_context(question)
                if patient_result.success:
                    patient_context = patient_result.data
            
            # Step 3: Build context for LLM
            context = self._build_context(context_docs, patient_context)
            
            # Step 4: Generate answer using LLM
            answer_result = await self._generate_answer(question, context)
            if not answer_result.success:
                return ProcessingResult(
                    success=False,
                    error=f"Answer generation failed: {answer_result.error}"
                )
            
            answer = answer_result.data
            
            # Step 5: Prepare response
            response = {
                "question": question,
                "answer": answer,
                "context_documents": len(context_docs),
                "patient_records": len(patient_context),
                "sources": self._extract_sources(context_docs, patient_context),
                "context_used": context[:1000] + "..." if len(context) > 1000 else context
            }
            
            return ProcessingResult(
                success=True,
                data=response,
                metadata={
                    "retrieval_method": "vector_similarity",
                    "llm_model": getattr(self.llm_client, 'model_name', 'unknown'),
                    "context_length": len(context)
                }
            )
            
        except Exception as e:
            log.error(f"Error in RAG question answering: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"RAG processing failed: {str(e)}"
            )
    
    async def _retrieve_context(self, question: str, max_docs: int) -> ProcessingResult[List[Dict[str, Any]]]:
        """Retrieve relevant documents using vector similarity."""
        try:
            # Search vector database
            search_result = self.vector_manager.search(question, top_k=max_docs)
            if not search_result.success:
                return search_result
            
            return ProcessingResult(
                success=True,
                data=search_result.data
            )
            
        except Exception as e:
            log.error(f"Error retrieving context: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Context retrieval failed: {str(e)}"
            )
    
    async def _retrieve_patient_context(self, question: str) -> ProcessingResult[List[Dict[str, Any]]]:
        """Retrieve relevant patient records based on question keywords."""
        try:
            # Extract potential keywords for patient record search
            keywords = self._extract_keywords(question)
            
            all_records = []
            
            # Search by gene if mentioned
            gene_keywords = [kw for kw in keywords if kw.isupper() and len(kw) > 2]
            for gene in gene_keywords[:3]:  # Limit to top 3 genes
                records_result = self.sqlite_manager.get_patient_records(gene=gene, limit=10)
                if records_result.success:
                    all_records.extend(records_result.data)
            
            # General text search
            if not all_records:
                for keyword in keywords[:3]:  # Try top 3 keywords
                    search_result = self.sqlite_manager.search_records(keyword, limit=10)
                    if search_result.success:
                        all_records.extend(search_result.data)
                        break
            
            # Remove duplicates
            seen_ids = set()
            unique_records = []
            for record in all_records:
                if record.get('id') not in seen_ids:
                    unique_records.append(record)
                    seen_ids.add(record.get('id'))
            
            return ProcessingResult(
                success=True,
                data=unique_records[:10]  # Limit to 10 records
            )
            
        except Exception as e:
            log.error(f"Error retrieving patient context: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Patient context retrieval failed: {str(e)}"
            )
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from question for search."""
        # Simple keyword extraction
        import re
        
        # Remove common question words
        stop_words = {'what', 'how', 'when', 'where', 'why', 'who', 'which', 'is', 'are', 'was', 'were', 
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', question.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Also extract potential gene names (uppercase words in original question)
        gene_candidates = re.findall(r'\b[A-Z]{2,}\b', question)
        keywords.extend([gene.upper() for gene in gene_candidates])
        
        return list(set(keywords))
    
    def _build_context(self, context_docs: List[Dict[str, Any]], patient_records: List[Dict[str, Any]]) -> str:
        """Build context string for LLM."""
        context_parts = []
        
        # Add document context
        if context_docs:
            context_parts.append("RELEVANT DOCUMENTS:")
            for i, doc in enumerate(context_docs, 1):
                title = doc.get('title', 'Unknown Title')
                doc_id = doc.get('document_id', 'Unknown ID')
                context_parts.append(f"\n{i}. Document: {title} (ID: {doc_id})")
                
                # Add metadata if available
                metadata = doc.get('metadata', {})
                if metadata.get('pmid'):
                    context_parts.append(f"   PMID: {metadata['pmid']}")
        
        # Add patient record context
        if patient_records:
            context_parts.append("\n\nRELEVANT PATIENT RECORDS:")
            for i, record in enumerate(patient_records, 1):
                patient_id = record.get('patient_id', f'Patient {i}')
                context_parts.append(f"\n{i}. {patient_id}:")
                
                # Add key fields
                key_fields = ['sex', 'age_of_onset', 'gene', 'mutations', 'inheritance', 
                            'phenotypes', 'treatments', 'clinical_outcome']
                
                for field in key_fields:
                    value = record.get(field)
                    if value is not None and value != '':
                        context_parts.append(f"   {field}: {value}")
                
                if record.get('pmid'):
                    context_parts.append(f"   Source PMID: {record['pmid']}")
        
        return '\n'.join(context_parts)
    
    async def _generate_answer(self, question: str, context: str) -> ProcessingResult[str]:
        """Generate answer using LLM."""
        try:
            prompt = f"""Based on the following context from biomedical literature and patient records, please answer the question.

CONTEXT:
{context}

QUESTION: {question}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain sufficient information to answer the question, please state this clearly."""
            
            result = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=1000
            )
            
            return result
            
        except Exception as e:
            log.error(f"Error generating answer: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Answer generation failed: {str(e)}"
            )
    
    def _extract_sources(self, context_docs: List[Dict[str, Any]], patient_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information for citations."""
        sources = []
        
        # Document sources
        for doc in context_docs:
            source = {
                "type": "document",
                "id": doc.get('document_id', ''),
                "title": doc.get('title', ''),
                "pmid": doc.get('metadata', {}).get('pmid')
            }
            sources.append(source)
        
        # Patient record sources
        pmids_seen = set()
        for record in patient_records:
            pmid = record.get('pmid')
            if pmid and pmid not in pmids_seen:
                source = {
                    "type": "patient_record",
                    "pmid": pmid,
                    "patient_id": record.get('patient_id', '')
                }
                sources.append(source)
                pmids_seen.add(pmid)
        
        return sources
    
    async def get_summary_statistics(self) -> ProcessingResult[Dict[str, Any]]:
        """Get summary statistics about the RAG system."""
        try:
            # Get vector database stats
            vector_stats_result = self.vector_manager.get_statistics()
            vector_stats = vector_stats_result.data if vector_stats_result.success else {}
            
            # Get SQL database stats
            sql_stats_result = self.sqlite_manager.get_statistics()
            sql_stats = sql_stats_result.data if sql_stats_result.success else {}
            
            summary = {
                "vector_database": vector_stats,
                "sql_database": sql_stats,
                "rag_capabilities": {
                    "document_search": vector_stats.get("total_vectors", 0) > 0,
                    "patient_record_search": sql_stats.get("total_patient_records", 0) > 0,
                    "llm_integration": self.llm_client is not None
                }
            }
            
            return ProcessingResult(
                success=True,
                data=summary
            )
            
        except Exception as e:
            log.error(f"Error getting RAG statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get RAG statistics: {str(e)}"
            )
    
    async def add_documents_to_index(self, documents: List) -> ProcessingResult[int]:
        """Add documents to the vector index."""
        try:
            # Add to vector database
            vector_result = self.vector_manager.add_documents(documents)
            if not vector_result.success:
                return vector_result
            
            # Store documents in SQL database
            for doc in documents:
                doc_result = self.sqlite_manager.store_document(doc)
                if not doc_result.success:
                    log.warning(f"Failed to store document {doc.id} in SQL database: {doc_result.error}")
            
            return ProcessingResult(
                success=True,
                data=len(documents),
                metadata={"added_to_vector_db": vector_result.data}
            )
            
        except Exception as e:
            log.error(f"Error adding documents to RAG system: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to add documents: {str(e)}"
            )

