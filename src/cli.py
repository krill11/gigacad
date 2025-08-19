"""
Command-line interface for GigaCAD AI CAD Agent
"""

import asyncio
import sys
import logging
import os
import warnings
from .config import config

def print_rainbow_banner():
    """Print a cool rainbow banner with GigaCAD in big block letters"""
    # ANSI color codes for rainbow effect
    colors = [
        '\033[91m',  # Red
        '\033[93m',  # Yellow
        '\033[92m',  # Green
        '\033[96m',  # Cyan
        '\033[94m',  # Blue
        '\033[95m',  # Magenta
    ]
    reset = '\033[0m'
    bold = '\033[1m'
    
    # Big block letters for GIGACAD
    banner_lines = [
        "  ██████╗ ██╗ ██████╗  █████╗  ██████╗ █████╗ ██████╗ ",
        " ██╔════╝ ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗██╔══██╗",
        " ██║  ███╗██║██║  ███╗███████║██║     ███████║██║  ██║",
        " ██║   ██║██║██║   ██║██╔══██║██║     ██╔══██║██║  ██║",
        " ╚██████╔╝██║╚██████╔╝██║  ██║╚██████╗██║  ██║██████╔╝",
        "  ╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ "
    ]
    
    print()
    # Print each line with rainbow colors
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        print(f"{bold}{color}{line}{reset}")
    
    # Subtitle with gradient effect
    subtitle = "🤖 AI-Powered CAD Generation"
    print(f"\n{bold}{colors[2]}                  {subtitle}{reset}")
    
    # Cool separator
    separator = "═" * 58
    print(f"{colors[4]}{separator}{reset}")
    print()

# Suppress all logging before any imports if DEBUG is False
if not config.DEBUG:
    warnings.filterwarnings("ignore")
    logging.getLogger().setLevel(logging.ERROR)
    for logger_name in ['onpy', 'requests', 'urllib3', 'urllib3.connectionpool']:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
    os.environ['ONPY_DEBUG'] = 'false'
    os.environ['ONPY_LOG_LEVEL'] = 'ERROR'

from .ai_agent import CADAgent

async def main():
    """Main CLI function"""
    
    # Clear the terminal for a clean start
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Always show the cool rainbow banner
    print_rainbow_banner()
    
    if config.DEBUG:
        print("🎯 Now with FULL CAD capabilities!")
        print("   • Sketches, Extrusions, Revolves, Sweeps, Lofts")
        print("   • Patterns, Fillets, Holes, Advanced Features")
        print("   • Assembly creation and management")
        print("=" * 58)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed!")
        print("Please check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    
    if config.DEBUG:
        print("✅ Configuration validated")
    
    # Initialize agent
    try:
        agent = CADAgent(llm_type="groq")
        if config.DEBUG:
            print("✅ AI Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {str(e)}")
        sys.exit(1)
    
    if config.DEBUG:
        print("\nAvailable commands:")
        print("  create <description> - Create a part from description")
        print("  list-docs            - List available documents")
        print("  status               - Show current session status")
        print("  reset                - Reset current session")
        print("  help                 - Show this help")
        print("  quit                 - Exit the program")
        print("\n" + "=" * 50)
    
    while True:
        try:
            command = input("\n🤖 CAD Agent > ").strip()
            
            if not command:
                continue
                
            if command.lower() == "quit" or command.lower() == "exit":
                print("👋 Goodbye!")
                break
                
            elif command.lower() == "help":
                print("\nAvailable commands:")
                print("  create <description> - Create a part from description")
                print("  list-docs            - List available documents")
                print("  status               - Show current session status")
                print("  reset                - Reset current session")
                print("  help                 - Show this help")
                print("  quit                 - Exit the program")
                print("\nExamples:")
                print("  create Create a gear with 20 teeth, 2mm module, 10mm thickness")
                print("  create Design a phone stand with adjustable angle")
                print("  create Make a mechanical pencil with retractable tip")
                
            elif command.lower() == "status":
                status = await agent.get_status()
                print("\n📊 Current Session Status:")
                print(f"  Document ID: {status['document_id'] or 'None'}")
                print(f"  Workspace ID: {status['workspace_id'] or 'None'}")
                print(f"  Part Studio ID: {status['part_studio_id'] or 'None'}")
                print(f"  Assembly ID: {status['assembly_id'] or 'None'}")
                print(f"  Available Tools: {len(status['tools_available'])} tools")
                print(f"  Tool Categories:")
                for tool in status['tools_available']:
                    print(f"    • {tool}")
                
            elif command.lower() == "list-docs":
                try:
                    documents = await agent.list_documents()
                    if documents:
                        print("\n📁 Available Documents:")
                        for doc in documents:
                            print(f"  • {doc['name']} (ID: {doc['id']})")
                            if doc.get('description'):
                                print(f"    Description: {doc['description']}")
                    else:
                        print("\n📁 No documents found")
                except Exception as e:
                    print(f"❌ Error listing documents: {str(e)}")
                
            elif command.lower() == "reset":
                await agent.reset_session()
                print("🔄 Session reset successfully")
                
            elif command.lower().startswith("create "):
                description = command[7:].strip()
                if not description:
                    print("❌ Please provide a description for the part")
                    continue
                    
                print(f"\n🎯 Creating part: {description}")
                print("⏳ Processing with AI CAD Agent...")
                print("   This may take a moment as the AI plans and executes the design...")
                
                result = await agent.create_part_from_description(description)
                print(f"\n✅ Result: {result}")
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 