#!/usr/bin/env python3
"""
Simple test runner for SocialAI.
"""

import sys
import subprocess


def run_tests():
    """Run the test suite."""
    print("Running SocialAI tests...")
    
    try:
        # Run pytest
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            capture_output=False,
            cwd="/home/engine/project/pc-control"
        )
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        print("Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest>=7.0.0", "pytest-asyncio>=0.21.0"
        ])
        return
    
    run_tests()


if __name__ == "__main__":
    main()
