"""
AI Agent for CAD generation using LLM and Onshape API
"""

import json
import asyncio
import re
from typing import Dict, Any, List, Optional
from .llm_interface import LLMFactory, LLMInterface
from .onpy_client import OnPyClient

class CADAgent:
    """AI agent for generating CAD parts from natural language descriptions"""
    
    def __init__(self, llm_type: str = "groq"):
        self.llm = LLMFactory.create_interface(llm_type)
        self.onshape = OnPyClient()
        self.current_document = None
        self.current_workspace = None
        self.current_part_studio = None
        
        # Test connection first
        if not self.onshape.test_connection():
            raise Exception("Failed to connect to Onshape API. Check your API keys and authentication.")
        
        # Define simplified CAD tools for the LLM (matching what actually works)
        self.tools = [
            # Document and workspace management
            {
                "type": "function",
                "function": {
                    "name": "create_document",
                    "description": "Create a new Onshape document for CAD work",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the document"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the document"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "select_document",
                    "description": "Select an existing document to work with by ID or name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "Document ID (24-character string) or document name to search for"
                            }
                        },
                        "required": ["document_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_part_studio",
                    "description": "Create a new part studio in the current document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the part studio"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            
            # Sketch operations
            {
                "type": "function",
                "function": {
                    "name": "create_sketch",
                    "description": "Create an empty sketch on a specified plane",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plane": {
                                "type": "string",
                                "description": "Plane name to sketch on (Front, Top, Right, or custom plane name)"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name for the sketch"
                            }
                        },
                        "required": ["plane", "name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_circle_to_sketch",
                    "description": "Add a circle to an existing sketch",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to add circle to"
                            },
                            "center": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Center position [x, y]"
                            },
                            "radius": {
                                "type": "number",
                                "description": "Radius as a NUMBER ONLY - NO UNITS! Example: 25 (not '25mm')"
                            }
                        },
                        "required": ["sketch_name", "center", "radius"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_rectangle_to_sketch",
                    "description": "Add a rectangle to an existing sketch",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to add rectangle to"
                            },
                            "corner_1": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "First corner position [x, y]"
                            },
                            "corner_2": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Opposite corner position [x, y]"
                            }
                        },
                        "required": ["sketch_name", "corner_1", "corner_2"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_line_to_sketch",
                    "description": "Add a straight line to an existing sketch",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to add line to"
                            },
                            "start_point": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Start point [x, y] in mm (NO UNITS, just numbers like [0, 10])"
                            },
                            "end_point": {
                                "type": "array", 
                                "items": {"type": "number"},
                                "description": "End point [x, y] in mm (NO UNITS, just numbers like [50, 30])"
                            }
                        },
                        "required": ["sketch_name", "start_point", "end_point"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_arc_to_sketch",
                    "description": "Add a circular arc to an existing sketch", 
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to add arc to"
                            },
                            "centerpoint": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Arc center point [x, y] in mm (NO UNITS, just numbers)"
                            },
                            "radius": {
                                "type": "number",
                                "description": "Arc radius in mm (NO UNITS, just number like 15)"
                            },
                            "start_angle": {
                                "type": "number",
                                "description": "Start angle in degrees (0-360)"
                            },
                            "end_angle": {
                                "type": "number", 
                                "description": "End angle in degrees (0-360)"
                            }
                        },
                        "required": ["sketch_name", "centerpoint", "radius", "start_angle", "end_angle"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trace_points_in_sketch",
                    "description": "Create connected lines through multiple points in a sketch",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to add lines to"
                            },
                            "points": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"}
                                },
                                "description": "Array of points [[x1, y1], [x2, y2], [x3, y3]] in mm (NO UNITS, just numbers)"
                            },
                            "end_connect": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to connect the last point back to the first (closes the shape)"
                            }
                        },
                        "required": ["sketch_name", "points"]
                    }
                }
            },
            
            # Feature operations
            {
                "type": "function",
                "function": {
                    "name": "extrude_sketch",
                    "description": "Extrude a sketch to create a 3D feature with different boolean operations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_name": {
                                "type": "string",
                                "description": "Name of the sketch to extrude"
                            },
                            "endBoundOffset": {
                                "type": "number",
                                "description": "Extrusion distance as a NUMBER ONLY - NO UNITS! Example: 70 (not '70mm')"
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["new", "add", "remove", "intersect"],
                                "default": "new",
                                "description": "Boolean operation: 'new' creates new part, 'add' joins with existing, 'remove' cuts/subtracts from existing part (like drilling holes), 'intersect' keeps only overlapping volume"
                            }
                        },
                        "required": ["sketch_name", "endBoundOffset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "revolve_sketch",
                    "description": "Revolve a sketch around an axis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sketch_id": {
                                "type": "string",
                                "description": "ID of the sketch to revolve"
                            },
                            "axis": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Axis direction [x, y, z]"
                            },
                            "axisPoint": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Point on the axis [x, y, z]"
                            },
                            "angle": {
                                "type": "number",
                                "description": "Revolve angle in degrees"
                            }
                        },
                        "required": ["sketch_id", "axis", "angle"]
                    }
                }
            },
            
            # Feature management
            {
                "type": "function", 
                "function": {
                    "name": "get_features",
                    "description": "Get list of features in the current part studio",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_planes",
                    "description": "Get available default planes (Front, Top, Right) with their IDs",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_feature",
                    "description": "Delete a feature from the part studio",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "feature_id": {
                                "type": "string",
                                "description": "ID of the feature to delete"
                            }
                        },
                        "required": ["feature_id"]
                    }
                }
            },
            
            # Modification features
            {
                "type": "function",
                "function": {
                    "name": "create_fillet",
                    "description": "Create a fillet (rounded edge) feature",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "edge_queries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of edge IDs to fillet"
                            },
                            "radius": {
                                "type": "number", 
                                "description": "Fillet radius"
                            }
                        },
                        "required": ["edge_queries", "radius"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_chamfer",
                    "description": "Create a chamfer (angled edge) feature",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "edge_queries": {
                                "type": "array",
                                "items": {"type": "string"}, 
                                "description": "List of edge IDs to chamfer"
                            },
                            "distance": {
                                "type": "number",
                                "description": "Chamfer distance"
                            }
                        },
                        "required": ["edge_queries", "distance"]
                    }
                }
            }
        ]
        
        # Simplified system message for the LLM
        self.system_message = """You are an AI CAD assistant that helps users create 3D parts in Onshape using OnPy like a real engineer would. 
        You must follow proper CAD workflow: create empty sketches first, add geometry to them, then extrude.
        
        Available operations:
        - Document and workspace management (create/select documents, create part studios)
        - Sketch creation (create_sketch - creates empty sketch on plane)
        - Sketch geometry (add_circle_to_sketch, add_rectangle_to_sketch, add_line_to_sketch, add_arc_to_sketch, trace_points_in_sketch)
        - 3D features (extrude_sketch with operations: new/add/remove/intersect, revolve_sketch) 
        - Feature management (get_features, delete_feature)
        - Modifications (create_fillet, create_chamfer)
        
        CRITICAL WORKFLOW RULES:
        1. Always start by creating or selecting a document
        2. Create a part studio for 3D modeling
        3. Create empty sketches first: create_sketch(plane="Top", name="Base Sketch")
        4. Add geometry to sketches: add_circle_to_sketch(sketch_name="Base Sketch", center=[0,0], radius=25)
        5. Extrude sketches by name: extrude_sketch(sketch_name="Base Sketch", endBoundOffset=50)
        
        Example workflow for a cylinder:
        1. create_document(name="Cylinder Part")
        2. create_part_studio(name="Main")
        3. create_sketch(plane="Top", name="Circle Sketch")
        4. add_circle_to_sketch(sketch_name="Circle Sketch", center=[0,0], radius=25)
        5. extrude_sketch(sketch_name="Circle Sketch", endBoundOffset=50)
        
        Example workflow for a box:
        1. create_document(name="Box Part")
        2. create_part_studio(name="Main")
        3. create_sketch(plane="Front", name="Rectangle Sketch")
        4. add_rectangle_to_sketch(sketch_name="Rectangle Sketch", corner_1=[-25,-15], corner_2=[25,15])
        5. extrude_sketch(sketch_name="Rectangle Sketch", endBoundOffset=30)
        
        Example workflow for drilling a hole (remove operation):
        1. First create a base part with extrude_sketch(operation="new")
        2. create_sketch(plane="Top", name="Hole Sketch")  
        3. add_circle_to_sketch(sketch_name="Hole Sketch", center=[10,10], radius=5)
        4. extrude_sketch(sketch_name="Hole Sketch", endBoundOffset=20, operation="remove")
        
        Example workflow for complex profile with lines and arcs:
        1. create_sketch(plane="Front", name="Profile Sketch")
        2. trace_points_in_sketch(sketch_name="Profile Sketch", points=[[0,0], [50,0], [50,30]], end_connect=False)
        3. add_arc_to_sketch(sketch_name="Profile Sketch", centerpoint=[50,30], radius=10, start_angle=0, end_angle=90)
        4. add_line_to_sketch(sketch_name="Profile Sketch", start_point=[60,30], end_point=[60,60])
        5. extrude_sketch(sketch_name="Profile Sketch", endBoundOffset=25)
        
        EXTRUDE OPERATIONS EXPLAINED:
        - operation="new": Creates a new separate part
        - operation="add": Joins/merges with existing parts (union)
        - operation="remove": Cuts away/subtracts from existing parts (like drilling holes)
        - operation="intersect": Keeps only overlapping volume
        
        SKETCH GEOMETRY CAPABILITIES:
        - Lines: add_line_to_sketch(start_point=[x1,y1], end_point=[x2,y2])
        - Arcs: add_arc_to_sketch(centerpoint=[x,y], radius=R, start_angle=0, end_angle=90) 
        - Connected lines: trace_points_in_sketch(points=[[x1,y1], [x2,y2], [x3,y3]])
        - Basic shapes: add_circle_to_sketch, add_rectangle_to_sketch
        
        CRITICAL DIMENSIONAL ACCURACY REQUIREMENTS:
        - MAKE SURE ALL DIMENSIONS ARE EXACTLY AS THE USER SPECIFIES
        - Double-check every radius, length, width, height, angle, and position
        - If user says "50mm diameter", use radius=25 (half of diameter)
        - If user says "100mm x 50mm rectangle", use corner_1=[0,0], corner_2=[100,50]
        - CAREFULLY THINK THROUGH ALL ACTIONS TO ENSURE PART PERFECTION
        
        ABSOLUTELY CRITICAL: NEVER use strings like "70mm" or '25mm' - ALWAYS use plain numbers like 70 or 25!
        
        Design principles:
        - Think like a mechanical engineer - empty sketch → geometry → extrude
        - CRITICAL: ALL NUMBERS MUST BE PLAIN NUMBERS WITHOUT UNITS! 
        - Use radius=25 NOT "25mm" or '25mm' - the system converts to mm automatically
        - Create logical, organized designs with descriptive sketch names
        - Break complex parts into logical features
        - Use descriptive names like "Base Sketch", "Handle Profile", etc.
        
        IMPORTANT: This matches the proper OnPy workflow from the examples. Always create empty sketches first, then add geometry.
        Be precise with dimensions and positions. Always think step by step and create professional-quality designs."""
    
    async def create_part_from_description(self, description: str) -> str:
        """Create a CAD part from a natural language description using agentic workflow"""
        
        print("\n" + "="*80)
        print(f"🤖 AI CAD AGENT STARTING")
        print(f"📝 USER REQUEST: {description}")
        print("="*80)
        
        try:
            return await self._agentic_workflow(description)
        except Exception as e:
            print(f"\n❌ AGENT ERROR: {str(e)}")
            return f"Error creating part: {str(e)}"
    
    async def _agentic_workflow(self, description: str) -> str:
        """Execute the agentic workflow step by step"""
        
        step_count = 0
        max_steps = 10  # Prevent infinite loops
        context = f"User wants to create: {description}"
        
        while step_count < max_steps:
            step_count += 1
            
            print(f"\n🔄 STEP {step_count}: AGENT THINKING...")
            print("-" * 60)
            
            # Get the next action from the LLM
            next_action = await self._plan_next_step(context, description)
            
            if next_action.get("action") == "complete":
                print(f"\n✅ AGENT COMPLETE: {next_action.get('message', 'Task completed successfully!')}")
                return next_action.get("message", "Part creation completed successfully!")
            
            # Execute the planned action
            step_result = await self._execute_planned_step(next_action)
            
            # Show results to user
            print(f"\n📊 STEP {step_count} RESULT:")
            print(f"   Status: {'✅ SUCCESS' if step_result['success'] else '❌ FAILED'}")
            print(f"   Output: {step_result['output']}")
            
            # Update context for next iteration
            context += f"\n\nStep {step_count}: {next_action.get('description', 'Unknown action')}"
            context += f"\nResult: {step_result['output']}"
            
            if not step_result['success']:
                print(f"\n❌ STEP FAILED: {step_result['output']}")
                break
        
        return "Agent workflow completed or reached maximum steps."
    
    async def _plan_next_step(self, context: str, original_description: str) -> Dict[str, Any]:
        """Use LLM to plan the next step based on current context"""
        
        available_tools = [tool["function"]["name"] for tool in self.tools]
        tool_descriptions = []
        for tool in self.tools:
            func = tool["function"]
            params = list(func["parameters"]["properties"].keys())
            tool_descriptions.append(f"- {func['name']}: {func['description']} (params: {params})")
        
        planning_prompt = f"""
        You are an AI CAD agent. Based on the context below, determine the next single step to take.
        
        CONTEXT:
        {context}
        
        ORIGINAL REQUEST: {original_description}
        
        CURRENT STATUS:
        - Document: {'Selected (ID: ' + self.current_document + ')' if self.current_document else 'None'}
        - Workspace: {'Selected (ID: ' + self.current_workspace + ')' if self.current_workspace else 'None'}  
        - Part Studio: {'Selected (ID: ' + self.current_part_studio + ')' if self.current_part_studio else 'None'}
        
        CURRENT FEATURES:
        {self.onshape.get_current_features_summary() if hasattr(self.onshape, 'get_current_features_summary') else 'No features tracking available'}
        
        AVAILABLE SKETCHES:
        {self.onshape.get_available_sketches() if hasattr(self.onshape, 'get_available_sketches') else []}
        
        WORKFLOW GUIDANCE:
        1. If no document/part studio: create_document -> create_part_studio
        2. If have part studio: create sketches with plane -> extrude sketches
        3. Add modifications (fillets, chamfers) last
        
        AVAILABLE TOOLS (use EXACT names):
        {chr(10).join(tool_descriptions)}
        
        CRITICAL REQUIREMENTS: 
        - Use EXACT tool names from the list above
        - For sketches, ALWAYS specify a plane (Front, Top, or Right)
        - When adding geometry, use the EXACT sketch name from "AVAILABLE SKETCHES" list above
        - If you see "MugBase" in Available Sketches, use sketch_name="MugBase" exactly
        - ALL NUMERIC VALUES MUST BE PLAIN NUMBERS WITHOUT UNITS!
        - Use endBoundOffset=70 NOT "70mm" or '70mm' or "70 mm"
        - Use radius=25 NOT "25mm" or '25mm' 
        
        DIMENSIONAL ACCURACY IMPERATIVE:
        - MAKE SURE ALL DIMENSIONS ARE EXACTLY AS THE USER SPECIFIES
        - CAREFULLY THINK THROUGH ALL ACTIONS TO ENSURE PART PERFECTION
        - Double-check calculations: diameter ÷ 2 = radius, verify all measurements
        - Plan each step methodically before executing
        
        - Continue until the original request is fully completed
        - Only complete when the part is fully designed
        
        Respond ONLY with valid JSON in this exact format:
        {{
            "action": "tool_call",
            "tool_name": "exact_tool_name",
            "tool_args": {{"param": "value"}},
            "description": "what this step does",
            "reasoning": "why this step is needed"
        }}
        
        OR if truly complete:
        {{
            "action": "complete",
            "message": "Part creation completed successfully",
            "reasoning": "all requested features have been created"
        }}
        """
        
        response = await self.llm.generate(planning_prompt, max_tokens=12000, temperature=0.1)
        
        # Debug: Print the raw LLM response to see what's happening
        print(f"🔍 DEBUG - Raw LLM Response:")
        print(f"   {response}")
        
        try:
            # Extract JSON from response
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print(f"🔍 DEBUG - Extracted JSON: {json_str}")
                plan = json.loads(json_str)
            else:
                print(f"⚠️  No JSON found in response: {response}")
                # Fallback if no JSON found
                plan = {
                    "action": "complete",
                    "message": "Could not find JSON in planning response"
                }
            
            print(f"🧠 AGENT PLAN:")
            print(f"   Action: {plan.get('action', 'unknown')}")
            print(f"   Reasoning: {plan.get('reasoning', 'No reasoning provided')}")
            if plan.get('action') == 'tool_call':
                print(f"   Tool: {plan.get('tool_name', 'unknown')}")
                print(f"   Description: {plan.get('description', 'No description')}")
            
            return plan
            
        except Exception as e:
            print(f"⚠️  Planning error: {str(e)}")
            print(f"   Response was: {response}")
            return {
                "action": "complete",
                "message": f"Planning failed: {str(e)}"
            }
    
    async def _execute_planned_step(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single planned step"""
        
        if plan.get("action") != "tool_call":
            return {"success": False, "output": "Invalid action type"}
        
        tool_name = plan.get("tool_name")
        tool_args = plan.get("tool_args", {})
        
        print(f"⚙️  EXECUTING: {plan.get('description', 'Unknown action')}")
        print(f"   Tool: {tool_name}")
        print(f"   Args: {tool_args}")
        
        try:
            # Check if tool exists in our available tools
            available_tool_names = [tool["function"]["name"] for tool in self.tools]
            if tool_name not in available_tool_names:
                return {
                    "success": False,
                    "output": f"Tool '{tool_name}' not found. Available tools: {available_tool_names}"
                }
            
            # Create a fake tool call structure for the existing executor
            tool_call = {
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_args)
                }
            }
            
            await self._execute_tool_call(tool_call)
            
            return {
                "success": True,
                "output": f"Successfully executed {tool_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": f"Failed to execute {tool_name}: {str(e)}"
            }
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> None:
        """Execute a tool call from the LLM"""
        
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        try:
            if function_name == "create_document":
                print(f"🔧 Creating Onshape document: {arguments['name']}")
                result = self.onshape.create_document(
                    name=arguments["name"],
                    description=arguments.get("description", "")
                )
                self.current_document = result["id"]
                self.current_workspace = result["defaultWorkspace"]["id"]
                print(f"✅ Created document: {result['name']} (ID: {self.current_document})")
                print(f"   Workspace ID: {self.current_workspace}")
                
            elif function_name == "select_document":
                document_id = arguments["document_id"]
                
                # If the document_id looks like a name (contains spaces, not 24 chars), search for it
                if len(document_id) != 24 or ' ' in document_id:
                    print(f"Searching for document with name: {document_id}")
                    search_results = self.onshape.search_documents_by_name(document_id)
                    print(f"Search returned: {search_results}")
                    
                    if not search_results or len(search_results) == 0:
                        # Try creating a document if search fails
                        print(f"No documents found with name '{document_id}'. Creating new document.")
                        create_result = self.onshape.create_document(name=document_id)
                        document_id = create_result["id"]
                        self.current_document = document_id
                        self.current_workspace = create_result["defaultWorkspace"]["id"]
                        print(f"Created new document: {create_result['name']} (ID: {document_id})")
                        return
                    else:
                        # Use the first match
                        if isinstance(search_results, list) and len(search_results) > 0:
                            document_id = search_results[0]["id"]
                            print(f"Found document: {search_results[0]['name']} (ID: {document_id})")
                        else:
                            raise Exception(f"Invalid search results format: {search_results}")
                
                # Get document info to validate
                result = self.onshape.get_document_info(document_id)
                workspaces = self.onshape.get_workspaces(document_id)
                self.current_document = document_id
                self.current_workspace = workspaces[0]["id"] if workspaces else None
                print(f"Selected document: {result['name']} (ID: {self.current_document})")
                
            elif function_name == "create_part_studio":
                if not self.current_document or not self.current_workspace:
                    raise Exception("No document or workspace selected. Create a document first.")
                
                print(f"🔧 Creating part studio: {arguments['name']}")
                result = self.onshape.create_part_studio(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    name=arguments["name"]
                )
                self.current_part_studio = result["id"]
                print(f"✅ Created part studio: {arguments['name']} (ID: {self.current_part_studio})")
                
            elif function_name == "create_sketch":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.create_sketch(
                    plane_name=arguments["plane"],
                    sketch_name=arguments["name"]
                )
                sketch_id = result.get("feature", {}).get("featureId")
                print(f"✅ Created empty sketch: '{arguments['name']}' on plane '{arguments['plane']}' (ID: {sketch_id})")
                
            elif function_name == "add_circle_to_sketch":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.add_circle_to_sketch(
                    sketch_name=arguments["sketch_name"],
                    center=arguments["center"],
                    radius=arguments["radius"]
                )
                print(f"✅ Added circle to sketch '{arguments['sketch_name']}': radius {arguments['radius']}mm")
                
            elif function_name == "add_rectangle_to_sketch":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.add_rectangle_to_sketch(
                    sketch_name=arguments["sketch_name"],
                    corner_1=arguments["corner_1"],
                    corner_2=arguments["corner_2"]
                )
                print(f"✅ Added rectangle to sketch '{arguments['sketch_name']}'")
                
            elif function_name == "add_line_to_sketch":
                result = self.onshape.add_line_to_sketch(
                    sketch_name=arguments["sketch_name"],
                    start_point=arguments["start_point"],
                    end_point=arguments["end_point"]
                )
                print(f"✅ Added line to sketch '{arguments['sketch_name']}'")
                
            elif function_name == "add_arc_to_sketch":
                result = self.onshape.add_arc_to_sketch(
                    sketch_name=arguments["sketch_name"],
                    centerpoint=arguments["centerpoint"],
                    radius=arguments["radius"],
                    start_angle=arguments["start_angle"],
                    end_angle=arguments["end_angle"]
                )
                print(f"✅ Added arc to sketch '{arguments['sketch_name']}'")
                
            elif function_name == "trace_points_in_sketch":
                result = self.onshape.trace_points_in_sketch(
                    sketch_name=arguments["sketch_name"],
                    points=arguments["points"],
                    end_connect=arguments.get("end_connect", True)
                )
                print(f"✅ Traced {len(arguments['points'])} points in sketch '{arguments['sketch_name']}'")
                
            elif function_name == "extrude_sketch":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.extrude_sketch_by_name(
                    sketch_name=arguments["sketch_name"],
                    distance=arguments["endBoundOffset"],
                    operation=arguments.get("operation", "new")
                )
                print(f"Extruded sketch '{arguments['sketch_name']}': {arguments.get('endBoundOffset', 'default')} mm")
                
            elif function_name == "revolve_sketch":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.revolve_sketch(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    part_studio_id=self.current_part_studio,
                    sketch_id=arguments["sketch_id"],
                    revolve_data=arguments
                )
                print(f"Revolved sketch: {arguments.get('angle', 'default')} degrees")
                

            elif function_name == "get_features":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.get_part_studio_features(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    part_studio_id=self.current_part_studio
                )
                print(f"Retrieved {len(result.get('features', []))} features from part studio")
                
            elif function_name == "get_planes":
                result = self.onshape.get_available_planes()
                print(f"Available planes: {result}")
                
            elif function_name == "delete_feature":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.delete_part_studio_feature(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    part_studio_id=self.current_part_studio,
                    feature_id=arguments["feature_id"]
                )
                print(f"Deleted feature: {arguments['feature_id']}")
                
            elif function_name == "create_fillet":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.create_fillet(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    part_studio_id=self.current_part_studio,
                    edge_queries=arguments["edge_queries"],
                    radius=arguments["radius"]
                )
                print(f"Created fillet: radius {arguments['radius']} mm on {len(arguments['edge_queries'])} edges")
                
            elif function_name == "create_chamfer":
                if not self.current_part_studio:
                    raise Exception("No part studio selected. Create a part studio first.")
                
                result = self.onshape.create_chamfer(
                    document_id=self.current_document,
                    workspace_id=self.current_workspace,
                    part_studio_id=self.current_part_studio,
                    edge_queries=arguments["edge_queries"],
                    distance=arguments["distance"]
                )
                print(f"Created chamfer: distance {arguments['distance']} mm on {len(arguments['edge_queries'])} edges")
                
            else:
                print(f"Unknown tool: {function_name}")
                
        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the CAD session"""
        return {
            "document_id": self.current_document,
            "workspace_id": self.current_workspace,
            "part_studio_id": self.current_part_studio,
            "tools_available": [tool["function"]["name"] for tool in self.tools]
        }
    
    async def reset_session(self) -> None:
        """Reset the current CAD session"""
        self.current_document = None
        self.current_workspace = None
        self.current_part_studio = None
        print("CAD session reset")
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List available documents"""
        return self.onshape.get_documents()
    
    def test_connection(self) -> bool:
        """Test connection to Onshape API"""
        return self.onshape.test_connection() 