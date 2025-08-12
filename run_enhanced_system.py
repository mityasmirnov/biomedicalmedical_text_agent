#!/usr/bin/env python3
"""
Enhanced Biomedical Data Extraction Engine - Main Runner
"""

import sys
import os
import argparse
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
        print(f"❌ Status check failed: {e}")
        sys.exit(1)

def run_extraction(input_file, output_file):
    """Run data extraction."""
    try:
        from agents.orchestrator.enhanced_orchestrator_simple_fixed import SimpleEnhancedOrchestrator
        
        orchestrator = SimpleEnhancedOrchestrator()
        
        print(f"🚀 Starting extraction from {input_file}...")
        result = orchestrator.extract_from_file(input_file, output_file)
        
        if result.success:
            print(f"✅ Extraction completed successfully!")
            print(f"📁 Results saved to: {output_file}")
        else:
            print(f"❌ Extraction failed: {result.error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)

def run_demo():
    """Run demo extraction."""
    try:
        from agents.orchestrator.enhanced_orchestrator_simple_fixed import SimpleEnhancedOrchestrator
        
        orchestrator = SimpleEnhancedOrchestrator()
        
        print("🎭 Running demo extraction...")
        result = orchestrator.run_demo()
        
        if result.success:
            print("✅ Demo completed successfully!")
        else:
            print(f"❌ Demo failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def run_usage():
    """Check API usage statistics and limits."""
    try:
        from core.llm_client.openrouter_client import OpenRouterClient
        from core.api_usage_tracker import APIUsageTracker
        from core.config import get_config
        
        config = get_config()
        
        print("📊 API Usage Statistics")
        print("=" * 50)
        
        # Initialize usage tracker
        usage_tracker = APIUsageTracker(config.llm.usage_database_path)
        
        # Get overall summary
        summary = usage_tracker.get_usage_summary()
        if summary:
            print(f"📈 Total Requests: {summary.get('total_requests', 0)}")
            print(f"🕐 Recent Requests (24h): {summary.get('recent_requests_24h', 0)}")
            print(f"💾 Database Size: {summary.get('database_size_mb', 0):.2f} MB")
            print()
        
        # Get OpenRouter specific stats
        openrouter_stats = usage_tracker.get_usage_stats("openrouter", 30)
        if openrouter_stats:
            print("🔗 OpenRouter API (Last 30 Days)")
            print("-" * 30)
            print(f"✅ Successful Requests: {openrouter_stats.successful_requests}")
            print(f"❌ Failed Requests: {openrouter_stats.failed_requests}")
            print(f"🔢 Total Tokens: {openrouter_stats.total_tokens:,}")
            print(f"💰 Estimated Cost: ${openrouter_stats.total_cost:.4f}")
            print()
        
        # Check remaining limits
        daily_remaining = config.llm.max_requests_per_day
        monthly_remaining = config.llm.max_requests_per_month
        
        if openrouter_stats:
            daily_used = openrouter_stats.total_requests
            daily_remaining = max(0, config.llm.max_requests_per_day - daily_used)
        
        print("🎯 Usage Limits")
        print("-" * 30)
        print(f"📅 Daily Limit: {config.llm.max_requests_per_day} requests")
        print(f"📅 Daily Remaining: {daily_remaining} requests")
        print(f"📆 Monthly Limit: {config.llm.max_requests_per_month} requests")
        print(f"📆 Monthly Remaining: {monthly_remaining} requests")
        print()
        
        # Get daily usage breakdown
        daily_usage = usage_tracker.get_daily_usage("openrouter")
        if daily_usage:
            print("⏰ Today's Usage by Hour")
            print("-" * 30)
            for hour in sorted(daily_usage.keys()):
                usage = daily_usage[hour]
                print(f"{hour}:00 - {usage['requests']} requests, {usage['tokens']} tokens")
        
    except Exception as e:
        print(f"❌ Usage check failed: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Biomedical Data Extraction Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_enhanced_system.py status                    # Check system status
  python run_enhanced_system.py extract input.pdf output.json  # Extract data
  python run_enhanced_system.py demo                      # Run demo extraction
  python run_enhanced_system.py usage                     # Check API usage
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Check system status')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data from file')
    extract_parser.add_argument('input', help='Input file path')
    extract_parser.add_argument('output', help='Output file path')
    
    # Demo command
    subparsers.add_parser('demo', help='Run demo extraction')
    
    # Usage command
    subparsers.add_parser('usage', help='Check API usage statistics and limits')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'status':
        run_status()
    elif args.command == 'extract':
        run_extraction(args.input, args.output)
    elif args.command == 'demo':
        run_demo()
    elif args.command == 'usage':
        run_usage()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
