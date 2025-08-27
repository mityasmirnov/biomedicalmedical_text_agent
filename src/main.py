#!/usr/bin/env python3
"""
Main CLI interface for Biomedical Text Agent.

This module provides a command-line interface for the unified Biomedical Text Agent system.
"""

import argparse
import sys
import logging
import asyncio
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from unified_app import run_unified_server

# Import core components for CLI operations
try:
    from agents.orchestrator.extraction_orchestrator import ExtractionOrchestrator
    from database.sqlite_manager import SQLiteManager
    from database.vector_manager import VectorManager
    from rag.rag_system import RAGSystem
    from core.llm_client.openrouter_client import OpenRouterClient
    from processors.pdf_parser import PDFParser
    CLI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CLI components not available: {e}")
    CLI_AVAILABLE = False

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def extract_command(args):
    """Handle extract command."""
    if not CLI_AVAILABLE:
        print("❌ CLI components not available. Install required dependencies.")
        return
    
    try:
        # Initialize components
        llm_client = OpenRouterClient()
        orchestrator = ExtractionOrchestrator(llm_client=llm_client)
        
        print(f"🔍 Extracting data from: {args.file}")
        
        # Extract data
        result = await orchestrator.extract_from_file(args.file)
        
        if result.success:
            records = result.data
            print(f"✅ Successfully extracted {len(records)} patient records")
            
            # Save to output file if specified
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    if args.format == 'json':
                        json.dump([record.data for record in records], f, indent=2, default=str)
                    else:  # CSV
                        import csv
                        if records and hasattr(records[0], 'data'):
                            fieldnames = list(records[0].data.keys())
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            for record in records:
                                writer.writerow(record.data)
                print(f"💾 Results saved to: {args.output}")
        else:
            print(f"❌ Extraction failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")

async def batch_command(args):
    """Handle batch command."""
    if not CLI_AVAILABLE:
        print("❌ CLI components not available. Install required dependencies.")
        return
    
    try:
        # Initialize components
        llm_client = OpenRouterClient()
        orchestrator = ExtractionOrchestrator(llm_client=llm_client)
        
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"❌ Input directory not found: {input_dir}")
            return
        
        # Find files to process
        if args.pattern:
            files = list(input_dir.glob(args.pattern))
        else:
            files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.txt"))
        
        if not files:
            print(f"❌ No files found in {input_dir}")
            return
        
        print(f"🔍 Processing {len(files)} files from: {input_dir}")
        
        all_records = []
        for i, file_path in enumerate(files):
            print(f"📄 Processing {i+1}/{len(files)}: {file_path.name}")
            try:
                result = await orchestrator.extract_from_file(str(file_path))
                if result.success:
                    all_records.extend(result.data)
                    print(f"   ✅ Extracted {len(result.data)} records")
                else:
                    print(f"   ❌ Failed: {result.error}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Save results
        if all_records and args.output:
            import json
            with open(args.output, 'w') as f:
                if args.format == 'json':
                    json.dump([record.data for record in all_records], f, indent=2, default=str)
                else:  # CSV
                    import csv
                    if all_records and hasattr(all_records[0], 'data'):
                        fieldnames = list(all_records[0].data.keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for record in all_records:
                            writer.writerow(record.data)
            
            print(f"💾 Batch results saved to: {args.output}")
            print(f"📊 Total records extracted: {len(all_records)}")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")

async def db_command(args):
    """Handle database commands."""
    if not CLI_AVAILABLE:
        print("❌ CLI components not available. Install required dependencies.")
        return
    
    try:
        db_manager = SQLiteManager()
        
        if args.subcommand == "stats":
            # Get database statistics
            stats = db_manager.get_statistics()
            if stats.success:
                print("📊 Database Statistics:")
                print(f"   Total records: {stats.data.get('total_records', 0)}")
                print(f"   Total documents: {stats.data.get('total_documents', 0)}")
                print(f"   Database size: {stats.data.get('database_size', 'Unknown')}")
            else:
                print(f"❌ Failed to get statistics: {stats.error}")
        
        elif args.subcommand == "search":
            # Search records
            if not args.query:
                print("❌ Search query required. Use --query 'search term'")
                return
            
            result = db_manager.search_records(args.query, limit=args.limit)
            if result.success:
                records = result.data
                print(f"🔍 Found {len(records)} records matching '{args.query}':")
                for i, record in enumerate(records[:5]):  # Show first 5
                    print(f"   {i+1}. Patient ID: {record.get('patient_id', 'Unknown')}")
                    print(f"      Gene: {record.get('gene', 'Unknown')}")
                    print(f"      Phenotypes: {record.get('phenotypes', 'Unknown')}")
                    print()
                if len(records) > 5:
                    print(f"   ... and {len(records) - 5} more records")
            else:
                print(f"❌ Search failed: {result.error}")
        
        elif args.subcommand == "export":
            # Export records
            result = db_manager.export_to_csv(args.output)
            if result.success:
                print(f"💾 Exported data to: {result.data}")
            else:
                print(f"❌ Export failed: {result.error}")
        
    except Exception as e:
        print(f"❌ Error during database operation: {e}")

async def rag_command(args):
    """Handle RAG commands."""
    if not CLI_AVAILABLE:
        print("❌ CLI components not available. Install required dependencies.")
        return
    
    try:
        # Initialize components
        vector_manager = VectorManager()
        sqlite_manager = SQLiteManager()
        llm_client = OpenRouterClient()
        rag_system = RAGSystem(vector_manager, sqlite_manager, llm_client)
        
        if args.question:
            # Answer specific question
            print(f"🤖 Question: {args.question}")
            result = await rag_system.answer_question(args.question)
            
            if result.success:
                answer_data = result.data
                print(f"💡 Answer: {answer_data.get('answer', 'No answer generated')}")
                if answer_data.get('sources'):
                    print(f"📚 Sources: {len(answer_data['sources'])} documents")
            else:
                print(f"❌ Failed to answer question: {result.error}")
        
        elif args.interactive:
            # Interactive mode
            print("🤖 Interactive RAG Mode (type 'quit' to exit)")
            print("=" * 50)
            
            while True:
                try:
                    question = input("\n❓ Your question: ").strip()
                    if question.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not question:
                        continue
                    
                    print("🤔 Thinking...")
                    result = await rag_system.answer_question(question)
                    
                    if result.success:
                        answer_data = result.data
                        print(f"\n💡 Answer: {answer_data.get('answer', 'No answer generated')}")
                        if answer_data.get('sources'):
                            print(f"📚 Sources: {len(answer_data['sources'])} documents")
                    else:
                        print(f"❌ Failed to answer: {result.error}")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Error during RAG operation: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Biomedical Text Agent - Unified System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start the unified system
  %(prog)s --port 8080       # Start on port 8080
  %(prog)s --host 0.0.0.0    # Bind to all interfaces
  %(prog)s --reload          # Enable auto-reload (development)
  %(prog)s --verbose         # Enable verbose logging
  %(prog)s --check           # Check system configuration
  
  # Data extraction
  %(prog)s extract --file document.pdf --output results.csv
  %(prog)s batch --input-dir papers/ --output batch_results.csv
  
  # Database operations
  %(prog)s db stats                    # View database statistics
  %(prog)s db search --query "SURF1"  # Search records
  %(prog)s db export --output all.csv # Export all data
  
  # RAG system
  %(prog)s rag --question "What genes cause Leigh syndrome?"
  %(prog)s rag --interactive           # Interactive Q&A mode
        """
    )
    
    # Main system arguments
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check system configuration and exit"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract data from a single document")
    extract_parser.add_argument("--file", required=True, help="Path to document file")
    extract_parser.add_argument("--output", help="Output file path")
    extract_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process multiple documents")
    batch_parser.add_argument("--input-dir", required=True, help="Input directory path")
    batch_parser.add_argument("--output", required=True, help="Output file path")
    batch_parser.add_argument("--pattern", help="File pattern (e.g., '*.pdf')")
    batch_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    batch_parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    
    # Database command
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="subcommand", help="Database subcommands")
    
    stats_parser = db_subparsers.add_parser("stats", help="View database statistics")
    
    search_parser = db_subparsers.add_parser("search", help="Search records")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=20, help="Maximum results")
    
    export_parser = db_subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("--output", required=True, help="Output file path")
    
    # RAG command
    rag_parser = subparsers.add_parser("rag", help="RAG system operations")
    rag_group = rag_parser.add_mutually_exclusive_group(required=True)
    rag_group.add_argument("--question", help="Ask a specific question")
    rag_group.add_argument("--interactive", action="store_true", help="Interactive Q&A mode")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle subcommands
    if args.command == "extract":
        asyncio.run(extract_command(args))
        return
    elif args.command == "batch":
        asyncio.run(batch_command(args))
        return
    elif args.command == "db":
        asyncio.run(db_command(args))
        return
    elif args.command == "rag":
        asyncio.run(rag_command(args))
        return
    
    # Check if we're in the right directory
    if not (Path.cwd() / "src").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", Path.cwd())
        print("   Expected to find 'src' directory here")
        sys.exit(1)
    
    # System check
    if args.check:
        print("🔍 Checking system configuration...")
        
        # Check required directories
        required_dirs = ["src", "data", "docs"]
        missing_dirs = [d for d in required_dirs if not Path(d).exists()]
        
        if missing_dirs:
            print(f"❌ Missing directories: {missing_dirs}")
            sys.exit(1)
        else:
            print("✅ Required directories found")
        
        # Check frontend build
        frontend_build = Path("src/ui/frontend/build")
        if frontend_build.exists():
            print("✅ Frontend build found")
        else:
            print("⚠️  Frontend not built (will run API only)")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment active")
        else:
            print("⚠️  Virtual environment not detected")
        
        print("✅ System configuration check passed")
        return
    
    # Print startup information
    print("🚀 Biomedical Text Agent - Unified System")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"Verbose: {'Enabled' if args.verbose else 'Disabled'}")
    print()
    
    print("📋 System Components:")
    print("   • Unified FastAPI Application")
    print("   • Consolidated API Endpoints")
    print("   • Database Management")
    print("   • Metadata Triage System")
    print("   • LangExtract Integration")
    print("   • RAG System")
    print("   • React Frontend (if built)")
    
    print("\n🔧 Starting unified system...")
    print(f"   API Documentation: http://{args.host}:{args.port}/api/docs")
    print(f"   Frontend: http://{args.host}:{args.port}/")
    print(f"   Health Check: http://{args.host}:{args.port}/api/health")
    print(f"   System Status: http://{args.host}:{args.port}/api/v1/system/status")
    
    print("\n" + "=" * 60)
    
    try:
        # Start the unified server
        run_unified_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start system: {e}")
        logging.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

