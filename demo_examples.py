#!/usr/bin/env python3
"""
Demo examples for CoralMaker AI CAD Agent
Shows the enhanced capabilities for creating complex parts
"""

import asyncio
from src.ai_agent import CADAgent
from src.config import config

async def demo_complex_parts():
    """Demo creating complex parts with the enhanced AI agent"""
    
    print("🚀 CoralMaker Enhanced CAD Demo")
    print("=" * 60)
    print("🎯 Now with FULL CAD capabilities!")
    print("   • Sketches, Extrusions, Revolves, Sweeps, Lofts")
    print("   • Patterns, Fillets, Holes, Advanced Features")
    print("   • Assembly creation and management")
    print("=" * 60)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed!")
        print("Please check your .env file and ensure all required API keys are set.")
        return
    
    print("✅ Configuration validated")
    
    # Initialize agent
    try:
        agent = CADAgent(llm_type="groq")
        print("✅ AI Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {str(e)}")
        return
    
    # Demo examples
    examples = [
        {
            "name": "Gear with Teeth",
            "description": "Create a spur gear with 20 teeth, 2mm module, and 10mm thickness. Include proper tooth profile and center hole.",
            "expected_operations": ["create_document", "create_part_studio", "create_circle_sketch", "extrude_sketch", "create_hole"]
        },
        {
            "name": "Phone Stand",
            "description": "Design a phone stand with adjustable angle mechanism, non-slip base, and ergonomic grip. Include hinge mechanism.",
            "expected_operations": ["create_document", "create_part_studio", "create_sketch", "extrude_sketch", "create_assembly"]
        },
        {
            "name": "Mechanical Pencil",
            "description": "Make a mechanical pencil with retractable tip, grip pattern, and internal mechanism housing. Include threaded components.",
            "expected_operations": ["create_document", "create_part_studio", "create_cylinder", "create_sketch", "extrude_sketch", "linear_pattern"]
        },
        {
            "name": "Bottle Opener",
            "description": "Create a bottle opener with ergonomic handle, proper leverage design, and magnetic bottle cap holder.",
            "expected_operations": ["create_document", "create_part_studio", "create_sketch", "extrude_sketch", "create_hole", "fillet_edges"]
        },
        {
            "name": "Custom Bracket",
            "description": "Design a mounting bracket with multiple mounting holes, reinforcement ribs, and cable management features.",
            "expected_operations": ["create_document", "create_part_studio", "create_rectangle_sketch", "extrude_sketch", "create_hole", "linear_pattern", "circular_pattern"]
        }
    ]
    
    print(f"\n📋 Demo Examples ({len(examples)} complex parts):")
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   Description: {example['description']}")
        print(f"   Expected Operations: {', '.join(example['expected_operations'])}")
    
    print("\n" + "=" * 60)
    print("💡 These examples demonstrate the AI agent's ability to:")
    print("   • Understand complex mechanical requirements")
    print("   • Plan multi-step CAD operations")
    print("   • Create professional-quality designs")
    print("   • Handle assemblies and complex geometry")
    print("   • Apply engineering best practices")
    
    print("\n🎯 To try these examples:")
    print("   1. Run: python main.py cli")
    print("   2. Use: create <description>")
    print("   3. Or run: python main.py web")
    print("   4. Open the web interface")
    
    print("\n🔧 The AI agent will automatically:")
    print("   • Create appropriate documents and part studios")
    print("   • Generate necessary sketches")
    print("   • Apply 3D operations in the correct order")
    print("   • Add finishing features and modifications")
    print("   • Consider manufacturability and assembly")
    
    print("\n🚀 This represents a major step toward AI-powered CAD!")
    print("   Engineers can now describe complex parts in natural language")
    print("   and the AI will handle the entire CAD workflow.")

if __name__ == "__main__":
    asyncio.run(demo_complex_parts()) 