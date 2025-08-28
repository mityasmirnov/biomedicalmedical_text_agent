"""Test script for implementation package."""
import sys
from pathlib import Path

def test_files():
    """Test that all required files exist."""
    required_files = [
        "requirements.txt",
        ".env.example", 
        ".gitignore",
        "setup.py",
        "src/metadata_triage/pubmed_client.py",
        "src/database/enhanced_sqlite_manager.py",
        "src/ui/frontend/package.json"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present")
        return True

if __name__ == "__main__":
    print("🧪 Testing Implementation Package")
    print("=" * 40)
    
    if test_files():
        print("🎉 Package ready for deployment!")
        sys.exit(0)
    else:
        print("❌ Package incomplete")
        sys.exit(1)
