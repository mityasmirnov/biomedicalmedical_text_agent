"""
Simplified API endpoints for Biomedical Text Agent.

This module defines all the API endpoints without complex imports.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# ============================================================================
# Dashboard Endpoints
# ============================================================================

dashboard_router = APIRouter()

@dashboard_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can be extended for real-time updates
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@dashboard_router.get("/overview")
async def get_dashboard_overview() -> Dict[str, Any]:
    """Return a minimal overview using latest pipeline summary if present."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "files_indexed": 0,
        "latest_summary": {},
        "status": "ok"
    }

@dashboard_router.get("/statistics")
async def get_dashboard_statistics() -> Dict[str, Any]:
    """Return dashboard statistics with mock data for now."""
    return {
        "total_documents": 1250,
        "processed_today": 45,
        "success_rate": 94.2,
        "average_processing_time": 2.3,
        "active_extractions": 2,
        "queue_length": 5,
        "system_health": "healthy",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

@dashboard_router.get("/recent-activities")
async def get_recent_activities() -> Dict[str, Any]:
    """Return recent activities with mock data for now."""
    return {
        "activities": [
            {
                "id": "act-001",
                "type": "document_upload",
                "description": "Uploaded PMID32679198.pdf",
                "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z",
                "status": "completed"
            },
            {
                "id": "act-002",
                "type": "extraction",
                "description": "Extracted data from 3 documents",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                "status": "completed"
            }
        ]
    }

@dashboard_router.get("/alerts")
async def get_dashboard_alerts() -> Dict[str, Any]:
    """Return dashboard alerts with mock data for now."""
    return {
        "alerts": [
            {
                "id": "alert-001",
                "type": "warning",
                "message": "High memory usage detected",
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat() + "Z",
                "severity": "medium"
            }
        ],
        "system_metrics": {
            "cpu_usage": 25.0,
            "memory_usage": 45.0,
            "disk_usage": 60.0,
            "active_connections": 0,
            "api_requests_per_minute": 0,
        }
    }

@dashboard_router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Return system status information."""
    return {
        "status": "healthy",
        "uptime": 3600,  # 1 hour in seconds
        "processing_queue": 5,
        "active_extractions": 2,
        "database_size": 1250,
        "api_usage": {
            "openrouter": 150,
            "huggingface": 75,
            "total_requests": 225
        },
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "service": "biomedical-text-agent",
        "version": "1.0.0",
        "authentication": "disabled",
        "features": {
            "extraction": "enabled",
            "ontology": "enabled",
            "rag": "enabled",
            "database": "enabled",
            "ui": "enabled"
        }
    }

@dashboard_router.get("/queue")
async def get_processing_queue() -> Dict[str, Any]:
    """Return processing queue information."""
    return {
        "jobs": [
            {
                "id": "job-001",
                "type": "metadata_search",
                "status": "running",
                "progress": 75,
                "created_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
                "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat() + "Z",
                "details": {"query": "Leigh syndrome case report", "max_results": 100}
            },
            {
                "id": "job-002",
                "type": "document_extraction",
                "status": "pending",
                "progress": 0,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "details": {"document_id": "PMID32679198", "type": "case_report"}
            }
        ]
    }

@dashboard_router.get("/results")
async def get_recent_results() -> Dict[str, Any]:
    """Return recent extraction results."""
    return {
        "results": [
            {
                "id": "ext-001",
                "document_id": "PMID32679198",
                "title": "Leigh Syndrome: A Case Report",
                "extraction_type": "case_report",
                "confidence_score": 0.87,
                "validation_status": "pending",
                "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z",
                "patient_count": 1
            },
            {
                "id": "ext-002",
                "document_id": "PMID12345678",
                "title": "Mitochondrial Disorder Analysis",
                "extraction_type": "research_paper",
                "confidence_score": 0.92,
                "validation_status": "validated",
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                "patient_count": 15
            }
        ]
    }

# ============================================================================
# Agents Endpoints
# ============================================================================

agents_router = APIRouter()

@agents_router.get("/")
async def get_agents() -> Dict[str, Any]:
    """Get all agents with mock data."""
    return {
        "agents": [
            {
                "id": "demographics",
                "name": "Demographics Agent",
                "description": "Extracts patient demographic information from medical documents",
                "status": "active",
                "performance": 95.2,
                "accuracy": 94.8,
                "speed": 2.3,
                "lastRun": "2 minutes ago",
                "totalRuns": 1250,
                "successRate": 94.2,
                "type": "extraction",
                "capabilities": ["age", "gender", "ethnicity", "consanguinity"],
                "model": "DemographicsAgent",
                "version": "2.1.0"
            },
            {
                "id": "genetics",
                "name": "Genetics Agent",
                "description": "Identifies and normalizes genetic variants and gene information",
                "status": "active",
                "performance": 88.7,
                "accuracy": 87.3,
                "speed": 3.1,
                "lastRun": "5 minutes ago",
                "totalRuns": 890,
                "successRate": 87.3,
                "type": "extraction",
                "capabilities": ["gene_symbol", "mutation", "variant", "allele"],
                "model": "GeneticsAgent",
                "version": "2.0.0"
            }
        ]
    }

@agents_router.get("/{agent_id}")
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get specific agent details."""
    agents = await get_agents()
    for agent in agents.get("agents", []):
        if agent["id"] == agent_id:
            return agent
    
    raise HTTPException(status_code=404, detail="Agent not found")

@agents_router.post("/{agent_id}/start")
async def start_agent(agent_id: str) -> Dict[str, Any]:
    """Start a specific agent."""
    return {"message": f"Agent {agent_id} started", "status": "success"}

@agents_router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str) -> Dict[str, Any]:
    """Stop a specific agent."""
    return {"message": f"Agent {agent_id} stopped", "status": "success"}

# ============================================================================
# Documents Endpoints
# ============================================================================

documents_router = APIRouter()

@documents_router.get("/")
async def get_documents() -> Dict[str, Any]:
    """Get all documents with mock data."""
    return {
        "documents": [
            {
                "id": "doc-001",
                "title": "Leigh Syndrome Case Report",
                "type": "case_report",
                "source": "PubMed",
                "pmid": "PMID32679198",
                "doi": "10.1000/example.2024.001",
                "authors": ["Smith, J.", "Johnson, A."],
                "abstract": "A case report of Leigh syndrome in a 3-year-old patient...",
                "upload_date": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "status": "extracted",
                "file_size": 2048576,
                "extraction_results": {
                    "patient_count": 1,
                    "confidence_score": 0.87
                }
            },
            {
                "id": "doc-002",
                "title": "Mitochondrial Disorder Analysis",
                "type": "research_paper",
                "source": "PubMed",
                "pmid": "PMID12345678",
                "doi": "10.1000/example.2024.002",
                "authors": ["Brown, M.", "Davis, K."],
                "abstract": "Analysis of mitochondrial disorders in pediatric patients...",
                "upload_date": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
                "status": "validated",
                "file_size": 1536000,
                "extraction_results": {
                    "patient_count": 15,
                    "confidence_score": 0.92
                }
            }
        ]
    }

@documents_router.get("/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """Get specific document details."""
    documents = await get_documents()
    for doc in documents.get("documents", []):
        if doc["id"] == document_id:
            return doc
    
    raise HTTPException(status_code=404, detail="Document not found")

@documents_router.get("/{document_id}/full-text")
async def get_document_fulltext(document_id: str) -> Dict[str, Any]:
    """Get document full text."""
    return {
        "document_id": document_id,
        "full_text": "This is the full text content of the document...",
        "extraction_results": {
            "patient_count": 1,
            "confidence_score": 0.87
        }
    }

# ============================================================================
# Metadata Endpoints
# ============================================================================

metadata_router = APIRouter()

@metadata_router.get("/")
async def get_metadata() -> Dict[str, Any]:
    """Get metadata overview."""
    return {
        "total_records": 1250,
        "collections": [
            {
                "name": "pubmed",
                "count": 850,
                "last_updated": (datetime.utcnow() - timedelta(hours=6)).isoformat() + "Z"
            },
            {
                "name": "europepmc",
                "count": 400,
                "last_updated": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"
            }
        ]
    }

@metadata_router.get("/search")
async def search_metadata(query: str = Query(...)) -> Dict[str, Any]:
    """Search metadata."""
    return {
        "query": query,
        "results": [
            {
                "id": "meta-001",
                "title": f"Search result for: {query}",
                "abstract": f"This is an abstract related to {query}",
                "pmid": "PMID12345678",
                "relevance_score": 0.95
            }
        ],
        "total_results": 1
    }

# ============================================================================
# Database Endpoints
# ============================================================================

database_router = APIRouter()

@database_router.get("/status")
async def get_database_status() -> Dict[str, Any]:
    """Get database status."""
    return {
        "status": "healthy",
        "tables": [
            {
                "name": "metadata",
                "record_count": 1250,
                "size_mb": 45.2
            },
            {
                "name": "documents",
                "record_count": 450,
                "size_mb": 156.8
            },
            {
                "name": "extractions",
                "record_count": 890,
                "size_mb": 23.4
            }
        ]
    }

@database_router.get("/patients")
async def get_patients(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Get patient records from database."""
    return {
        "patients": [
            {
                "id": "patient-001",
                "age": 3,
                "gender": "male",
                "diagnosis": "Leigh syndrome",
                "gene": "MT-ATP6"
            }
        ],
        "total": 1
    }

# ============================================================================
# Configuration Endpoints
# ============================================================================

config_router = APIRouter()

@config_router.get("/providers")
async def get_providers() -> Dict[str, Any]:
    """Get available API providers."""
    return {
        "providers": [
            {
                "name": "openrouter",
                "display_name": "OpenRouter",
                "description": "Access to multiple LLM models including GPT, Claude, and others",
                "enabled": True,
                "api_key_configured": True,
                "base_url": "https://openrouter.ai/api/v1",
                "rate_limit": 100
            },
            {
                "name": "huggingface",
                "display_name": "Hugging Face",
                "description": "Open source model hosting and inference API",
                "enabled": True,
                "api_key_configured": False,
                "base_url": "https://api-inference.huggingface.co",
                "rate_limit": 50
            },
            {
                "name": "ollama",
                "display_name": "Ollama",
                "description": "Local model deployment and inference",
                "enabled": False,
                "api_key_configured": False,
                "base_url": "http://localhost:11434",
                "rate_limit": 1000
            }
        ]
    }

@config_router.put("/providers/{provider}")
async def update_provider(provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update provider configuration."""
    return {
        "provider": provider,
        "updated": True,
        "changes": data
    }

@config_router.get("/models")
async def get_models() -> Dict[str, Any]:
    """Get available models."""
    return {
        "models": [
            {
                "id": "google/gemma-2-27b-it:free",
                "name": "Gemma 2 27B",
                "provider": "openrouter",
                "type": "free",
                "available": True,
                "max_tokens": 8192,
                "context_length": 32768
            },
            {
                "id": "microsoft/phi-3-mini-128k-instruct:free",
                "name": "Phi-3 Mini",
                "provider": "openrouter",
                "type": "free",
                "available": True,
                "max_tokens": 4096,
                "context_length": 128000
            }
        ]
    }

@config_router.put("/providers/{provider}/key")
async def update_api_key(provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update API key for a provider."""
    return {
        "provider": provider,
        "api_key_updated": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@config_router.get("/usage")
async def get_usage() -> Dict[str, Any]:
    """Get API usage statistics."""
    return {
        "openrouter": {
            "total_requests": 150,
            "total_cost": 0.25,
            "limit": 1000,
            "reset_date": "2024-02-01"
        },
        "huggingface": {
            "total_requests": 75,
            "total_cost": 0.00,
            "limit": 500,
            "reset_date": "2024-02-01"
        }
    }

# ============================================================================
# Ontology Endpoints
# ============================================================================

ontologies_router = APIRouter()

@ontologies_router.get("/")
async def get_ontologies() -> Dict[str, Any]:
    """Get all available ontologies."""
    return {
        "ontologies": [
            {
                "id": "hpo",
                "name": "Human Phenotype Ontology",
                "description": "Standard vocabulary of phenotypic abnormalities encountered in human disease",
                "version": "2024-01-15",
                "source": "https://hpo.jax.org/",
                "term_count": 15447,
                "last_updated": "2024-01-15"
            },
            {
                "id": "genes",
                "name": "Gene Ontology",
                "description": "Standard representation of gene and gene product attributes",
                "version": "2024-01-20",
                "source": "http://geneontology.org/",
                "term_count": 45678,
                "last_updated": "2024-01-20"
            }
        ]
    }

@ontologies_router.post("/search")
async def search_ontologies(query: str) -> Dict[str, Any]:
    """Search ontology terms."""
    return {
        "results": [
            {
                "term": {
                    "id": "HP:0000002",
                    "name": "Abnormality of body height",
                    "description": "Abnormal body height"
                },
                "ontology": "hpo",
                "relevance": 0.95,
                "matched_fields": ["name", "description"]
            }
        ]
    }

# ============================================================================
# Prompt Management Endpoints
# ============================================================================

prompts_router = APIRouter()

@prompts_router.get("/")
async def get_prompts() -> Dict[str, Any]:
    """Get all prompts."""
    return {
        "prompts": [
            {
                "id": "system-main",
                "name": "Main System Prompt",
                "description": "Primary system prompt for the biomedical text agent",
                "content": "You are a biomedical text analysis agent specialized in extracting structured information from medical literature.",
                "type": "system",
                "version": "1.0.0",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z"
            }
        ]
    }

@prompts_router.post("/")
async def create_prompt(prompt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new prompt."""
    return {
        "prompt": {
            "id": f"prompt-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            **prompt_data,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@prompts_router.get("/langextract-instructions")
async def get_langextract_instructions() -> Dict[str, Any]:
    """Get LangExtract instructions."""
    return {
        "instructions": [
            {
                "id": "patient-extraction",
                "name": "Patient Information Extraction",
                "description": "Extract patient demographics and clinical information",
                "schema": '{"patient": {"age": "number", "gender": "string"}}',
                "examples": ["Patient is a 25-year-old male"],
                "instructions": "Identify patient age, gender, symptoms, and diagnosis from the text.",
                "is_default": True
            }
        ]
    }

@prompts_router.post("/{id}/test")
async def test_prompt(id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Test a prompt."""
    return {
        "prompt_id": id,
        "test_text": data.get("test_text", ""),
        "result": "This is a mock test result for the prompt."
    }

# ============================================================================
# Analytics Endpoints
# ============================================================================

analytics_router = APIRouter()

@analytics_router.get("/visualizations")
async def get_visualizations(time_range: str = "7d") -> Dict[str, Any]:
    """Get analytics data for visualizations."""
    return {
        "extraction_stats": {
            "total_extractions": 1250,
            "successful_extractions": 1180,
            "failed_extractions": 70,
            "average_confidence": 0.87,
            "total_documents": 450
        },
        "agent_performance": [
            {
                "agent_id": "extraction-agent",
                "agent_name": "Extraction Agent",
                "total_requests": 850,
                "success_rate": 0.94,
                "average_response_time": 2.3,
                "error_rate": 0.06
            }
        ],
        "extraction_timeline": [
            {"date": "2024-01-01", "extractions": 45, "documents": 12, "confidence": 0.85},
            {"date": "2024-01-02", "extractions": 52, "documents": 15, "confidence": 0.87}
        ],
        "concept_distribution": [
            {"concept": "Patient Demographics", "count": 450, "percentage": 36},
            {"concept": "Clinical Symptoms", "count": 380, "percentage": 30.4}
        ],
        "validation_stats": {
            "total_validated": 850,
            "approved": 780,
            "rejected": 45,
            "pending": 25,
            "average_validation_time": 3.2
        }
    }

# ============================================================================
# Validation Endpoints
# ============================================================================

validation_router = APIRouter()

@validation_router.get("/{extraction_id}")
async def get_extraction_data(extraction_id: str) -> Dict[str, Any]:
    """Get extraction data for validation."""
    return {
        "extraction_id": extraction_id,
        "original_text": "Patient is a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G mutation...",
        "highlighted_text": "Patient is a <span class='extraction-highlight' data-field='age' data-confidence='0.95'>3-year-old</span> <span class='extraction-highlight' data-field='sex' data-confidence='0.98'>male</span> with <span class='extraction-highlight' data-field='diagnosis' data-confidence='0.92'>Leigh syndrome</span> due to <span class='extraction-highlight' data-field='gene_symbol' data-confidence='0.89'>MT-ATP6</span> <span class='extraction-highlight' data-field='mutation_description' data-confidence='0.87'>c.8993T>G</span> mutation...",
        "extractions": {
            "age_of_onset_years": 3,
            "sex": "male",
            "diagnosis": "Leigh syndrome",
            "gene_symbol": "MT-ATP6",
            "mutation_description": "c.8993T>G"
        },
        "spans": [
            {
                "start": 8,
                "end": 17,
                "text": "3-year-old",
                "extraction_type": "demographics",
                "field_name": "age_of_onset_years",
                "confidence": 0.95
            },
            {
                "start": 18,
                "end": 22,
                "text": "male",
                "extraction_type": "demographics",
                "field_name": "sex",
                "confidence": 0.98
            }
        ],
        "confidence_scores": {
            "age_of_onset_years": 0.95,
            "sex": 0.98,
            "diagnosis": 0.92,
            "gene_symbol": 0.89,
            "mutation_description": 0.87
        }
    }

@validation_router.post("/{extraction_id}/submit")
async def submit_validation(extraction_id: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit validation results."""
    return {
        "extraction_id": extraction_id,
        "validation_status": validation_data.get("status", "validated"),
        "validator_notes": validation_data.get("notes", ""),
        "corrections": validation_data.get("corrections", {}),
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    }

@validation_router.get("/queue")
async def get_validation_queue(status: Optional[str] = None) -> Dict[str, Any]:
    """Get validation queue."""
    queue_items = [
        {
            "extraction_id": "ext-001",
            "document_title": "Leigh Syndrome Case Report",
            "extraction_type": "case_report",
            "confidence_score": 0.87,
            "status": "pending",
            "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z"
        },
        {
            "extraction_id": "ext-002",
            "document_title": "Mitochondrial Disorder Analysis",
            "extraction_type": "research_paper",
            "confidence_score": 0.92,
            "status": "pending",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
        }
    ]
    
    if status:
        queue_items = [item for item in queue_items if item["status"] == status]
    
    return {"queue": queue_items}

# ============================================================================
# Authentication Endpoints
# ============================================================================

auth_router = APIRouter()

@auth_router.post("/login")
async def login(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Mock login endpoint."""
    return {
        "access_token": "mock_token_12345",
        "token_type": "bearer",
        "user": {
            "id": "user_001",
            "username": credentials.get("username", "user"),
            "email": "user@example.com",
            "role": "admin"
        }
    }

@auth_router.post("/logout")
async def logout() -> Dict[str, Any]:
    """Mock logout endpoint."""
    return {"message": "Logged out successfully"}

@auth_router.post("/refresh")
async def refresh_token() -> Dict[str, Any]:
    """Mock token refresh endpoint."""
    return {
        "access_token": "new_mock_token_67890",
        "token_type": "bearer"
    }

@auth_router.get("/profile")
async def get_profile() -> Dict[str, Any]:
    """Mock user profile endpoint."""
    return {
        "id": "user_001",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "created_at": "2024-01-01T00:00:00Z"
    }

# ============================================================================
# Health and System Status Endpoints
# ============================================================================

health_router = APIRouter()

@health_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "biomedical-text-agent"
    }

@health_router.get("/system/status")
async def system_status() -> Dict[str, Any]:
    """System status endpoint."""
    return {
        "status": "operational",
        "service": "biomedical-text-agent",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy",
            "vector_store": "healthy",
            "llm_client": "healthy",
            "metadata_triage": "healthy",
            "langextract": "healthy"
        }
    }

# ============================================================================
# Placeholder routers for compatibility
# ============================================================================

metadata_triage_router = APIRouter()
extraction_router = APIRouter()
rag_router = APIRouter()
user_router = APIRouter()

# Add placeholder endpoints to avoid 404s
@metadata_triage_router.get("/")
async def metadata_triage_overview():
    return {"message": "Metadata triage system"}

@extraction_router.get("/")
async def extraction_overview():
    return {"message": "Extraction system"}

@rag_router.get("/")
async def rag_overview():
    return {"message": "RAG system"}

@user_router.get("/")
async def user_overview():
    return {"message": "User management system"}
