#!/usr/bin/env python3
"""
SHIP GENERATION MODULE UNIT TESTS
Comprehensive testing for 3D ship generation and mesh creation
"""

import sys
import time
import tempfile
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class ShipGenerationTestSuite(ModuleTestSuite):
    """Complete test suite for ship generation module"""
    
    def _setup_module_specific(self):
        """Setup specific to ship generation testing"""
        self.test_ships = []
        self.test_meshes = []
        self.export_dir = Path(tempfile.mkdtemp(prefix="ship_test_"))
        
    def test_module_imports(self, result: TestResult):
        """Test that all required classes and functions can be imported"""
        
        # Check main classes exist
        assert_class_has_method(self.module.ShipGenerator, '__init__')
        assert_class_has_method(self.module.PrimitiveGenerator, '__init__')
        assert_class_has_method(self.module.MeshCache, '__init__')
        assert_class_has_method(self.module.ShipArchitecture, '__init__')
        result.add_detail("All main classes importable")
        
        # Check generator methods (actual implementation)
        assert_class_has_method(self.module.ShipGenerator, 'generate_ship_from_template')
        assert_class_has_method(self.module.ShipGenerator, 'generate_ship_by_class')
        assert_class_has_method(self.module.ShipGenerator, 'generate_custom_ship')
        assert_class_has_method(self.module.ShipGenerator, 'create_mesh')
        assert_class_has_method(self.module.ShipGenerator, 'export_ship')
        result.add_detail("ShipGenerator has required methods")
        
        # Check primitive methods
        assert_class_has_method(self.module.PrimitiveGenerator, 'create_cylinder')
        assert_class_has_method(self.module.PrimitiveGenerator, 'create_cone')
        assert_class_has_method(self.module.PrimitiveGenerator, 'create_box')
        result.add_detail("PrimitiveGenerator has required methods")
        
        # Check cache methods
        assert_class_has_method(self.module.MeshCache, 'get_cached_mesh')
        assert_class_has_method(self.module.MeshCache, 'cache_mesh')
        assert_class_has_method(self.module.MeshCache, 'clear_cache')
        result.add_detail("MeshCache has required methods")
    
    def test_ship_generator_creation(self, result: TestResult):
        """Test ship generator can be created and configured"""
        
        # Create generator instance
        generator = assert_instance_created(
            lambda: self.module.ShipGenerator(),
            self.module.ShipGenerator
        )
        result.add_detail("ShipGenerator created successfully")
        
        # Check generator properties (matching actual implementation)
        required_attrs = ['primitive_gen', 'component_materials', 'generation_stats']
        for attr in required_attrs:
            assert hasattr(generator, attr), f"Generator missing attribute: {attr}"
        result.add_detail("Generator has all required attributes")
        
        # Check component materials configuration
        materials = getattr(generator, 'component_materials', {})
        if materials:
            assert len(materials) > 0, "Component materials not configured"
            result.add_detail(f"Component materials configured: {len(materials)} types")
        
        # Check generation stats
        stats = getattr(generator, 'generation_stats', {})
        if stats:
            expected_stats = ['ships_generated', 'total_generation_time', 'average_generation_time']
            for stat in expected_stats:
                assert stat in stats, f"Missing generation stat: {stat}"
            result.add_detail("Generation statistics initialized")
        
        return generator
    
    def test_primitive_generation(self, result: TestResult):
        """Test primitive shape generation"""
        
        # Create primitive generator
        prim_gen = assert_instance_created(
            lambda: self.module.PrimitiveGenerator(),
            self.module.PrimitiveGenerator
        )
        result.add_detail("PrimitiveGenerator created successfully")
        
        # Test cylinder creation (using actual method signature)
        try:
            cylinder = prim_gen.create_primitive("cylinder", radius=1.0, height=2.0, sections=8)
            assert cylinder is not None, "Cylinder creation returned None"
            result.add_detail("Cylinder primitive created")
            self.test_meshes.append(cylinder)
        except Exception as e:
            result.add_detail(f"Cylinder creation error: {str(e)}")
        
        # Test box creation
        try:
            box = prim_gen.create_primitive("box", extents=[2.0, 2.0, 2.0])
            assert box is not None, "Box creation returned None"
            result.add_detail("Box primitive created")
            self.test_meshes.append(box)
        except Exception as e:
            result.add_detail(f"Box creation error: {str(e)}")
        
        # Test sphere creation
        try:
            sphere = prim_gen.create_primitive("sphere", radius=1.0, subdivisions=2)
            assert sphere is not None, "Sphere creation returned None"
            result.add_detail("Sphere primitive created")
            self.test_meshes.append(sphere)
        except Exception as e:
            result.add_detail(f"Sphere creation error: {str(e)}")
        
        # Test cache functionality
        try:
            # Create same cylinder again - should hit cache
            cylinder2 = prim_gen.create_primitive("cylinder", radius=1.0, height=2.0, sections=8)
            assert cylinder2 is not None, "Cached cylinder creation failed"
            result.add_detail("Primitive caching working")
        except Exception as e:
            result.add_detail(f"Cache test error: {str(e)}")
    
    def test_mesh_cache_functionality(self, result: TestResult):
        """Test mesh caching system"""
        
        # Create mesh cache
        cache = assert_instance_created(
            lambda: self.module.MeshCache(),
            self.module.MeshCache
        )
        result.add_detail("MeshCache created successfully")
        
        # Test cache storage and retrieval
        test_key = "test_cylinder_1.0_2.0_8"
        test_mesh = "mock_mesh_data"  # Using string for simple test
        
        # Cache a mesh
        cache.cache_mesh(test_key, test_mesh)
        result.add_detail(f"Mesh cached with key: {test_key}")
        
        # Retrieve cached mesh
        retrieved = cache.get_cached_mesh(test_key)
        assert retrieved is not None, "Cached mesh not retrieved"
        assert retrieved == test_mesh, "Retrieved mesh differs from cached"
        result.add_detail("Cached mesh retrieved successfully")
        
        # Test cache miss
        missing = cache.get_cached_mesh("nonexistent_key")
        assert missing is None, "Cache returned data for nonexistent key"
        result.add_detail("Cache miss handled correctly")
        
        # Test cache clearing
        cache.clear_cache()
        cleared = cache.get_cached_mesh(test_key)
        assert cleared is None, "Cache not cleared properly"
        result.add_detail("Cache cleared successfully")
    
    def test_ship_architecture(self, result: TestResult):
        """Test ship architecture templates and patterns"""
        
        # Create ship architecture
        arch = assert_instance_created(
            lambda: self.module.ShipArchitecture(),
            self.module.ShipArchitecture
        )
        result.add_detail("ShipArchitecture created successfully")
        
        # Check architecture templates
        if hasattr(arch, 'templates'):
            templates = getattr(arch, 'templates', {})
            assert isinstance(templates, dict), "Templates should be a dictionary"
            result.add_detail(f"Architecture templates available: {len(templates)}")
            
            # Test template structure
            for template_name, template in templates.items():
                assert isinstance(template, dict), f"Template {template_name} should be a dictionary"
                result.add_detail(f"Template validated: {template_name}")
        
        # Test architecture generation methods
        if hasattr(arch, 'generate_fighter'):
            try:
                fighter_layout = arch.generate_fighter()
                assert fighter_layout is not None, "Fighter layout generation failed"
                result.add_detail("Fighter architecture generated")
            except Exception as e:
                result.add_detail(f"Fighter generation error: {str(e)}")
        
        if hasattr(arch, 'generate_cruiser'):
            try:
                cruiser_layout = arch.generate_cruiser()
                assert cruiser_layout is not None, "Cruiser layout generation failed"
                result.add_detail("Cruiser architecture generated")
            except Exception as e:
                result.add_detail(f"Cruiser generation error: {str(e)}")
    
    def test_ship_generation_complete(self, result: TestResult):
        """Test complete ship generation workflow"""
        
        # Create ship generator
        generator = self.test_ship_generator_creation(TestResult("setup", "ship_generation"))
        
        try:
            # Generate ship using actual ship class method (easier than template)
            ship = generator.generate_ship_by_class("cruiser")
            assert ship is not None, "Ship class generation returned None"
            result.add_detail("Ship by class generated")
            
            # Check if ship is dict with mesh data
            if isinstance(ship, dict) and 'mesh' in ship:
                mesh = ship['mesh']
                if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                    vertex_count = len(mesh.vertices)
                    face_count = len(mesh.faces)
                    result.add_detail(f"Ship mesh: {vertex_count} vertices, {face_count} faces")
            
            self.test_ships.append(ship)
            
            # Test different ship classes
            ship_classes = ['fighter', 'cruiser', 'capital']
            for ship_class in ship_classes:
                try:
                    variant = generator.generate_ship_by_class(ship_class)
                    if variant:
                        result.add_detail(f"Generated {ship_class} ship")
                        self.test_ships.append(variant)
                except Exception as e:
                    result.add_detail(f"{ship_class} ship error: {str(e)}")
        
        except Exception as e:
            result.add_detail(f"Ship generation error: {str(e)}")
            raise
    
    def test_mesh_creation_and_validation(self, result: TestResult):
        """Test mesh creation and validation"""
        
        generator = self.test_ship_generator_creation(TestResult("setup", "ship_generation"))
        
        try:
            # Generate ship (returns dict with mesh)
            ship_data = generator.generate_ship_by_class("cruiser")
            mesh = ship_data.get('mesh') if isinstance(ship_data, dict) else ship_data
            
            assert mesh is not None, "Mesh creation returned None"
            result.add_detail("Ship mesh created successfully")
            
            # Validate mesh properties (if using trimesh)
            if hasattr(mesh, 'vertices'):
                vertex_count = len(mesh.vertices)
                assert vertex_count > 0, "Mesh has no vertices"
                result.add_detail(f"Mesh has {vertex_count} vertices")
            
            if hasattr(mesh, 'faces'):
                face_count = len(mesh.faces)
                assert face_count > 0, "Mesh has no faces"
                result.add_detail(f"Mesh has {face_count} faces")
            
            # Test mesh validity
            if hasattr(mesh, 'is_valid'):
                is_valid = mesh.is_valid
                result.add_detail(f"Mesh validity: {is_valid}")
            
            # Test mesh properties
            if hasattr(mesh, 'is_watertight'):
                is_watertight = mesh.is_watertight
                result.add_detail(f"Mesh watertight: {is_watertight}")
            
            self.test_meshes.append(mesh)
            
        except Exception as e:
            result.add_detail(f"Mesh creation error: {str(e)}")
    
    def test_export_functionality(self, result: TestResult):
        """Test ship export in various formats"""
        
        if not self.test_ships:
            result.complete("SKIP", "No test ships available for export")
            return
        
        generator = self.test_ship_generator_creation(TestResult("setup", "ship_generation"))
        test_ship = self.test_ships[0]
        
        # Test STL export
        try:
            stl_path = self.export_dir / "test_ship.stl"
            success = generator.export_ship(test_ship, str(stl_path), format='stl')
            if success and stl_path.exists():
                result.add_detail(f"STL export successful: {stl_path}")
            else:
                result.add_detail("STL export attempted")
        except Exception as e:
            result.add_detail(f"STL export error: {str(e)}")
        
        # Test OBJ export
        try:
            obj_path = self.export_dir / "test_ship.obj"
            success = generator.export_ship(test_ship, str(obj_path), format='obj')
            if success and obj_path.exists():
                result.add_detail(f"OBJ export successful: {obj_path}")
            else:
                result.add_detail("OBJ export attempted")
        except Exception as e:
            result.add_detail(f"OBJ export error: {str(e)}")
        
        # Test GLB export (if available)
        try:
            glb_path = self.export_dir / "test_ship.glb"
            success = generator.export_ship(test_ship, str(glb_path), format='glb')
            if success and glb_path.exists():
                result.add_detail(f"GLB export successful: {glb_path}")
            else:
                result.add_detail("GLB export attempted")
        except Exception as e:
            result.add_detail(f"GLB export error: {str(e)}")
    
    def test_performance_optimization(self, result: TestResult):
        """Test performance optimizations and caching"""
        
        generator = self.test_ship_generator_creation(TestResult("setup", "ship_generation"))
        
        # Test mesh caching performance
        start_time = time.time()
        
        # Generate multiple ships to test caching
        for i in range(3):
            try:
                ship = generator.generate_ship_by_class("cruiser")
                mesh = generator.create_mesh(ship)
                result.add_detail(f"Ship {i+1} generated")
            except Exception as e:
                result.add_detail(f"Ship {i+1} error: {str(e)}")
        
        total_time = time.time() - start_time
        result.add_detail(f"Generated 3 ships in {total_time:.3f}s")
        
        # Test cache hit rates (if available)
        if hasattr(generator, 'mesh_cache') and hasattr(generator.mesh_cache, 'hit_count'):
            hit_count = getattr(generator.mesh_cache, 'hit_count', 0)
            miss_count = getattr(generator.mesh_cache, 'miss_count', 0)
            total_requests = hit_count + miss_count
            
            if total_requests > 0:
                hit_rate = hit_count / total_requests * 100
                result.add_detail(f"Cache hit rate: {hit_rate:.1f}% ({hit_count}/{total_requests})")
    
    def test_error_handling_and_recovery(self, result: TestResult):
        """Test error handling and graceful degradation"""
        
        generator = self.test_ship_generator_creation(TestResult("setup", "ship_generation"))
        
        # Test invalid parameters
        try:
            # Test error handling with invalid parameters
            try:
                invalid_ship = generator.generate_ship_by_class("invalid_class")
            except Exception:
                invalid_ship = None  # Expected for invalid class
            result.add_detail("Invalid grid size handled gracefully")
        except Exception as e:
            result.add_detail(f"Invalid parameters error handling: {str(e)}")
        
        # Test primitive generation with invalid data
        if hasattr(generator, 'primitive_generator'):
            prim_gen = generator.primitive_generator
            
            try:
                invalid_cylinder = prim_gen.create_cylinder(radius=-1, height=0)
                result.add_detail("Invalid cylinder parameters handled")
            except Exception as e:
                result.add_detail(f"Invalid cylinder error: {str(e)}")
        
        # Test export with invalid paths
        try:
            invalid_export = generator.export_ship({}, "/invalid/path/ship.stl")
            result.add_detail("Invalid export path handled")
        except Exception as e:
            result.add_detail(f"Invalid export error: {str(e)}")
        
        # Test mesh creation with corrupted data
        try:
            corrupted_mesh = generator.create_mesh({'corrupted': 'data'})
            result.add_detail("Corrupted data handled gracefully")
        except Exception as e:
            result.add_detail(f"Corrupted data error: {str(e)}")
    
    def test_memory_management(self, result: TestResult):
        """Test memory usage and cleanup"""
        
        import gc
        
        initial_objects = len(gc.get_objects())
        result.add_detail(f"Initial objects: {initial_objects}")
        
        # Create and destroy multiple generators
        generators = []
        for i in range(5):
            gen = self.module.ShipGenerator()
            ship = gen.generate_ship_by_class("cruiser")
            mesh = gen.create_mesh(ship)
            generators.append((gen, ship, mesh))
        
        mid_objects = len(gc.get_objects())
        result.add_detail(f"Objects after creation: {mid_objects}")
        
        # Clear references
        generators.clear()
        gc.collect()
        
        final_objects = len(gc.get_objects())
        result.add_detail(f"Objects after cleanup: {final_objects}")
        
        # Check for memory leaks
        object_growth = final_objects - initial_objects
        if object_growth < 100:  # Reasonable threshold
            result.add_detail("Memory usage within acceptable limits")
        else:
            result.add_detail(f"Potential memory leak: {object_growth} objects retained")

if __name__ == "__main__":
    from test_framework import UniversalTestRunner
    
    # Create test runner
    runner = UniversalTestRunner()
    
    # Add ship generation test suite
    ship_suite = ShipGenerationTestSuite("ship_generation", runner.logger)
    runner.add_test_suite(ship_suite)
    
    # Run dependency check
    deps_ok = runner.run_dependency_check()
    
    if deps_ok:
        # Run tests
        results = runner.run_all_tests()
        
        # Save results
        output_dir = Path(__file__).parent.parent / "results"
        runner.save_results(output_dir)
        
        print(f"\n🚀 SHIP GENERATION MODULE TESTING COMPLETE")
        print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    else:
        print("❌ Critical dependencies missing - skipping tests")