#!/usr/bin/env python3
"""
SHIP GENERATION LOGIC - ISOLATED MODULE
High-performance spaceship generation with caching and optimization
"""

import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from pathlib import Path
import json

class ShipComponentType(Enum):
    """Enumeration of ship component types"""
    HULL = "hull"
    ENGINE = "engine" 
    WEAPON = "weapon"
    SENSOR = "sensor"
    CARGO = "cargo"
    BRIDGE = "bridge"

@dataclass
class ComponentConfig:
    """Configuration for ship components"""
    comp_type: ShipComponentType
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    enabled: bool = True
    material_id: int = 0

class MeshCache:
    """High-performance mesh caching system"""
    
    def __init__(self, max_size: int = 100):
        self._cache = {}
        self._access_order = []
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _get_key(self, mesh_type: str, **params) -> str:
        """Generate cache key from parameters"""
        sorted_params = sorted(params.items())
        return f"{mesh_type}:{hash(frozenset(sorted_params))}"
    
    def get(self, mesh_type: str, **params) -> Optional[trimesh.Trimesh]:
        """Get mesh from cache"""
        key = self._get_key(mesh_type, **params)
        
        if key in self._cache:
            self.hits += 1
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key].copy()
        
        self.misses += 1
        return None
    
    def put(self, mesh_type: str, mesh: trimesh.Trimesh, **params):
        """Store mesh in cache"""
        key = self._get_key(mesh_type, **params)
        
        # Remove oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = mesh.copy()
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / max(1, total)
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }

class PrimitiveGenerator:
    """Optimized primitive mesh generation"""
    
    def __init__(self):
        self.cache = MeshCache()
    
    def create_primitive(self, mesh_type: str, **params) -> trimesh.Trimesh:
        """Create optimized primitive with caching"""
        # Check cache first
        cached_mesh = self.cache.get(mesh_type, **params)
        if cached_mesh is not None:
            return cached_mesh
        
        # Generate new mesh
        mesh = self._generate_primitive(mesh_type, **params)
        
        # Cache the result
        self.cache.put(mesh_type, mesh, **params)
        
        return mesh
    
    def _generate_primitive(self, mesh_type: str, **params) -> trimesh.Trimesh:
        """Generate primitive mesh"""
        try:
            if mesh_type == "cylinder":
                return trimesh.primitives.Cylinder(
                    radius=params.get('radius', 1.0),
                    height=params.get('height', 2.0),
                    sections=params.get('sections', 8)
                )
            elif mesh_type == "box":
                extents = params.get('extents', [2.0, 2.0, 2.0])
                return trimesh.primitives.Box(extents=extents)
            elif mesh_type == "sphere":
                return trimesh.primitives.Sphere(
                    radius=params.get('radius', 1.0),
                    subdivisions=params.get('subdivisions', 2)
                )
            elif mesh_type == "cone":
                return trimesh.primitives.Cone(
                    radius=params.get('radius', 1.0),
                    height=params.get('height', 2.0),
                    sections=params.get('sections', 8)
                )
            else:
                # Fallback to box
                return trimesh.primitives.Box(extents=[1.0, 1.0, 1.0])
        except Exception as e:
            print(f"Primitive generation error: {e}")
            # Always return valid mesh
            return trimesh.primitives.Box(extents=[1.0, 1.0, 1.0])
    
    def clear_cache(self):
        """Clear primitive cache"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return self.cache.get_stats()

class ShipArchitecture:
    """Ship design templates and patterns"""
    
    @staticmethod
    def get_fighter_template() -> List[ComponentConfig]:
        """Fast, agile fighter ship template"""
        return [
            ComponentConfig(ShipComponentType.HULL, (0, 0, 0), (1.5, 0.5, 3.0)),
            ComponentConfig(ShipComponentType.ENGINE, (0, -0.3, -2.0), (0.4, 0.4, 1.0)),
            ComponentConfig(ShipComponentType.WEAPON, (0.5, 0, 1.0), (0.2, 0.2, 0.5)),
            ComponentConfig(ShipComponentType.WEAPON, (-0.5, 0, 1.0), (0.2, 0.2, 0.5)),
            ComponentConfig(ShipComponentType.BRIDGE, (0, 0.3, 0.5), (0.6, 0.3, 0.6)),
        ]
    
    @staticmethod
    def get_cruiser_template() -> List[ComponentConfig]:
        """Balanced multi-role cruiser template"""
        return [
            ComponentConfig(ShipComponentType.HULL, (0, 0, 0), (2.0, 1.0, 4.0)),
            ComponentConfig(ShipComponentType.ENGINE, (0, -0.5, -3.0), (0.8, 0.8, 1.5)),
            ComponentConfig(ShipComponentType.WEAPON, (1.0, 0, 1.0), (0.3, 0.3, 0.8)),
            ComponentConfig(ShipComponentType.WEAPON, (-1.0, 0, 1.0), (0.3, 0.3, 0.8)),
            ComponentConfig(ShipComponentType.CARGO, (0, -0.2, -1.0), (1.2, 0.6, 1.5)),
            ComponentConfig(ShipComponentType.BRIDGE, (0, 0.8, 1.0), (0.8, 0.4, 0.8)),
            ComponentConfig(ShipComponentType.SENSOR, (0, 0.5, 2.5), (0.3, 0.3, 0.3)),
        ]
    
    @staticmethod
    def get_capital_template() -> List[ComponentConfig]:
        """Heavy capital ship template"""
        return [
            ComponentConfig(ShipComponentType.HULL, (0, 0, 0), (3.0, 1.5, 6.0)),
            ComponentConfig(ShipComponentType.ENGINE, (0, -1.0, -4.0), (1.2, 1.2, 2.0)),
            ComponentConfig(ShipComponentType.WEAPON, (2.0, 0, 2.0), (0.5, 0.5, 1.0)),
            ComponentConfig(ShipComponentType.WEAPON, (-2.0, 0, 2.0), (0.5, 0.5, 1.0)),
            ComponentConfig(ShipComponentType.WEAPON, (0, 1.0, 0), (0.4, 0.4, 0.8)),
            ComponentConfig(ShipComponentType.CARGO, (0, -0.3, -2.0), (2.0, 1.0, 2.5)),
            ComponentConfig(ShipComponentType.BRIDGE, (0, 1.2, 2.0), (1.0, 0.6, 1.0)),
            ComponentConfig(ShipComponentType.SENSOR, (0, 0.8, 4.0), (0.4, 0.4, 0.4)),
        ]
    
    @staticmethod
    def get_custom_template(components_count: int = 5) -> List[ComponentConfig]:
        """Generate custom template with specified component count"""
        # Always start with hull
        template = [ComponentConfig(ShipComponentType.HULL, (0, 0, 0), (2.0, 1.0, 3.0))]
        
        # Add components up to desired count
        component_types = [ShipComponentType.ENGINE, ShipComponentType.WEAPON, 
                          ShipComponentType.BRIDGE, ShipComponentType.SENSOR, ShipComponentType.CARGO]
        
        for i in range(min(components_count - 1, len(component_types))):
            comp_type = component_types[i]
            # Generate random position and scale
            pos = (np.random.uniform(-2, 2), np.random.uniform(-1, 1), np.random.uniform(-3, 3))
            scale = (np.random.uniform(0.3, 1.0), np.random.uniform(0.3, 1.0), np.random.uniform(0.5, 1.5))
            template.append(ComponentConfig(comp_type, pos, scale))
        
        return template

class ShipGenerator:
    """High-performance ship generation engine"""
    
    def __init__(self):
        self.primitive_gen = PrimitiveGenerator()
        self.component_materials = {
            ShipComponentType.HULL: [0.6, 0.6, 0.7, 1.0],
            ShipComponentType.ENGINE: [1.0, 0.3, 0.3, 1.0], 
            ShipComponentType.WEAPON: [0.8, 0.8, 0.2, 1.0],
            ShipComponentType.SENSOR: [0.2, 0.8, 0.2, 1.0],
            ShipComponentType.CARGO: [0.5, 0.3, 0.1, 1.0],
            ShipComponentType.BRIDGE: [0.9, 0.9, 0.9, 1.0],
        }
        self.generation_stats = {
            'ships_generated': 0,
            'total_generation_time': 0.0,
            'average_generation_time': 0.0
        }
    
    def generate_component_mesh(self, config: ComponentConfig) -> Optional[trimesh.Trimesh]:
        """Generate mesh for a single component"""
        if not config.enabled:
            return None
        
        # Component type to primitive mapping
        type_mapping = {
            ShipComponentType.HULL: ("box", {"extents": [config.scale[0]*2, config.scale[1]*2, config.scale[2]*2]}),
            ShipComponentType.ENGINE: ("cylinder", {"radius": config.scale[0], "height": config.scale[2]*2, "sections": 6}),
            ShipComponentType.WEAPON: ("cylinder", {"radius": config.scale[0]*0.5, "height": config.scale[2]*2, "sections": 6}),
            ShipComponentType.SENSOR: ("sphere", {"radius": config.scale[0], "subdivisions": 1}),
            ShipComponentType.CARGO: ("box", {"extents": [config.scale[0]*2, config.scale[1]*2, config.scale[2]*2]}),
            ShipComponentType.BRIDGE: ("box", {"extents": [config.scale[0]*2, config.scale[1]*2, config.scale[2]*2]}),
        }
        
        mesh_type, params = type_mapping.get(config.comp_type, ("box", {"extents": [1.0, 1.0, 1.0]}))
        mesh = self.primitive_gen.create_primitive(mesh_type, **params)
        
        # Apply transformations
        if any(config.rotation):
            mesh = mesh.apply_transform(trimesh.transformations.euler_matrix(*config.rotation))
        
        if config.position != (0, 0, 0):
            mesh = mesh.apply_translation(config.position)
        
        # Set material color
        if hasattr(mesh.visual, 'face_colors'):
            color = self.component_materials.get(config.comp_type, [0.5, 0.5, 0.5, 1.0])
            mesh.visual.face_colors = np.tile(color, (len(mesh.faces), 1))
        
        return mesh
    
    def generate_ship_from_template(self, template: List[ComponentConfig]) -> Dict[str, Any]:
        """Generate complete ship from component template"""
        start_time = time.time()
        
        # Generate individual component meshes
        components = []
        total_vertices = 0
        total_faces = 0
        
        for config in template:
            mesh = self.generate_component_mesh(config)
            if mesh is not None:
                components.append(mesh)
                total_vertices += len(mesh.vertices)
                total_faces += len(mesh.faces)
        
        # Combine all components into single mesh
        if components:
            try:
                combined_mesh = trimesh.util.concatenate(components)
            except Exception as e:
                print(f"Mesh combination failed: {e}, using fallback")
                # Fallback to simple box
                combined_mesh = trimesh.primitives.Box(extents=[2, 1, 3])
                total_vertices = len(combined_mesh.vertices)
                total_faces = len(combined_mesh.faces)
        else:
            combined_mesh = trimesh.primitives.Box(extents=[2, 1, 3])
            total_vertices = len(combined_mesh.vertices)
            total_faces = len(combined_mesh.faces)
        
        generation_time = time.time() - start_time
        
        # Update statistics
        self.generation_stats['ships_generated'] += 1
        self.generation_stats['total_generation_time'] += generation_time
        self.generation_stats['average_generation_time'] = (
            self.generation_stats['total_generation_time'] / 
            self.generation_stats['ships_generated']
        )
        
        return {
            'mesh': combined_mesh,
            'vertices': total_vertices,
            'faces': total_faces,
            'generation_time': generation_time,
            'components': len(template),
            'template': template,
            'cache_stats': self.primitive_gen.get_cache_stats()
        }
    
    def generate_ship_by_class(self, ship_class: str = "cruiser", randomize: bool = True) -> Dict[str, Any]:
        """Generate ship of specified class"""
        templates = {
            "fighter": ShipArchitecture.get_fighter_template,
            "cruiser": ShipArchitecture.get_cruiser_template,
            "capital": ShipArchitecture.get_capital_template
        }
        
        template_func = templates.get(ship_class, ShipArchitecture.get_cruiser_template)
        template = template_func()
        
        # Add randomization if requested
        if randomize:
            for config in template:
                if np.random.random() > 0.1:  # 90% chance to keep component
                    # Add small random variations
                    scale_variation = np.random.uniform(0.8, 1.2, 3)
                    config.scale = tuple(s * v for s, v in zip(config.scale, scale_variation))
        
        return self.generate_ship_from_template(template)
    
    def generate_custom_ship(self, components_count: int = 5) -> Dict[str, Any]:
        """Generate custom ship with specified component count"""
        template = ShipArchitecture.get_custom_template(components_count)
        return self.generate_ship_from_template(template)
    
    def export_ship(self, ship_data: Dict[str, Any], filepath: Path, format: str = "stl") -> bool:
        """Export ship mesh to file"""
        try:
            mesh = ship_data['mesh']
            format_lower = format.lower()
            
            if format_lower == "stl":
                mesh.export(str(filepath.with_suffix('.stl')))
            elif format_lower == "obj":
                mesh.export(str(filepath.with_suffix('.obj')))
            elif format_lower == "glb":
                mesh.export(str(filepath.with_suffix('.glb')))
            elif format_lower == "ply":
                mesh.export(str(filepath.with_suffix('.ply')))
            else:
                # Default to STL
                mesh.export(str(filepath.with_suffix('.stl')))
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        cache_stats = self.primitive_gen.get_cache_stats()
        return {
            'generation_stats': self.generation_stats,
            'cache_performance': cache_stats,
            'memory_usage': {
                'cached_primitives': cache_stats['size']
            }
        }
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        self.primitive_gen.clear_cache()

class ShipConfiguration:
    """Ship configuration management"""
    
    @staticmethod
    def save_ship_config(ship_data: Dict[str, Any], filepath: Path) -> bool:
        """Save ship configuration to JSON file"""
        try:
            config = {
                'template': [
                    {
                        'type': comp.comp_type.value,
                        'position': comp.position,
                        'scale': comp.scale,
                        'rotation': comp.rotation,
                        'enabled': comp.enabled,
                        'material_id': comp.material_id
                    }
                    for comp in ship_data.get('template', [])
                ],
                'metadata': {
                    'vertices': ship_data.get('vertices', 0),
                    'faces': ship_data.get('faces', 0),
                    'generation_time': ship_data.get('generation_time', 0.0),
                    'components': ship_data.get('components', 0)
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Config save failed: {e}")
            return False
    
    @staticmethod
    def load_ship_config(filepath: Path) -> Optional[List[ComponentConfig]]:
        """Load ship configuration from JSON file"""
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            template = []
            for comp_data in config.get('template', []):
                comp_type = ShipComponentType(comp_data['type'])
                template.append(ComponentConfig(
                    comp_type=comp_type,
                    position=tuple(comp_data['position']),
                    scale=tuple(comp_data['scale']),
                    rotation=tuple(comp_data['rotation']),
                    enabled=comp_data['enabled'],
                    material_id=comp_data['material_id']
                ))
            
            return template
        except Exception as e:
            print(f"Config load failed: {e}")
            return None

# Factory functions for easy instantiation
def create_ship_generator() -> ShipGenerator:
    """Create ship generator instance"""
    return ShipGenerator()

def create_primitive_generator() -> PrimitiveGenerator:
    """Create primitive generator instance"""
    return PrimitiveGenerator()

if __name__ == "__main__":
    # Demo usage
    print("🚀 SHIP GENERATION LOGIC - ISOLATED MODULE TEST")
    print("=" * 50)
    
    # Create generator
    generator = create_ship_generator()
    
    # Test different ship classes
    for ship_class in ["fighter", "cruiser", "capital"]:
        ship_data = generator.generate_ship_by_class(ship_class)
        print(f"✅ {ship_class.title()}: {ship_data['vertices']} vertices, {ship_data['faces']} faces")
        print(f"   Generation time: {ship_data['generation_time']:.4f}s")
    
    # Performance report
    report = generator.get_performance_report()
    print(f"\n📊 Cache hit rate: {report['cache_performance']['hit_rate']:.1%}")
    print(f"⚡ Average generation: {report['generation_stats']['average_generation_time']:.4f}s")