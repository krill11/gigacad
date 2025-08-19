"""
Command-line interface for CoralMaker AI CAD Agent
"""

import asyncio
import sys
from .ai_agent import CADAgent
from .config import config

async def main():
    """Main CLI function"""
    
    print("🤖 CoralMaker - AI CAD Agent")
    print("=" * 50)
    print("🎯 Now with FULL CAD capabilities!")
    print("   • Sketches, Extrusions, Revolves, Sweeps, Lofts")
    print("   • Patterns, Fillets, Holes, Advanced Features")
    print("   • Assembly creation and management")
    print("=" * 50)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed!")
        print("Please check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    
    print("✅ Configuration validated")
    
    # Initialize agent
    try:
        agent = CADAgent(llm_type="groq")
        print("✅ AI Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {str(e)}")
        sys.exit(1)
    
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