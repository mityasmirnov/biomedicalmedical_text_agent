#!/usr/bin/env python3
"""
Wrapper script to run the enhanced biomedical data extraction system.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_status():
    """Run system status check."""
    try:
        from agents.orchestrator.enhanced_orchestrator_simple_fixed import SimpleEnhancedOrchestrator
        
        orchestrator = SimpleEnhancedOrchestrator()
        orchestrator.display_system_status()
        
    except Exception as e:
        print(f"❌ Failed to run status: {e}")
        import traceback
        traceback.print_exc()

def run_extraction(input_file, output_file):
    """Run data extraction."""
    try:
        from agents.orchestrator.enhanced_orchestrator_simple_fixed import SimpleEnhancedOrchestrator
        
        orchestrator = SimpleEnhancedOrchestrator()
        
        print(f"🚀 Starting extraction from {input_file}...")
        result = asyncio.run(orchestrator.extract_from_file(input_file, output_file))
        
        if result.success:
            print(f"✅ Extraction completed successfully!")
            print(f"📊 Extracted {len(result.data)} patient records")
            if output_file:
                print(f"💾 Results saved to {output_file}")
        else:
            print(f"❌ Extraction failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Failed to run extraction: {e}")
        import traceback
        traceback.print_exc()

def run_demo():
    """Run a demonstration of the enhanced system."""
    try:
        print("🎯 Enhanced Biomedical Data Extraction System - Demo")
        print("=" * 60)
        
        # Test file
        test_file = "data/input/PMID32679198.pdf"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return
        
        print(f"📄 Using test file: {test_file}")
        
        # Run extraction
        output_file = "data/output/enhanced_demo_results.json"
        run_extraction(test_file, output_file)
        
        print("\n🎉 Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_enhanced_system.py status")
        print("  python run_enhanced_system.py extract <input_file> [output_file]")
        print("  python run_enhanced_system.py demo")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        run_status()
    elif command == "extract":
        if len(sys.argv) < 3:
            print("Error: Input file required for extract command")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            return
        
        run_extraction(input_file, output_file)
    elif command == "demo":
        run_demo()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: status, extract, demo")

if __name__ == "__main__":
    main()
