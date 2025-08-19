"""
OnPy-based client for CAD operations in Onshape
Using the OnPy library for robust Onshape API interactions
"""

import onpy
import os
from typing import Dict, Any, List, Optional
from .config import config

class OnPyClient:
    """Client for interacting with Onshape using OnPy library"""
    
    def __init__(self):
        self.current_document = None
        self.current_partstudio = None
        self.sketches = {}  # Store sketch objects by name
        self.planes = {}    # Store plane objects by name
        self.features = {}  # Store all features (sketches, extrudes, etc) with metadata
        self.parts = []     # Store created parts for boolean operations
        
        # Set OnPy environment variables from your existing config
        # OnPy expects ONSHAPE_DEV_ACCESS and ONSHAPE_DEV_SECRET
        if hasattr(config, 'ONSHAPE_ACCESS_KEY') and config.ONSHAPE_ACCESS_KEY:
            os.environ['ONSHAPE_DEV_ACCESS'] = config.ONSHAPE_ACCESS_KEY
        if hasattr(config, 'ONSHAPE_SECRET_KEY') and config.ONSHAPE_SECRET_KEY:
            os.environ['ONSHAPE_DEV_SECRET'] = config.ONSHAPE_SECRET_KEY
        
    def test_connection(self) -> bool:
        """Test if we can connect to Onshape API"""
        try:
            # Try to create a test document to verify connection
            test_doc = onpy.create_document("OnPy Connection Test")
            # Delete it immediately if successful
            # Note: OnPy might not have delete functionality, so we'll just leave it
            print("✅ OnPy connection successful!")
            return True
        except Exception as e:
            print(f"❌ OnPy connection failed: {str(e)}")
            return False
    
    # ===== DOCUMENT MANAGEMENT =====
    
    def create_document(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new document using OnPy"""
        try:
            self.current_document = onpy.create_document(name)
            return {
                "id": "onpy_document",  # OnPy handles IDs internally
                "name": name,
                "defaultWorkspace": {"id": "onpy_workspace"}
            }
        except Exception as e:
            raise Exception(f"Failed to create document: {str(e)}")
    
    def select_document_by_name(self, name: str) -> Dict[str, Any]:
        """Select an existing document by name"""
        # For now, create a new document since OnPy doesn't have document search
        # In a real implementation, you'd need to store document references
        return self.create_document(name)
    
    # ===== PART STUDIO MANAGEMENT =====
    
    def create_part_studio(self, document_id: str, workspace_id: str, name: str) -> Dict[str, Any]:
        """Get or create a part studio - OnPy handles this automatically"""
        if not self.current_document:
            raise Exception("No document selected. Create a document first.")
        
        self.current_partstudio = self.current_document.get_partstudio()
        
        # Initialize default planes
        self.planes["Front"] = self.current_partstudio.features.front_plane
        self.planes["Top"] = self.current_partstudio.features.top_plane
        self.planes["Right"] = self.current_partstudio.features.right_plane
        
        return {
            "id": "onpy_partstudio",
            "name": name
        }
    
    # ===== SKETCH OPERATIONS =====
    
    def create_sketch(self, plane_name: str, sketch_name: str) -> Dict[str, Any]:
        """Create an empty sketch using OnPy - matching lamp example approach"""
        if not self.current_partstudio:
            raise Exception("No part studio available. Create a part studio first.")
        
        # Get plane object using the same approach as the lamp example
        try:
            if plane_name.lower() == "top":
                plane = self.current_partstudio.features.top_plane
            elif plane_name.lower() == "front":
                plane = self.current_partstudio.features.front_plane
            elif plane_name.lower() == "right":
                plane = self.current_partstudio.features.right_plane
            else:
                # For custom planes, try to find in stored planes
                plane = self.planes.get(plane_name)
                if not plane:
                    raise Exception(f"Unknown plane: {plane_name}. Available: Front, Top, Right")
        except Exception as e:
            raise Exception(f"Failed to get plane '{plane_name}': {str(e)}")
        
        # Create the empty sketch using exact same syntax as lamp example
        try:
            sketch = self.current_partstudio.add_sketch(plane=plane, name=sketch_name)
            print(f"✅ Created sketch using OnPy: {sketch}")
        except Exception as e:
            raise Exception(f"Failed to create sketch with OnPy: {str(e)}")
        
        # Store the sketch for later geometry addition
        self.sketches[sketch_name] = sketch
        
        # Track in features list
        self.features[sketch_name] = {
            "type": "sketch",
            "plane": plane_name,
            "has_geometry": False,
            "object": sketch
        }
        
        print(f"✅ Created empty sketch '{sketch_name}' on plane '{plane_name}'")
        
        return {
            "feature": {
                "featureId": f"sketch_{id(sketch)}",
                "name": sketch_name
            },
            "sketch_object": sketch
        }
    
    def create_rectangle_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                               corner: List[float], width: float, height: float, 
                               plane: str = "Front") -> Dict[str, Any]:
        """Create a rectangle sketch using OnPy"""
        sketch_data = {"name": "Rectangle Sketch", "plane": plane}
        result = self.create_sketch(document_id, workspace_id, part_studio_id, sketch_data)
        
        # Add rectangle geometry to the sketch
        sketch_obj = result["sketch_object"]
        
        # OnPy uses different methods - we'll create a rectangle using lines or built-in methods
        # For now, let's create individual lines to form a rectangle
        x, y = corner[0], corner[1]
        
        # Add rectangle lines (OnPy may have a built-in rectangle method)
        try:
            # Try to use OnPy's rectangle method if available
            sketch_obj.add_rectangle(corner=(x, y), width=width, height=height)
        except AttributeError:
            # Fallback: create rectangle with lines
            sketch_obj.add_line(start=(x, y), end=(x + width, y))
            sketch_obj.add_line(start=(x + width, y), end=(x + width, y + height))
            sketch_obj.add_line(start=(x + width, y + height), end=(x, y + height))
            sketch_obj.add_line(start=(x, y + height), end=(x, y))
        
        return result
    
    def create_circle_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                            center: List[float], radius: float, 
                            plane: str = "Front") -> Dict[str, Any]:
        """Create a circle sketch using OnPy"""
        sketch_data = {"name": "Circle Sketch", "plane": plane}
        result = self.create_sketch(document_id, workspace_id, part_studio_id, sketch_data)
        
        # Add circle geometry to the sketch
        sketch_obj = result["sketch_object"]
        sketch_obj.add_circle(center=(center[0], center[1]), radius=radius)
        
        return result
    
    def add_circle_to_sketch(self, sketch_name: str, center: List[float], radius: float) -> Dict[str, Any]:
        """Add a circle to an existing sketch - matching lamp example approach"""
        if sketch_name not in self.sketches:
            raise Exception(f"Sketch '{sketch_name}' not found. Available sketches: {list(self.sketches.keys())}")
        
        sketch = self.sketches[sketch_name]
        
        # Convert mm to inches (OnPy default) since AI passes in mm
        radius_inches = radius / 25.4
        center_inches = (center[0] / 25.4, center[1] / 25.4)
        
        try:
            # Use exact same syntax as lamp example: sketch.add_circle(center=(0, 0), radius=0.5)
            sketch.add_circle(center=center_inches, radius=radius_inches)
            
            # Update feature tracking
            if sketch_name in self.features:
                self.features[sketch_name]["has_geometry"] = True
                self.features[sketch_name]["geometry_type"] = "circle"
                self.features[sketch_name]["details"] = f"radius={radius}"
            
            print(f"✅ Added circle to '{sketch_name}': center={center_inches}, radius={radius_inches} inches ({radius}mm)")
            return {"success": True}
        except Exception as e:
            print(f"❌ OnPy circle error details:")
            print(f"   - Sketch: {sketch}")
            print(f"   - Center: {center_inches}")
            print(f"   - Radius: {radius_inches} inches ({radius}mm)")
            print(f"   - Error: {str(e)}")
            raise Exception(f"Failed to add circle to sketch '{sketch_name}': {str(e)}")
     
    def add_rectangle_to_sketch(self, sketch_name: str, corner_1: List[float], corner_2: List[float]) -> Dict[str, Any]:
        """Add a rectangle to an existing sketch using corner rectangle method"""
        if sketch_name not in self.sketches:
            raise Exception(f"Sketch '{sketch_name}' not found. Available sketches: {list(self.sketches.keys())}")
        
        sketch = self.sketches[sketch_name]
        
        # Convert mm to inches (OnPy default) since AI passes in mm
        corner_1_inches = (corner_1[0] / 25.4, corner_1[1] / 25.4)
        corner_2_inches = (corner_2[0] / 25.4, corner_2[1] / 25.4)
        
        try:
            sketch.add_corner_rectangle(corner_1=corner_1_inches, corner_2=corner_2_inches)
            
            # Update feature tracking
            if sketch_name in self.features:
                self.features[sketch_name]["has_geometry"] = True
                self.features[sketch_name]["geometry_type"] = "rectangle"
                width = abs(corner_2[0] - corner_1[0])
                height = abs(corner_2[1] - corner_1[1])
                self.features[sketch_name]["details"] = f"{width}x{height}mm"
            
            print(f"✅ Added rectangle to '{sketch_name}': corners={corner_1_inches} to {corner_2_inches} inches ({corner_1} to {corner_2} mm)")
            return {"success": True}
        except Exception as e:
            raise Exception(f"Failed to add rectangle to sketch '{sketch_name}': {str(e)}")
    
    # ===== FEATURE OPERATIONS =====
    
    def extrude_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                       sketch_id: str, extrude_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrude a sketch using OnPy"""
        if not self.current_partstudio:
            raise Exception("No part studio available.")
        
        # Find the sketch object by ID (this is a simplification)
        # In a real implementation, you'd need to track sketch objects
        sketch_obj = getattr(self, '_last_sketch', None)
        if not sketch_obj:
            raise Exception("No sketch found to extrude. Create a sketch first.")
        
        distance = extrude_data.get("endBoundOffset", 10.0)
        
        # Create extrude using OnPy
        extrude = self.current_partstudio.add_extrude(
            faces=sketch_obj,
            distance=distance / 25.4  # Convert mm to inches (OnPy default)
        )
        
        return {
            "feature": {
                "featureId": f"extrude_{id(extrude)}",
                "name": f"Extrude {distance}mm"
            }
        }
    
    def revolve_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                      sketch_id: str, revolve_data: Dict[str, Any]) -> Dict[str, Any]:
        """Revolve a sketch using OnPy"""
        if not self.current_partstudio:
            raise Exception("No part studio available.")
        
        sketch_obj = getattr(self, '_last_sketch', None)
        if not sketch_obj:
            raise Exception("No sketch found to revolve. Create a sketch first.")
        
        angle = revolve_data.get("angle", 360.0)
        
        # OnPy revolve (if available)
        try:
            revolve = self.current_partstudio.add_revolve(
                faces=sketch_obj,
                angle=angle
            )
            return {
                "feature": {
                    "featureId": f"revolve_{id(revolve)}",
                    "name": f"Revolve {angle}°"
                }
            }
        except AttributeError:
            raise Exception("Revolve feature not available in current OnPy version")
    
    def extrude_sketch_by_name(self, sketch_name: str, distance: float, operation: str = "new") -> Dict[str, Any]:
        """Extrude a sketch by name using OnPy"""
        if not self.current_partstudio:
            raise Exception("No part studio available.")
        
        if sketch_name not in self.sketches:
            raise Exception(f"Sketch '{sketch_name}' not found. Available sketches: {list(self.sketches.keys())}")
        
        sketch = self.sketches[sketch_name]
        
        # Convert mm to inches (OnPy default)
        distance_inches = distance / 25.4
        
        try:
            # Handle different extrude operations using OnPy's approach
            extrude_params = {
                "faces": sketch,
                "distance": distance_inches,
                "name": f"Extrude {distance}mm ({operation})"
            }
            
            # OnPy uses specific parameters for different operations
            if operation.lower() == "remove":
                # For remove operations, we need to specify what to subtract from
                if self.parts:
                    # Use the most recent part as the target
                    target_part = self.parts[-1]
                    extrude_params["subtract_from"] = target_part
                    print(f"🔧 Remove operation: subtracting from existing part")
                else:
                    print("⚠️ Warning: Remove operation requested but no existing parts found")
            elif operation.lower() == "add":
                # Add operations merge with existing geometry automatically in OnPy
                pass
            elif operation.lower() == "intersect":
                # OnPy may not support intersect directly - will use as new
                print("⚠️ Warning: Intersect operation not fully supported, using as new")
            # "new" is the default - no special parameters needed
            
            extrude = self.current_partstudio.add_extrude(**extrude_params)
            
            # Store created parts for future boolean operations
            if hasattr(extrude, 'get_created_parts'):
                created_parts = extrude.get_created_parts()
                if created_parts:
                    self.parts.extend(created_parts)
                    print(f"📦 Stored {len(created_parts)} parts for future operations")
            elif operation.lower() == "new":
                # For new operations, assume the extrude itself is a part
                self.parts.append(extrude)
                print(f"📦 Stored new part for future operations")
            
            # Track the extrude feature
            extrude_name = f"Extrude {distance}mm ({operation})"
            self.features[extrude_name] = {
                "type": "extrude",
                "operation": operation,
                "source_sketch": sketch_name,
                "distance": f"{distance}mm",
                "object": extrude
            }
            
            print(f"✅ Extruded sketch '{sketch_name}' by {distance_inches} inches ({distance}mm) using '{operation}' operation")
            return {
                "feature": {
                    "featureId": f"extrude_{id(extrude)}",
                    "name": extrude_name
                }
            }
        except Exception as e:
            raise Exception(f"Failed to extrude sketch '{sketch_name}': {str(e)}")
    
    # ===== FEATURE MANAGEMENT =====
    
    def get_current_features_summary(self) -> str:
        """Get a formatted summary of current features for AI context"""
        if not self.features:
            return "No features created yet."
        
        summary = "Current Features:\n"
        for name, info in self.features.items():
            if info["type"] == "sketch":
                geometry = f" (contains {info.get('geometry_type', 'no geometry')})" if info.get("has_geometry") else " (empty)"
                summary += f"  • '{name}': {info['type']} on {info['plane']}{geometry}\n"
            elif info["type"] == "extrude":
                summary += f"  • '{name}': {info['type']} of '{info['source_sketch']}' by {info['distance']}\n"
            else:
                summary += f"  • '{name}': {info['type']}\n"
        
        return summary.strip()
    
    def get_available_sketches(self) -> List[str]:
        """Get list of available sketch names"""
        return [name for name, info in self.features.items() if info["type"] == "sketch"]
    
    def get_available_planes(self) -> List[str]:
        """Get list of available default plane names"""
        return ["Front", "Top", "Right"]
    
    def get_part_studio_features(self, document_id: str, workspace_id: str, part_studio_id: str,
                                **kwargs) -> Dict[str, Any]:
        """Get features in a part studio"""
        # OnPy doesn't expose feature lists directly, so return a simple structure
        return {
            "features": [],
            "defaultFeatures": [
                {"name": "Front", "featureId": "front_plane"},
                {"name": "Top", "featureId": "top_plane"},
                {"name": "Right", "featureId": "right_plane"}
            ]
        }
    
    # ===== HELPER METHODS =====
    
    def _store_last_sketch(self, sketch_obj):
        """Store the last created sketch for extrude operations"""
        self._last_sketch = sketch_obj
        
    def create_fillet(self, document_id: str, workspace_id: str, part_studio_id: str,
                     edge_queries: List[str], radius: float) -> Dict[str, Any]:
        """Create a fillet using OnPy (if supported)"""
        # OnPy may not support fillets yet
        raise Exception("Fillet operations not yet supported in OnPy integration")
    
    def create_chamfer(self, document_id: str, workspace_id: str, part_studio_id: str,
                      edge_queries: List[str], distance: float) -> Dict[str, Any]:
        """Create a chamfer using OnPy (if supported)"""
        # OnPy may not support chamfers yet
        raise Exception("Chamfer operations not yet supported in OnPy integration")