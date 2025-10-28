#!/usr/bin/env python3
"""
OPTIMIZED SPACESHIP GENERATION ENGINE
Modular, high-performance ship generation with efficient algorithms
"""

import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from pathlib import Path

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

class OptimizedMeshGenerator:
    """High-performance mesh generation with caching and optimization"""
    
    def __init__(self):
        self._primitive_cache = {}
        self._mesh_cache = {}
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'generation_time': 0.0
        }
    
    def _get_cache_key(self, mesh_type: str, **params) -> str:
        """Generate cache key for mesh parameters"""
        sorted_params = sorted(params.items())
        return f"{mesh_type}:{hash(frozenset(sorted_params))}"
    
    def create_optimized_primitive(self, mesh_type: str, **params) -> trimesh.Trimesh:
        """Create optimized primitive with caching"""
        cache_key = self._get_cache_key(mesh_type, **params)
        
        if cache_key in self._primitive_cache:
            self.performance_metrics['cache_hits'] += 1
            return self._primitive_cache[cache_key].copy()
        
        self.performance_metrics['cache_misses'] += 1
        start_time = time.time()
        
        # Create primitive based on type
        if mesh_type == "cylinder":
            mesh = trimesh.primitives.Cylinder(
                radius=params.get('radius', 1.0),
                height=params.get('height', 2.0),
                sections=params.get('sections', 8)  # Optimized section count
            )
        elif mesh_type == "box":
            extents = params.get('extents', [2.0, 2.0, 2.0])
            mesh = trimesh.primitives.Box(extents=extents)
        elif mesh_type == "sphere":
            mesh = trimesh.primitives.Sphere(
                radius=params.get('radius', 1.0),
                subdivisions=params.get('subdivisions', 2)  # Optimized subdivision
            )
        elif mesh_type == "cone":
            mesh = trimesh.primitives.Cone(
                radius=params.get('radius', 1.0),
                height=params.get('height', 2.0),
                sections=params.get('sections', 8)
            )
        else:
            # Fallback to box
            mesh = trimesh.primitives.Box(extents=[1.0, 1.0, 1.0])
        
        # Cache the result
        self._primitive_cache[cache_key] = mesh.copy()
        
        generation_time = time.time() - start_time
        self.performance_metrics['generation_time'] += generation_time
        
        return mesh
    
    def clear_cache(self):
        """Clear primitive cache to free memory"""
        self._primitive_cache.clear()
        self._mesh_cache.clear()

class ShipArchitecture:
    """Defines ship architecture patterns and templates"""
    
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

class OptimizedSpaceshipEngine:
    """High-performance spaceship generation engine"""
    
    def __init__(self):
        self.mesh_generator = OptimizedMeshGenerator()
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
        """Generate optimized mesh for a single component"""
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
        mesh = self.mesh_generator.create_optimized_primitive(mesh_type, **params)
        
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
            'cache_performance': self.mesh_generator.performance_metrics.copy()
        }
    
    def generate_random_ship(self, ship_class: str = "cruiser") -> Dict[str, Any]:
        """Generate random ship of specified class"""
        templates = {
            "fighter": ShipArchitecture.get_fighter_template,
            "cruiser": ShipArchitecture.get_cruiser_template,
            "capital": ShipArchitecture.get_capital_template
        }
        
        template_func = templates.get(ship_class, ShipArchitecture.get_cruiser_template)
        template = template_func()
        
        # Add some randomization
        for config in template:
            if np.random.random() > 0.1:  # 90% chance to keep component
                # Add small random variations
                scale_variation = np.random.uniform(0.8, 1.2, 3)
                config.scale = tuple(s * v for s, v in zip(config.scale, scale_variation))
        
        return self.generate_ship_from_template(template)
    
    def export_ship(self, ship_data: Dict[str, Any], filepath: Path, format: str = "stl") -> bool:
        """Export ship mesh to file"""
        try:
            mesh = ship_data['mesh']
            if format.lower() == "stl":
                mesh.export(str(filepath.with_suffix('.stl')))
            elif format.lower() == "obj":
                mesh.export(str(filepath.with_suffix('.obj')))
            elif format.lower() == "glb":
                mesh.export(str(filepath.with_suffix('.glb')))
            else:
                mesh.export(str(filepath.with_suffix('.ply')))
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        mesh_metrics = self.mesh_generator.performance_metrics
        return {
            'generation_stats': self.generation_stats,
            'cache_performance': {
                'hit_rate': mesh_metrics['cache_hits'] / max(1, mesh_metrics['cache_hits'] + mesh_metrics['cache_misses']),
                'total_hits': mesh_metrics['cache_hits'],
                'total_misses': mesh_metrics['cache_misses'],
                'total_generation_time': mesh_metrics['generation_time']
            },
            'memory_usage': {
                'cached_primitives': len(self.mesh_generator._primitive_cache),
                'cached_meshes': len(self.mesh_generator._mesh_cache)
            }
        }
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        self.mesh_generator.clear_cache()

# Factory function for easy instantiation
def create_optimized_ship_engine() -> OptimizedSpaceshipEngine:
    """Create and return optimized ship generation engine"""
    return OptimizedSpaceshipEngine()

if __name__ == "__main__":
    # Demo usage
    engine = create_optimized_ship_engine()
    
    print("🚀 OPTIMIZED SPACESHIP GENERATION ENGINE")
    print("="*50)
    
    # Generate different ship types
    for ship_type in ["fighter", "cruiser", "capital"]:
        ship_data = engine.generate_random_ship(ship_type)
        print(f"✅ {ship_type.title()}: {ship_data['vertices']} vertices, {ship_data['faces']} faces")
        print(f"   Generation time: {ship_data['generation_time']:.4f}s")
    
    # Performance report
    report = engine.get_performance_report()
    print(f"\n📊 Performance: {report['cache_performance']['hit_rate']:.1%} cache hit rate")
    print(f"⚡ Average generation: {report['generation_stats']['average_generation_time']:.4f}s")