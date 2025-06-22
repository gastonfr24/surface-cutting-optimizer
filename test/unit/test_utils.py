"""
Unit tests for Surface Cutting Optimizer utils modules

Tests cover:
- Metrics calculation (efficiency, waste, reports)
- Logging functionality (custom logger, timing, operations)
- Visualization utilities (plotting, saving)
- Export functions (PDF, SVG, CSV, DXF)
- Dependency management
- Integration between utils modules
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import os
import tempfile
import json
from datetime import datetime
from io import StringIO
import logging

# Import modules directly to avoid circular imports
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from surface_optimizer.core.models import (
    Stock, Order, CuttingResult, PlacedShape,
    MaterialType, Priority
)
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.utils.metrics import (
    calculate_efficiency, calculate_waste, generate_metrics_report
)
from surface_optimizer.utils.logging import (
    OptimizationLogger, setup_logging, get_logger, 
    log_info, log_debug, log_warning, log_error, timed_operation
)
from surface_optimizer.utils.export import (
    export_to_pdf, export_to_svg, export_cutting_list, export_to_dxf
)


class TestMetricsCalculation(unittest.TestCase):
    """Tests for metrics calculation utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0, cost_per_unit=100.0),  # Area: 500,000
            Stock(id="S2", width=800.0, height=600.0, cost_per_unit=120.0)    # Area: 480,000
        ]
        
        self.orders = [
            Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2),  # Total area: 40,000
            Order(id="O2", shape=Rectangle(300.0, 150.0), quantity=1),  # Total area: 45,000
        ]
        
        self.result = CuttingResult()
        self.result.algorithm_used = "TestAlgorithm"
        self.result.computation_time = 0.5
        self.result.total_stock_used = 2
        self.result.total_orders_fulfilled = 2
        
        # Create placed shapes
        self.result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(200.0, 100.0), stock_id="S1"),
            PlacedShape(order_id="O1", shape=Rectangle(200.0, 100.0), stock_id="S1"),
            PlacedShape(order_id="O2", shape=Rectangle(300.0, 150.0), stock_id="S2")
        ]
        
        self.result.unfulfilled_orders = []
        
    def test_calculate_efficiency_basic(self):
        """Test basic efficiency calculation"""
        efficiency = calculate_efficiency(self.result, self.stocks)
        
        # Total placed area: 40,000 + 45,000 = 85,000
        # Total stock area: 500,000 + 480,000 = 980,000
        # Expected efficiency: ~8.7%
        self.assertGreater(efficiency, 8.0)
        self.assertLess(efficiency, 10.0)
        
    def test_calculate_efficiency_empty_result(self):
        """Test efficiency calculation with no placed shapes"""
        empty_result = CuttingResult()
        empty_result.placed_shapes = []
        
        efficiency = calculate_efficiency(empty_result, self.stocks)
        self.assertEqual(efficiency, 0.0)
        
    def test_calculate_efficiency_no_stocks(self):
        """Test efficiency calculation with no stocks"""
        efficiency = calculate_efficiency(self.result, [])
        self.assertEqual(efficiency, 0.0)
        
    def test_calculate_waste_basic(self):
        """Test basic waste calculation"""
        waste = calculate_waste(self.result, self.stocks)
        
        # Total stock area: 980,000
        # Total placed area: 85,000
        # Expected waste: 895,000
        self.assertGreater(waste, 890000)
        self.assertLess(waste, 900000)
        
    def test_calculate_waste_empty_result(self):
        """Test waste calculation with no placed shapes"""
        empty_result = CuttingResult()
        empty_result.placed_shapes = []
        
        waste = calculate_waste(empty_result, self.stocks)
        self.assertEqual(waste, 0.0)
        
    def test_calculate_waste_perfect_efficiency(self):
        """Test waste calculation with perfect efficiency"""
        # Create result that uses exact stock area
        perfect_result = CuttingResult()
        perfect_result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(1000.0, 500.0), stock_id="S1")
        ]
        
        waste = calculate_waste(perfect_result, [self.stocks[0]])
        self.assertEqual(waste, 0.0)
        
    def test_generate_metrics_report_complete(self):
        """Test comprehensive metrics report generation"""
        report = generate_metrics_report(self.result, self.stocks, self.orders)
        
        # Check all expected keys are present
        expected_keys = [
            "material_efficiency_percentage", "waste_area", "waste_percentage",
            "order_fulfillment_rate", "total_placed_area", "total_stock_area",
            "total_order_area", "stocks_used", "orders_fulfilled", 
            "orders_unfulfilled", "total_cost", "cost_per_area",
            "algorithm_used", "computation_time"
        ]
        
        for key in expected_keys:
            self.assertIn(key, report)
            
        # Check specific values
        self.assertEqual(report["algorithm_used"], "TestAlgorithm")
        self.assertEqual(report["computation_time"], 0.5)
        self.assertEqual(report["stocks_used"], 2)
        self.assertEqual(report["orders_fulfilled"], 2)
        self.assertEqual(report["orders_unfulfilled"], 0)
        self.assertEqual(report["order_fulfillment_rate"], 100.0)
        
        # Check cost calculations
        self.assertEqual(report["total_cost"], 220.0)  # 100 + 120
        self.assertGreater(report["cost_per_area"], 0)
        
    def test_generate_metrics_report_no_orders(self):
        """Test metrics report with no orders"""
        report = generate_metrics_report(self.result, self.stocks, [])
        
        self.assertEqual(report["order_fulfillment_rate"], 0.0)
        self.assertGreater(report["total_placed_area"], 0)
        
    def test_generate_metrics_report_unfulfilled_orders(self):
        """Test metrics report with unfulfilled orders"""
        self.result.unfulfilled_orders = ["O3", "O4"]
        self.result.total_orders_fulfilled = 2
        
        report = generate_metrics_report(self.result, self.stocks, self.orders + [
            Order(id="O3", shape=Rectangle(100.0, 100.0)),
            Order(id="O4", shape=Rectangle(100.0, 100.0))
        ])
        
        self.assertEqual(report["orders_unfulfilled"], 2)
        self.assertEqual(report["order_fulfillment_rate"], 50.0)  # 2/4 = 50%
        
    def test_efficiency_edge_cases(self):
        """Test efficiency calculation edge cases"""
        # Test with very small areas
        tiny_result = CuttingResult()
        tiny_result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(0.1, 0.1), stock_id="S1")
        ]
        
        efficiency = calculate_efficiency(tiny_result, self.stocks)
        self.assertGreater(efficiency, 0.0)
        self.assertLess(efficiency, 0.1)
        
        # Test with identical stock and shape areas
        exact_result = CuttingResult()
        exact_result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(1000.0, 500.0), stock_id="S1")
        ]
        
        efficiency = calculate_efficiency(exact_result, [self.stocks[0]])
        self.assertEqual(efficiency, 100.0)


class TestOptimizationLogger(unittest.TestCase):
    """Tests for custom optimization logger"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create logger with file logging disabled for testing
        self.logger = OptimizationLogger(
            name="test_logger", 
            level=logging.DEBUG,
            enable_file_logging=False
        )
        
        # Capture log output
        self.log_capture = StringIO()
        handler = logging.StreamHandler(self.log_capture)
        handler.setLevel(logging.DEBUG)
        self.logger.logger.handlers = [handler]  # Replace handlers
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clear any remaining operation timers
        self.logger.start_times.clear()
        self.logger.operation_logs.clear()
        
    def test_logger_initialization(self):
        """Test logger initialization"""
        self.assertIsInstance(self.logger, OptimizationLogger)
        self.assertEqual(self.logger.logger.name, "test_logger")
        self.assertEqual(self.logger.logger.level, logging.DEBUG)
        self.assertFalse(self.logger.enable_file_logging)
        
    def test_basic_logging_methods(self):
        """Test basic logging methods"""
        self.logger.info("Test info message")
        self.logger.debug("Test debug message")
        self.logger.warning("Test warning message")
        self.logger.error("Test error message")
        
        log_output = self.log_capture.getvalue()
        self.assertIn("Test info message", log_output)
        self.assertIn("Test debug message", log_output)
        self.assertIn("Test warning message", log_output)
        self.assertIn("Test error message", log_output)
        
    def test_operation_timing(self):
        """Test operation timing functionality"""
        operation_name = "test_operation"
        
        # Start operation
        self.logger.start_operation(operation_name, {"param1": "value1"})
        self.assertIn(operation_name, self.logger.start_times)
        
        # Small delay to ensure measurable time
        import time
        time.sleep(0.01)
        
        # End operation
        self.logger.end_operation(operation_name, success=True, 
                                result={"result1": "value1"})
        self.assertNotIn(operation_name, self.logger.start_times)
        
        # Check operation logs
        self.assertEqual(len(self.logger.operation_logs), 2)
        start_log = self.logger.operation_logs[0]
        end_log = self.logger.operation_logs[1]
        
        self.assertEqual(start_log["operation"], operation_name)
        self.assertEqual(start_log["status"], "started")
        self.assertEqual(end_log["operation"], operation_name)
        self.assertEqual(end_log["status"], "completed")
        self.assertGreater(end_log["duration_seconds"], 0)
        
    def test_operation_failure_logging(self):
        """Test logging of failed operations"""
        operation_name = "failed_operation"
        
        self.logger.start_operation(operation_name)
        self.logger.end_operation(operation_name, success=False)
        
        end_log = self.logger.operation_logs[-1]
        self.assertEqual(end_log["status"], "failed")
        
    def test_validation_logging(self):
        """Test validation logging"""
        # Successful validation
        self.logger.log_validation("stocks", 5)
        log_output = self.log_capture.getvalue()
        self.assertIn("Validation passed: 5 stocks", log_output)
        
        # Clear buffer
        self.log_capture.truncate(0)
        self.log_capture.seek(0)
        
        # Failed validation
        issues = ["Issue 1", "Issue 2"]
        self.logger.log_validation("orders", 3, issues)
        log_output = self.log_capture.getvalue()
        self.assertIn("Validation issues for orders: 2 problems", log_output)
        self.assertIn("Issue 1", log_output)
        self.assertIn("Issue 2", log_output)
        
    def test_algorithm_logging(self):
        """Test algorithm-specific logging"""
        # Algorithm start
        self.logger.log_algorithm_start("TestAlgorithm", 5, 10)
        log_output = self.log_capture.getvalue()
        self.assertIn("Algorithm: TestAlgorithm", log_output)
        self.assertIn("Stocks: 5", log_output)
        self.assertIn("Orders: 10", log_output)
        
        # Clear buffer
        self.log_capture.truncate(0)
        self.log_capture.seek(0)
        
        # Algorithm results
        result_summary = {
            "stocks_used": 3,
            "orders_fulfilled": 8,
            "efficiency": 85.5,
            "computation_time": 1.234
        }
        self.logger.log_algorithm_result(result_summary)
        log_output = self.log_capture.getvalue()
        self.assertIn("Optimization Results:", log_output)
        self.assertIn("Stocks used: 3", log_output)
        self.assertIn("Orders fulfilled: 8", log_output)
        self.assertIn("Efficiency: 85.5%", log_output)
        self.assertIn("Computation time: 1.234s", log_output)
        
    def test_placement_logging(self):
        """Test shape placement logging"""
        self.logger.log_placement("O1_1", "S1", (100, 50))
        self.logger.log_placement_failure("O2_1", "No space available")
        
        log_output = self.log_capture.getvalue()
        self.assertIn("Placed O1_1 on S1 at (100, 50)", log_output)
        self.assertIn("Failed to place O2_1: No space available", log_output)
        
    def test_demo_logging_methods(self):
        """Test demo-specific logging methods"""
        self.logger.demo_section("Demo Section", "=")
        self.logger.demo_step(1, "Step Title")
        self.logger.demo_success("Success message")
        self.logger.demo_warning("Warning message")
        self.logger.demo_info("Info message")
        self.logger.demo_result(85.5, 8, 10)
        
        log_output = self.log_capture.getvalue()
        self.assertIn("Demo Section", log_output)
        self.assertIn("STEP 1: Step Title", log_output)
        self.assertIn("Success message", log_output)
        self.assertIn("Warning message", log_output)
        self.assertIn("Info message", log_output)
        self.assertIn("85.5%", log_output)
        
    def test_export_logs(self):
        """Test log export functionality"""
        # Add some operations
        self.logger.start_operation("op1")
        self.logger.end_operation("op1")
        
        # Use a temporary file path instead of NamedTemporaryFile to avoid Windows permission issues
        import tempfile
        import uuid
        temp_path = os.path.join(tempfile.gettempdir(), f"test_logs_{uuid.uuid4().hex}.json")
        
        try:
            self.logger.export_logs(temp_path)
            
            # Read back the exported logs
            with open(temp_path, 'r') as f:
                exported_logs = json.load(f)
            
            self.assertEqual(len(exported_logs), 2)
            self.assertEqual(exported_logs[0]["operation"], "op1")
            self.assertEqual(exported_logs[0]["status"], "started")
            self.assertEqual(exported_logs[1]["operation"], "op1")
            self.assertEqual(exported_logs[1]["status"], "completed")
            
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass  # Ignore cleanup errors
                
    def test_get_summary(self):
        """Test operation summary generation"""
        # Add some operations with a small delay to ensure measurable time
        import time
        self.logger.start_operation("op1")
        time.sleep(0.001)  # Small delay
        self.logger.end_operation("op1", success=True)
        self.logger.start_operation("op2")
        time.sleep(0.001)  # Small delay
        self.logger.end_operation("op2", success=False)
        
        summary = self.logger.get_summary()
        
        self.assertEqual(summary["total_operations"], 4)  # 2 start + 2 end
        self.assertEqual(summary["completed_operations"], 1)
        self.assertEqual(summary["failed_operations"], 1)
        self.assertGreaterEqual(summary["total_time_seconds"], 0)  # Allow 0 if timing is too fast
        self.assertEqual(summary["success_rate"], 25.0)  # 1/4 = 25%
        
    def test_operation_without_start(self):
        """Test ending operation that wasn't started"""
        self.logger.end_operation("nonexistent_operation")
        
        # Should not crash and should log with 0 duration
        end_log = self.logger.operation_logs[-1]
        self.assertEqual(end_log["duration_seconds"], 0)
        
    def test_multiple_operations_parallel(self):
        """Test multiple overlapping operations"""
        self.logger.start_operation("op1")
        self.logger.start_operation("op2")
        
        self.assertEqual(len(self.logger.start_times), 2)
        
        self.logger.end_operation("op1")
        self.assertEqual(len(self.logger.start_times), 1)
        
        self.logger.end_operation("op2")
        self.assertEqual(len(self.logger.start_times), 0)


class TestExportFunctions(unittest.TestCase):
    """Tests for export utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.result = CuttingResult()
        self.result.algorithm_used = "TestAlgorithm"
        self.result.efficiency_percentage = 85.5
        
        self.stocks = [
            Stock(id="S1", width=1000.0, height=500.0),
            Stock(id="S2", width=800.0, height=600.0)
        ]
        
    @patch('builtins.print')
    def test_export_to_pdf(self, mock_print):
        """Test PDF export function"""
        result = export_to_pdf(self.result, self.stocks, "test.pdf")
        
        self.assertFalse(result)  # Function returns False (not implemented)
        mock_print.assert_called_once_with("PDF export to test.pdf - Feature coming soon!")
        
    @patch('builtins.print')
    def test_export_to_svg(self, mock_print):
        """Test SVG export function"""
        result = export_to_svg(self.result, self.stocks, "test.svg")
        
        self.assertFalse(result)  # Function returns False (not implemented)
        mock_print.assert_called_once_with("SVG export to test.svg - Feature coming soon!")
        
    @patch('builtins.print')
    def test_export_cutting_list(self, mock_print):
        """Test cutting list export function"""
        result = export_cutting_list(self.result, self.stocks, "test.csv")
        
        self.assertFalse(result)  # Function returns False (not implemented)
        mock_print.assert_called_once_with("Cutting list export to test.csv - Feature coming soon!")
        
    @patch('builtins.print')
    def test_export_to_dxf(self, mock_print):
        """Test DXF export function"""
        result = export_to_dxf(self.result, self.stocks, "test.dxf")
        
        self.assertFalse(result)  # Function returns False (not implemented)
        mock_print.assert_called_once_with("DXF export to test.dxf - Feature coming soon!")
        
    def test_export_functions_with_default_filenames(self):
        """Test export functions with default filenames"""
        # Test that default filenames work
        with patch('builtins.print') as mock_print:
            export_to_pdf(self.result, self.stocks)
            mock_print.assert_called_with("PDF export to cutting_plan.pdf - Feature coming soon!")
            
        with patch('builtins.print') as mock_print:
            export_to_svg(self.result, self.stocks)
            mock_print.assert_called_with("SVG export to cutting_plan.svg - Feature coming soon!")
            
        with patch('builtins.print') as mock_print:
            export_cutting_list(self.result, self.stocks)
            mock_print.assert_called_with("Cutting list export to cutting_list.csv - Feature coming soon!")
            
        with patch('builtins.print') as mock_print:
            export_to_dxf(self.result, self.stocks)
            mock_print.assert_called_with("DXF export to cutting_plan.dxf - Feature coming soon!")


class TestUtilsEdgeCases(unittest.TestCase):
    """Tests for edge cases in utils modules"""
    
    def test_metrics_with_very_small_areas(self):
        """Test metrics calculation with very small areas"""
        # Create shapes with very small but valid areas
        small_result = CuttingResult()
        small_result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(0.1, 100.0), stock_id="S1"),
            PlacedShape(order_id="O2", shape=Rectangle(100.0, 0.1), stock_id="S1")
        ]
        
        stocks = [Stock(id="S1", width=1000.0, height=500.0)]
        
        efficiency = calculate_efficiency(small_result, stocks)
        waste = calculate_waste(small_result, stocks)
        
        # Very small efficiency but not zero
        self.assertGreater(efficiency, 0.0)
        self.assertLess(efficiency, 0.1)
        # Almost full stock area as waste
        self.assertGreater(waste, 499900.0)
        self.assertLess(waste, 500000.0)
        
    def test_metrics_with_empty_collections(self):
        """Test metrics with empty stocks/orders/results"""
        empty_result = CuttingResult()
        empty_stocks = []
        empty_orders = []
        
        # Should not crash
        efficiency = calculate_efficiency(empty_result, empty_stocks)
        waste = calculate_waste(empty_result, empty_stocks)
        report = generate_metrics_report(empty_result, empty_stocks, empty_orders)
        
        self.assertEqual(efficiency, 0.0)
        self.assertEqual(waste, 0.0)
        self.assertIsInstance(report, dict)
        
    def test_logger_with_unicode_characters(self):
        """Test logger with unicode characters"""
        logger = OptimizationLogger(enable_file_logging=False)
        
        try:
            logger.info("测试 Unicode: 🔄 ✅ ⚠️")
            logger.demo_section("Sección de Prueba")
            logger.log_validation("tüürk", 5, ["Ümlauts: üöä"])
        except Exception as e:
            self.fail(f"Logger should handle unicode characters: {e}")
            
    def test_logger_with_very_long_messages(self):
        """Test logger with very long messages"""
        logger = OptimizationLogger(enable_file_logging=False)
        
        long_message = "A" * 10000  # 10KB message
        
        try:
            logger.info(long_message)
            logger.start_operation("long_op", {"data": long_message})
            logger.end_operation("long_op", result={"output": long_message})
        except Exception as e:
            self.fail(f"Logger should handle long messages: {e}")


class TestUtilsIntegration(unittest.TestCase):
    """Tests for integration between utils modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stocks = [Stock(id="S1", width=1000.0, height=500.0, cost_per_unit=100.0)]
        self.orders = [Order(id="O1", shape=Rectangle(200.0, 100.0), quantity=2)]
        
        self.result = CuttingResult()
        self.result.algorithm_used = "IntegrationTest"
        self.result.placed_shapes = [
            PlacedShape(order_id="O1", shape=Rectangle(200.0, 100.0), stock_id="S1"),
            PlacedShape(order_id="O1", shape=Rectangle(200.0, 100.0), stock_id="S1")
        ]
        self.result.total_stock_used = 1
        self.result.total_orders_fulfilled = 1
        self.result.computation_time = 0.5
        
    def test_metrics_and_logging_integration(self):
        """Test integration between metrics and logging modules"""
        logger = OptimizationLogger(enable_file_logging=False)
        
        # Calculate metrics
        efficiency = calculate_efficiency(self.result, self.stocks)
        waste = calculate_waste(self.result, self.stocks)
        report = generate_metrics_report(self.result, self.stocks, self.orders)
        
        # Log the results
        logger.log_algorithm_result({
            "efficiency": efficiency,
            "waste": waste,
            "stocks_used": report["stocks_used"],
            "orders_fulfilled": report["orders_fulfilled"],
            "computation_time": report["computation_time"]
        })
        
        # Verify integration worked
        self.assertGreater(efficiency, 0)
        self.assertGreater(waste, 0)
        self.assertIn("algorithm_used", report)
        
    def test_full_workflow_simulation(self):
        """Test a complete workflow using multiple utils modules"""
        logger = OptimizationLogger(enable_file_logging=False)
        
        # Simulate optimization workflow
        logger.start_operation("optimization", {
            "stocks": len(self.stocks),
            "orders": len(self.orders)
        })
        
        # Calculate metrics
        efficiency = calculate_efficiency(self.result, self.stocks)
        report = generate_metrics_report(self.result, self.stocks, self.orders)
        
        # Log results
        logger.log_algorithm_result(report)
        
        # End operation
        logger.end_operation("optimization", success=True, result={
            "efficiency": efficiency,
            "total_time": report["computation_time"]
        })
        
        # Verify complete workflow
        self.assertEqual(len(logger.operation_logs), 2)
        self.assertEqual(logger.operation_logs[0]["status"], "started")
        self.assertEqual(logger.operation_logs[1]["status"], "completed")
        self.assertGreater(logger.operation_logs[1]["duration_seconds"], 0)
        
        # Get summary
        summary = logger.get_summary() 
        self.assertEqual(summary["total_operations"], 2)
        self.assertEqual(summary["completed_operations"], 1)
        self.assertEqual(summary["success_rate"], 50.0)  # 1/2 = 50%


if __name__ == '__main__':
    unittest.main() 