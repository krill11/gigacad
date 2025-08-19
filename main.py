#!/usr/bin/env python3
"""
CoralMaker - AI-Powered CAD Generation
Main entry point for the application
"""

import sys
import asyncio
from src.cli import main as cli_main
from src.api import app
import uvicorn

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "cli":
            # Run CLI interface
            asyncio.run(cli_main())
        elif command == "web":
            # Run web API
            uvicorn.run(app, host="0.0.0.0", port=8000)
        elif command == "help":
            print("CoralMaker - AI-Powered CAD Generation")
            print("\nUsage:")
            print("  python main.py cli     - Run command-line interface")
            print("  python main.py web     - Run web API server")
            print("  python main.py help    - Show this help")
            print("\nExamples:")
            print("  python main.py cli")
            print("  python main.py web")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for usage information")
            sys.exit(1)
    else:
        # Default to CLI
        print("Starting CoralMaker CLI...")
        asyncio.run(cli_main())

if __name__ == "__main__":
    main() 