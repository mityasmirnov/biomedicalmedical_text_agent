#!/usr/bin/env python3
"""
Enhanced Biomedical Data Extraction Engine - Main Runner
"""

import sys
import os
import argparse
from pathlib import Path
import asyncio

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

def run_providers():
    """Check status of all LLM providers and test their availability."""
    try:
        from core.llm_client.smart_llm_manager import SmartLLMManager
        
        print("🔌 LLM Provider Status")
        print("=" * 50)
        
        # Initialize smart LLM manager
        manager = SmartLLMManager()
        
        # Get provider status
        status = manager.get_provider_status()
        available_providers = manager.get_available_providers()
        current_provider = manager.get_current_provider()
        
        print(f"🎯 Current Provider: {current_provider}")
        print(f"📡 Available Providers: {', '.join(available_providers)}")
        print()
        
        # Display status for each provider
        for provider, info in status.items():
            status_icon = "✅" if info["healthy"] else "❌"
            current_icon = "🎯" if info["current"] else "  "
            print(f"{current_icon} {provider.upper()}")
            print(f"   {status_icon} Available: {info['available']}")
            print(f"   {status_icon} Healthy: {info['healthy']}")
            print(f"   {status_icon} Current: {info['current']}")
            print()
        
        # Test all providers
        print("🧪 Testing All Providers...")
        print("-" * 30)
        
        test_results = asyncio.run(manager.test_all_providers())
        
        for provider, result in test_results.items():
            result_icon = "✅" if result else "❌"
            print(f"{result_icon} {provider}: {'Working' if result else 'Failed'}")
        
        print()
        
        # Show usage information if available
        if current_provider == "openrouter":
            try:
                from core.api_usage_tracker import APIUsageTracker
                from core.config import get_config
                
                config = get_config()
                usage_tracker = APIUsageTracker(config.llm.usage_database_path)
                
                # Get remaining requests
                remaining = manager.primary_client.get_remaining_requests() if hasattr(manager, 'primary_client') and manager.primary_client else {}
                
                if remaining:
                    print("📊 OpenRouter Usage")
                    print("-" * 20)
                    print(f"📅 Daily Remaining: {remaining.get('daily', 'Unknown')}")
                    print(f"📆 Monthly Remaining: {remaining.get('monthly', 'Unknown')}")
                
            except Exception as e:
                print(f"⚠️  Could not fetch usage info: {e}")
        
        print("🎉 Provider status check completed!")
        
    except Exception as e:
        print(f"❌ Provider status check failed: {e}")
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
  python run_enhanced_system.py providers                 # Check LLM provider status
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

    # Providers command
    subparsers.add_parser('providers', help='Check status of all LLM providers and test their availability')
    
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
    elif args.command == 'providers':
        run_providers()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
