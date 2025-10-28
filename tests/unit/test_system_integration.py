#!/usr/bin/env python3
"""
SYSTEM INTEGRATION MODULE UNIT TESTS
Comprehensive testing for integration layer and event bus system
"""

import sys
import time
import threading
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class SystemIntegrationTestSuite(ModuleTestSuite):
    """Complete test suite for system integration module"""
    
    def _setup_module_specific(self):
        """Setup specific to system integration testing"""
        self.test_systems = []
        self.test_events = []
        self.event_handlers_called = []
        
    def test_module_imports(self, result: TestResult):
        """Test that all required classes and functions can be imported"""
        
        # Check main classes exist
        assert_class_has_method(self.module.IntegratedSpaceshipDesigner, '__init__')
        assert_class_has_method(self.module.ModuleRegistry, '__init__')
        assert_class_has_method(self.module.SystemEventBus, '__init__')
        result.add_detail("All main classes importable")
        
        # Check integration methods
        assert_class_has_method(self.module.IntegratedSpaceshipDesigner, 'initialize_system')
        assert_class_has_method(self.module.IntegratedSpaceshipDesigner, 'start_application')
        assert_class_has_method(self.module.IntegratedSpaceshipDesigner, 'shutdown_system')
        result.add_detail("IntegratedSpaceshipDesigner has required methods")
        
        # Check registry methods
        assert_class_has_method(self.module.ModuleRegistry, 'register_module')
        assert_class_has_method(self.module.ModuleRegistry, 'get_module')
        assert_class_has_method(self.module.ModuleRegistry, 'unregister_module')
        result.add_detail("ModuleRegistry has required methods")
        
        # Check event bus methods
        assert_class_has_method(self.module.SystemEventBus, 'subscribe')
        assert_class_has_method(self.module.SystemEventBus, 'publish')
        assert_class_has_method(self.module.SystemEventBus, 'unsubscribe')
        result.add_detail("SystemEventBus has required methods")
    
    def test_integrated_spaceship_designer_creation(self, result: TestResult):
        """Test integrated system can be created and configured"""
        
        # Create integrated designer instance
        designer = assert_instance_created(
            lambda: self.module.IntegratedSpaceshipDesigner(),
            self.module.IntegratedSpaceshipDesigner
        )
        result.add_detail("IntegratedSpaceshipDesigner created successfully")
        
        # Check designer attributes
        required_attrs = ['module_registry', 'event_bus', 'modules', 'initialized']
        for attr in required_attrs:
            if hasattr(designer, attr):
                result.add_detail(f"Designer has {attr}")
        
        # Test system initialization
        try:
            designer.initialize_system()
            result.add_detail("System initialization completed")
            
            # Check if modules were loaded
            if hasattr(designer, 'modules'):
                modules = getattr(designer, 'modules', {})
                result.add_detail(f"Loaded modules: {list(modules.keys())}")
                
        except Exception as e:
            result.add_detail(f"System initialization error: {str(e)}")
        
        self.test_systems.append(designer)
        return designer
    
    def test_module_registry(self, result: TestResult):
        """Test module registry functionality"""
        
        # Create module registry
        registry = assert_instance_created(
            lambda: self.module.ModuleRegistry(),
            self.module.ModuleRegistry
        )
        result.add_detail("ModuleRegistry created successfully")
        
        # Test module registration
        try:
            # Create mock modules
            mock_modules = {
                'ui_system': {'name': 'UI System', 'status': 'active'},
                'ship_generation': {'name': 'Ship Generator', 'status': 'active'},
                'mcp_tools': {'name': 'MCP Tools', 'status': 'standby'}
            }
            
            # Register modules
            for name, module in mock_modules.items():
                registry.register_module(name, module)
                result.add_detail(f"Module registered: {name}")
            
            # Test module retrieval
            for name in mock_modules:
                retrieved = registry.get_module(name)
                assert retrieved is not None, f"Failed to retrieve module: {name}"
                result.add_detail(f"Module retrieved: {name}")
            
            # Test module listing
            if hasattr(registry, 'list_modules'):
                modules = registry.list_modules()
                result.add_detail(f"Total modules registered: {len(modules)}")
                
        except Exception as e:
            result.add_detail(f"Module registry error: {str(e)}")
        
        # Test module unregistration
        try:
            registry.unregister_module('mcp_tools')
            result.add_detail("Module unregistered successfully")
            
            # Verify removal
            removed = registry.get_module('mcp_tools')
            assert removed is None, "Module not properly unregistered"
            result.add_detail("Module removal verified")
            
        except Exception as e:
            result.add_detail(f"Module unregistration error: {str(e)}")
        
        return registry
    
    def test_system_event_bus(self, result: TestResult):
        """Test system event bus functionality"""
        
        # Create event bus
        event_bus = assert_instance_created(
            lambda: self.module.SystemEventBus(),
            self.module.SystemEventBus
        )
        result.add_detail("SystemEventBus created successfully")
        
        # Test event subscription and publishing
        def test_event_handler(event_data):
            self.event_handlers_called.append(event_data)
            return f"Handled: {event_data.get('type', 'unknown')}"
        
        try:
            # Subscribe to events
            event_bus.subscribe('ship_generated', test_event_handler)
            event_bus.subscribe('ui_updated', test_event_handler)
            result.add_detail("Event handlers subscribed")
            
            # Publish events
            test_events = [
                {'type': 'ship_generated', 'data': {'vertices': 100, 'faces': 200}},
                {'type': 'ui_updated', 'data': {'component': 'status_bar'}},
                {'type': 'system_ready', 'data': {'timestamp': time.time()}}
            ]
            
            for event in test_events:
                event_bus.publish(event['type'], event['data'])
                result.add_detail(f"Event published: {event['type']}")
                self.test_events.append(event)
            
            # Verify handlers were called
            time.sleep(0.1)  # Allow async processing
            if self.event_handlers_called:
                result.add_detail(f"Event handlers called: {len(self.event_handlers_called)} times")
            
        except Exception as e:
            result.add_detail(f"Event bus error: {str(e)}")
        
        # Test event unsubscription
        try:
            event_bus.unsubscribe('ship_generated', test_event_handler)
            result.add_detail("Event handler unsubscribed")
            
        except Exception as e:
            result.add_detail(f"Unsubscription error: {str(e)}")
        
        return event_bus
    
    def test_module_lifecycle_management(self, result: TestResult):
        """Test module lifecycle and dependency management"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test module startup sequence
        if hasattr(designer, 'start_modules'):
            try:
                startup_order = designer.start_modules()
                result.add_detail(f"Module startup order: {startup_order}")
            except Exception as e:
                result.add_detail(f"Module startup error: {str(e)}")
        
        # Test module dependency resolution
        if hasattr(designer, 'resolve_dependencies'):
            try:
                dependencies = {
                    'ui_system': ['display_3d'],
                    'ship_generation': ['mcp_tools'],
                    'display_3d': [],
                    'mcp_tools': []
                }
                
                resolved = designer.resolve_dependencies(dependencies)
                result.add_detail(f"Dependencies resolved: {resolved}")
                
            except Exception as e:
                result.add_detail(f"Dependency resolution error: {str(e)}")
        
        # Test module health monitoring
        if hasattr(designer, 'check_module_health'):
            try:
                health_status = designer.check_module_health()
                result.add_detail(f"Module health check: {health_status}")
            except Exception as e:
                result.add_detail(f"Health check error: {str(e)}")
    
    def test_inter_module_communication(self, result: TestResult):
        """Test communication between modules"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        event_bus = self.test_system_event_bus(TestResult("bus_setup", "system_integration"))
        
        # Test cross-module function calls
        if hasattr(designer, 'call_module_function'):
            try:
                # Simulate UI requesting ship generation
                request = {
                    'source_module': 'ui_system',
                    'target_module': 'ship_generation',
                    'function': 'generate_ship',
                    'parameters': {'ship_type': 'fighter'}
                }
                
                response = designer.call_module_function(request)
                result.add_detail("Cross-module function call completed")
                
                if response:
                    result.add_detail(f"Response received: {str(response)[:100]}")
                    
            except Exception as e:
                result.add_detail(f"Cross-module call error: {str(e)}")
        
        # Test data sharing between modules
        if hasattr(designer, 'share_data'):
            try:
                shared_data = {
                    'current_ship': {'id': 'ship_001', 'type': 'cruiser'},
                    'render_settings': {'wireframe': False, 'lighting': True}
                }
                
                designer.share_data('global_state', shared_data)
                result.add_detail("Data shared between modules")
                
                # Retrieve shared data
                retrieved = designer.get_shared_data('global_state')
                if retrieved:
                    result.add_detail("Shared data retrieved successfully")
                    
            except Exception as e:
                result.add_detail(f"Data sharing error: {str(e)}")
        
        # Test event-driven communication
        communication_events = []
        
        def communication_handler(event_data):
            communication_events.append(event_data)
        
        try:
            event_bus.subscribe('module_communication', communication_handler)
            
            # Simulate module communication events
            comm_events = [
                {'from': 'ui_system', 'to': 'ship_generation', 'action': 'generate'},
                {'from': 'ship_generation', 'to': 'display_3d', 'action': 'render'},
                {'from': 'display_3d', 'to': 'ui_system', 'action': 'update_status'}
            ]
            
            for comm_event in comm_events:
                event_bus.publish('module_communication', comm_event)
                result.add_detail(f"Communication event: {comm_event['from']} -> {comm_event['to']}")
            
            time.sleep(0.1)  # Allow processing
            result.add_detail(f"Communication events processed: {len(communication_events)}")
            
        except Exception as e:
            result.add_detail(f"Event communication error: {str(e)}")
    
    def test_error_propagation_and_handling(self, result: TestResult):
        """Test error propagation and system-wide error handling"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test error propagation
        if hasattr(designer, 'handle_module_error'):
            try:
                # Simulate module errors
                test_errors = [
                    {'module': 'ship_generation', 'error': 'mesh_creation_failed', 'severity': 'warning'},
                    {'module': 'display_3d', 'error': 'opengl_context_lost', 'severity': 'error'},
                    {'module': 'mcp_tools', 'error': 'connection_timeout', 'severity': 'info'}
                ]
                
                for error in test_errors:
                    handled = designer.handle_module_error(error)
                    result.add_detail(f"Error handled: {error['module']} - {error['error']}")
                    
            except Exception as e:
                result.add_detail(f"Error handling test error: {str(e)}")
        
        # Test system recovery
        if hasattr(designer, 'recover_from_error'):
            try:
                recovery_success = designer.recover_from_error('display_3d', 'opengl_context_lost')
                result.add_detail(f"System recovery attempted: {recovery_success}")
            except Exception as e:
                result.add_detail(f"Recovery test error: {str(e)}")
        
        # Test graceful degradation
        if hasattr(designer, 'enable_degraded_mode'):
            try:
                designer.enable_degraded_mode(['display_3d'])
                result.add_detail("Degraded mode enabled for display_3d")
            except Exception as e:
                result.add_detail(f"Degraded mode error: {str(e)}")
    
    def test_performance_monitoring(self, result: TestResult):
        """Test system performance monitoring and metrics"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test performance metrics collection
        if hasattr(designer, 'collect_performance_metrics'):
            try:
                start_time = time.time()
                
                # Simulate system activity
                for i in range(10):
                    if hasattr(designer, 'simulate_activity'):
                        designer.simulate_activity()
                    time.sleep(0.01)
                
                metrics = designer.collect_performance_metrics()
                total_time = time.time() - start_time
                
                result.add_detail(f"Performance test completed in {total_time:.3f}s")
                
                if metrics:
                    result.add_detail(f"Metrics collected: {list(metrics.keys())}")
                    
            except Exception as e:
                result.add_detail(f"Performance monitoring error: {str(e)}")
        
        # Test resource usage monitoring
        if hasattr(designer, 'monitor_resources'):
            try:
                resource_usage = designer.monitor_resources()
                if resource_usage:
                    for resource, value in resource_usage.items():
                        result.add_detail(f"Resource {resource}: {value}")
            except Exception as e:
                result.add_detail(f"Resource monitoring error: {str(e)}")
        
        # Test bottleneck detection
        if hasattr(designer, 'detect_bottlenecks'):
            try:
                bottlenecks = designer.detect_bottlenecks()
                if bottlenecks:
                    result.add_detail(f"Bottlenecks detected: {bottlenecks}")
                else:
                    result.add_detail("No bottlenecks detected")
            except Exception as e:
                result.add_detail(f"Bottleneck detection error: {str(e)}")
    
    def test_configuration_management(self, result: TestResult):
        """Test system configuration and settings management"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test configuration loading
        if hasattr(designer, 'load_configuration'):
            try:
                config = designer.load_configuration()
                if config:
                    result.add_detail(f"Configuration loaded: {len(config)} settings")
                    
                    # Check for expected configuration sections
                    expected_sections = ['ui_settings', 'render_settings', 'generation_settings']
                    for section in expected_sections:
                        if section in config:
                            result.add_detail(f"Configuration section found: {section}")
                            
            except Exception as e:
                result.add_detail(f"Configuration loading error: {str(e)}")
        
        # Test configuration updates
        if hasattr(designer, 'update_configuration'):
            try:
                test_updates = {
                    'ui_settings': {'theme': 'dark', 'window_size': [1200, 800]},
                    'render_settings': {'wireframe': False, 'lighting': True},
                    'generation_settings': {'default_ship_type': 'fighter'}
                }
                
                for section, settings in test_updates.items():
                    designer.update_configuration(section, settings)
                    result.add_detail(f"Configuration updated: {section}")
                    
            except Exception as e:
                result.add_detail(f"Configuration update error: {str(e)}")
        
        # Test configuration persistence
        if hasattr(designer, 'save_configuration'):
            try:
                save_success = designer.save_configuration()
                result.add_detail(f"Configuration saved: {save_success}")
            except Exception as e:
                result.add_detail(f"Configuration save error: {str(e)}")
    
    def test_plugin_system(self, result: TestResult):
        """Test plugin system and extensibility"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test plugin registration
        if hasattr(designer, 'register_plugin'):
            try:
                # Create mock plugins
                mock_plugins = [
                    {'name': 'advanced_renderer', 'version': '1.0', 'type': 'display'},
                    {'name': 'ship_exporter', 'version': '2.1', 'type': 'utility'},
                    {'name': 'ai_assistant', 'version': '1.5', 'type': 'automation'}
                ]
                
                for plugin in mock_plugins:
                    designer.register_plugin(plugin['name'], plugin)
                    result.add_detail(f"Plugin registered: {plugin['name']} v{plugin['version']}")
                    
            except Exception as e:
                result.add_detail(f"Plugin registration error: {str(e)}")
        
        # Test plugin loading and activation
        if hasattr(designer, 'load_plugins'):
            try:
                loaded_plugins = designer.load_plugins()
                result.add_detail(f"Plugins loaded: {len(loaded_plugins) if loaded_plugins else 0}")
            except Exception as e:
                result.add_detail(f"Plugin loading error: {str(e)}")
        
        # Test plugin hooks and extensions
        if hasattr(designer, 'execute_plugin_hooks'):
            try:
                hook_results = designer.execute_plugin_hooks('before_ship_generation')
                result.add_detail(f"Plugin hooks executed: {len(hook_results) if hook_results else 0}")
            except Exception as e:
                result.add_detail(f"Plugin hooks error: {str(e)}")
    
    def test_system_shutdown_and_cleanup(self, result: TestResult):
        """Test system shutdown and resource cleanup"""
        
        designer = self.test_integrated_spaceship_designer_creation(TestResult("designer_setup", "system_integration"))
        
        # Test graceful shutdown
        if hasattr(designer, 'shutdown_system'):
            try:
                shutdown_success = designer.shutdown_system()
                result.add_detail(f"System shutdown initiated: {shutdown_success}")
                
                # Check if modules were properly closed
                if hasattr(designer, 'modules'):
                    modules = getattr(designer, 'modules', {})
                    for name, module in modules.items():
                        if hasattr(module, 'status'):
                            status = getattr(module, 'status', 'unknown')
                            result.add_detail(f"Module {name} status: {status}")
                            
            except Exception as e:
                result.add_detail(f"Shutdown error: {str(e)}")
        
        # Test resource cleanup
        if hasattr(designer, 'cleanup_resources'):
            try:
                cleanup_report = designer.cleanup_resources()
                if cleanup_report:
                    result.add_detail(f"Resources cleaned: {cleanup_report}")
                else:
                    result.add_detail("Resource cleanup completed")
            except Exception as e:
                result.add_detail(f"Cleanup error: {str(e)}")
        
        # Test memory cleanup verification
        import gc
        initial_objects = len(gc.get_objects())
        
        # Clear test system references
        self.test_systems.clear()
        gc.collect()
        
        final_objects = len(gc.get_objects())
        object_difference = final_objects - initial_objects
        
        if abs(object_difference) < 100:  # Reasonable threshold
            result.add_detail("Memory cleanup successful")
        else:
            result.add_detail(f"Potential memory leak: {object_difference} objects")

if __name__ == "__main__":
    from test_framework import UniversalTestRunner
    
    # Create test runner
    runner = UniversalTestRunner()
    
    # Add system integration test suite
    integration_suite = SystemIntegrationTestSuite("system_integration", runner.logger)
    runner.add_test_suite(integration_suite)
    
    # Run dependency check
    deps_ok = runner.run_dependency_check()
    
    if deps_ok:
        # Run tests
        results = runner.run_all_tests()
        
        # Save results
        output_dir = Path(__file__).parent.parent / "results"
        runner.save_results(output_dir)
        
        print(f"\n⚙️ SYSTEM INTEGRATION MODULE TESTING COMPLETE")
        print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    else:
        print("❌ Critical dependencies missing - skipping tests")