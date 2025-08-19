"""
Onshape API client for CAD operations
Based on actual Onshape API documentation: https://onshape-public.github.io/docs/auth/apikeys/#local-authorization
"""

import hashlib
import hmac
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from .config import config

class OnshapeClient:
    """Client for interacting with Onshape API"""
    
    def __init__(self):
        self.access_key = config.ONSHAPE_ACCESS_KEY
        self.secret_key = config.ONSHAPE_SECRET_KEY
        self.base_url = config.ONSHAPE_BASE_URL.rstrip('/')
        
        if not self.access_key or not self.secret_key:
            raise ValueError("Onshape API keys not configured")
    
    def _generate_auth_headers(self, method: str, path: str, query: str = "", 
                              content_type: str = "application/json", 
                              body: str = "") -> Dict[str, str]:
        """Generate Onshape API Basic Authorization headers"""
        
        # For Basic Authorization, we just encode the access_key:secret_key in base64
        credentials = f"{self.access_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': content_type
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Onshape API"""
        
        url = f"{self.base_url}{endpoint}"
        
        # Prepare query string
        query = ""
        if params:
            query = "&".join([f"{k}={v}" for k, v in params.items()])
        
        # Prepare body
        body = ""
        if data:
            import json
            body = json.dumps(data)
        
        # Generate headers
        headers = self._generate_auth_headers(method, endpoint, query, body=body)
        
        # Debug output (optional)
        if config.DEBUG:
            print(f"🔍 Debug - Request Details:")
            print(f"  URL: {url}")
            print(f"  Method: {method}")
            print(f"  Headers: {headers}")
            print(f"  Query: {query}")
            print(f"  Body: {body}")
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=data if data else None,
            headers=headers
        )
        
        if response.status_code >= 400:
            print(f"❌ Request failed: {method} {url}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            raise Exception(f"Onshape API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    # ===== DOCUMENT MANAGEMENT =====
    
    def get_documents(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of user documents, optionally filtered by query"""
        params = {}
        if query:
            params['q'] = query
        result = self._make_request('GET', '/api/v10/documents', params=params)
        
        # Handle different response formats
        if isinstance(result, dict) and 'items' in result:
            return result['items']
        elif isinstance(result, list):
            return result
        else:
            print(f"Unexpected response format: {result}")
            return []
    
    def search_documents_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for documents by name"""
        return self.get_documents(query=name)
    
    def create_document(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new document"""
        data = {
            "name": name,
            "description": description
        }
        return self._make_request('POST', '/api/v10/documents', data=data)
    
    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get document information"""
        return self._make_request('GET', f'/api/v10/documents/{document_id}')
    
    def get_workspaces(self, document_id: str) -> List[Dict[str, Any]]:
        """Get workspaces in a document"""
        return self._make_request('GET', f'/api/v10/documents/{document_id}/workspaces')
    
    def get_part_studios(self, document_id: str, workspace_id: str) -> List[Dict[str, Any]]:
        """Get part studios in a document workspace"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}"
        return self._make_request('GET', endpoint)
    
    def create_part_studio(self, document_id: str, workspace_id: str, name: str) -> Dict[str, Any]:
        """Create a new part studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}"
        data = {"name": name}
        return self._make_request('POST', endpoint, data=data)
    
    # ===== SKETCH OPERATIONS =====
    
    def create_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                     sketch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sketch in a part studio using proper Onshape API format"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features"
        
        plane_name = sketch_data.get("plane", "Front")  # Default to Front plane
        
        # Proper Onshape sketch creation format - match your working curl exactly
        feature_data = {
            "feature": {
                "featureType": "newSketch",
                "name": sketch_data.get("name", "Sketch"),
                "parameters": [
                    {
                        "parameterId": "sketchPlane",
                        "parameterType": "BTMParameterQueryList",
                        "value": {
                            "queries": [
                                {
                                    "type": "BTMIndividualQuery",
                                    "queryString": f'mateConnector("{plane_name}")'
                                }
                            ]
                        }
                    }
                ],
                "entities": sketch_data.get("entities", [])
            }
        }
        
        return self._make_request('POST', endpoint, data=feature_data)
    
    def create_rectangle_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                               corner: List[float], width: float, height: float, plane: str = "Front") -> Dict[str, Any]:
        """Create a rectangle sketch with actual geometry"""
        # Create rectangle entities (4 lines forming a rectangle)
        entities = [
            {
                "entityType": "BTMSketchLine",
                "isConstruction": False,
                "parameters": {
                    "startPoint": {"x": corner[0], "y": corner[1]},
                    "endPoint": {"x": corner[0] + width, "y": corner[1]}
                }
            },
            {
                "entityType": "BTMSketchLine", 
                "isConstruction": False,
                "parameters": {
                    "startPoint": {"x": corner[0] + width, "y": corner[1]},
                    "endPoint": {"x": corner[0] + width, "y": corner[1] + height}
                }
            },
            {
                "entityType": "BTMSketchLine",
                "isConstruction": False,
                "parameters": {
                    "startPoint": {"x": corner[0] + width, "y": corner[1] + height},
                    "endPoint": {"x": corner[0], "y": corner[1] + height}
                }
            },
            {
                "entityType": "BTMSketchLine",
                "isConstruction": False,
                "parameters": {
                    "startPoint": {"x": corner[0], "y": corner[1] + height},
                    "endPoint": {"x": corner[0], "y": corner[1]}
                }
            }
        ]
        
        sketch_data = {
            "name": "Rectangle Sketch",
            "plane": plane,
            "entities": entities
        }
        return self.create_sketch(document_id, workspace_id, part_studio_id, sketch_data)
    
    def create_circle_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                            center: List[float], radius: float, plane: str = "Front") -> Dict[str, Any]:
        """Create a circle sketch with actual geometry"""
        # Create circle entity based on your working example
        entities = [
            {
                "entityType": "BTMSketchCircle",
                "isConstruction": False,
                "parameters": {
                    "radius": {
                        "value": radius,
                        "units": "mm"
                    },
                    "xCenter": center[0],
                    "yCenter": center[1]
                }
            }
        ]
        
        sketch_data = {
            "name": "Circle Sketch",
            "plane": plane,
            "entities": entities
        }
        return self.create_sketch(document_id, workspace_id, part_studio_id, sketch_data)
    

    
    # ===== FEATURE OPERATIONS =====
    
    def create_feature(self, document_id: str, workspace_id: str, part_studio_id: str, 
                      feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a feature in a part studio using proper Onshape API format"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features"
        return self._make_request('POST', endpoint, data=feature_data)
    
    def extrude_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                       sketch_id: str, extrude_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrude a sketch to create a 3D feature"""
        feature_data = {
            "btType": "BTFeatureDefinitionCall-1406",
            "feature": {
                "btType": "BTMFeature-134",
                "featureType": "extrude",
                "name": f"Extrude {extrude_data.get('endBoundOffset', 10)} mm",
                "parameters": [
                    {
                        "btType": "BTMParameterQueryList-118",
                        "parameterId": "entities",
                        "queries": [
                            {
                                "btType": "BTMIndividualQuery-138",
                                "query": sketch_id,
                                "queryType": "FACE"
                            }
                        ]
                    },
                    {
                        "btType": "BTMParameterString-149",
                        "parameterId": "operationType",
                        "value": extrude_data.get("operation", "NEW")
                    },
                    {
                        "btType": "BTMParameterQuantity-147",
                        "parameterId": "depth",
                        "expression": f"{extrude_data.get('endBoundOffset', 10)} mm",
                        "isInteger": False
                    }
                ],
                "suppressed": False,
                "returnAfterSubfeatures": False
            }
        }
        return self.create_feature(document_id, workspace_id, part_studio_id, feature_data)
    
    def revolve_sketch(self, document_id: str, workspace_id: str, part_studio_id: str,
                      sketch_id: str, revolve_data: Dict[str, Any]) -> Dict[str, Any]:
        """Revolve a sketch around an axis"""
        feature_data = {
            "feature": {
                "type": "revolve",
                "entities": [{"type": "sketch", "id": sketch_id}],
                "operation": revolve_data.get("operation", "new"),
                "axis": revolve_data.get("axis", [0, 0, 1]),
                "axisPoint": revolve_data.get("axisPoint", [0, 0, 0]),
                "angle": revolve_data.get("angle", 360.0)
            }
        }
        return self.create_feature(document_id, workspace_id, part_studio_id, feature_data)
    

    
    # ===== FEATURE MANAGEMENT OPERATIONS =====
    
    def get_part_studio_features(self, document_id: str, workspace_id: str, part_studio_id: str,
                                rollback_bar_index: int = -1, include_geometry_ids: bool = True,
                                no_sketch_geometry: bool = False) -> Dict[str, Any]:
        """Get features in a part studio"""
        params = {
            "rollbackBarIndex": rollback_bar_index,
            "includeGeometryIds": include_geometry_ids,
            "noSketchGeometry": no_sketch_geometry
        }
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features"
        return self._make_request('GET', endpoint, params=params)
    
    def get_available_planes(self) -> List[str]:
        """Get list of available default plane names"""
        return ["Front", "Top", "Right"]
    
    def update_part_studio_feature(self, document_id: str, workspace_id: str, part_studio_id: str,
                                  feature_id: str, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific feature in a part studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features/featureid/{feature_id}"
        return self._make_request('POST', endpoint, data=feature_data)
    
    def update_features(self, document_id: str, workspace_id: str, part_studio_id: str,
                       features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update multiple features in a part studio"""
        feature_data = {
            "btType": "BTUpdateFeaturesCall-1748",
            "features": features
        }
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features/updates"
        return self._make_request('POST', endpoint, data=feature_data)
    
    def delete_part_studio_feature(self, document_id: str, workspace_id: str, part_studio_id: str,
                                  feature_id: str) -> Dict[str, Any]:
        """Delete a feature from a part studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features/featureid/{feature_id}"
        return self._make_request('DELETE', endpoint)
    
    def update_rollback(self, document_id: str, workspace_id: str, part_studio_id: str,
                       rollback_index: int = -1) -> Dict[str, Any]:
        """Move the rollback bar in the Feature list"""
        data = {"rollbackIndex": rollback_index}
        endpoint = f"/api/v9/partstudios/d/{document_id}/w/{workspace_id}/e/{part_studio_id}/features/rollback"
        return self._make_request('POST', endpoint, data=data)
    
    def get_part_studio_body_details(self, document_id: str, workspace_id: str, part_studio_id: str) -> Dict[str, Any]:
        """Get the body details of a Part Studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/wvm/{workspace_id}/e/{part_studio_id}/bodydetails"
        return self._make_request('GET', endpoint)
    
    def get_part_studio_mass_properties(self, document_id: str, workspace_id: str, part_studio_id: str) -> Dict[str, Any]:
        """Get the mass properties of a Part Studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/wvm/{workspace_id}/e/{part_studio_id}/massproperties"
        return self._make_request('GET', endpoint)
    
    def get_part_studio_named_views(self, document_id: str, part_studio_id: str) -> Dict[str, Any]:
        """Get the named views in a Part Studio"""
        endpoint = f"/api/v9/partstudios/d/{document_id}/e/{part_studio_id}/namedViews"
        return self._make_request('GET', endpoint)
    
    # ===== MODIFICATION OPERATIONS =====
    
    def create_fillet(self, document_id: str, workspace_id: str, part_studio_id: str,
                     edge_queries: List[str], radius: float) -> Dict[str, Any]:
        """Create a fillet feature"""
        feature_data = {
            "btType": "BTFeatureDefinitionCall-1406",
            "feature": {
                "btType": "BTMFeature-134",
                "featureType": "fillet",
                "name": f"Fillet {radius} mm",
                "parameters": [
                    {
                        "btType": "BTMParameterQueryList-118",
                        "parameterId": "entities",
                        "queries": [
                            {
                                "btType": "BTMIndividualQuery-138",
                                "query": query,
                                "queryType": "EDGE"
                            } for query in edge_queries
                        ]
                    },
                    {
                        "btType": "BTMParameterQuantity-147",
                        "parameterId": "radius",
                        "expression": f"{radius} mm",
                        "isInteger": False
                    }
                ],
                "suppressed": False,
                "returnAfterSubfeatures": False
            }
        }
        return self.create_feature(document_id, workspace_id, part_studio_id, feature_data)
    
    def create_chamfer(self, document_id: str, workspace_id: str, part_studio_id: str,
                      edge_queries: List[str], distance: float) -> Dict[str, Any]:
        """Create a chamfer feature"""
        feature_data = {
            "btType": "BTFeatureDefinitionCall-1406",
            "feature": {
                "btType": "BTMFeature-134",
                "featureType": "chamfer",
                "name": f"Chamfer {distance} mm",
                "parameters": [
                    {
                        "btType": "BTMParameterQueryList-118",
                        "parameterId": "entities",
                        "queries": [
                            {
                                "btType": "BTMIndividualQuery-138",
                                "query": query,
                                "queryType": "EDGE"
                            } for query in edge_queries
                        ]
                    },
                    {
                        "btType": "BTMParameterQuantity-147",
                        "parameterId": "distance",
                        "expression": f"{distance} mm",
                        "isInteger": False
                    }
                ],
                "suppressed": False,
                "returnAfterSubfeatures": False
            }
        }
        return self.create_feature(document_id, workspace_id, part_studio_id, feature_data)
    
    # ===== TEST METHOD =====
    
    def test_connection(self) -> bool:
        """Test if we can connect to Onshape API"""
        try:
            # Try to get documents - this should work if auth is correct
            result = self._make_request('GET', '/api/documents')
            print(f"✅ Connection successful! Found {len(result)} documents")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False 