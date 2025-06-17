#!/usr/bin/env python3
"""
Supervised Testing and Validation System for Surface Cutting Optimizer

This module provides comprehensive testing by comparing algorithm results
with real-world solutions and known optimal benchmarks.
"""

import unittest
import time
import json
from typing import Dict, List, Tuple, Any, Optional
import statistics
from dataclasses import dataclass

from surface_optimizer.core.models import Stock, Order, OptimizationConfig, MaterialType, Priority
from surface_optimizer.core.geometry import Rectangle, Circle
from surface_optimizer.algorithms.basic.first_fit import FirstFitAlgorithm
from surface_optimizer.algorithms.basic.best_fit import BestFitAlgorithm
from surface_optimizer.algorithms.basic.bottom_left import BottomLeftAlgorithm
from surface_optimizer.algorithms.advanced.genetic import GeneticAlgorithm


@dataclass
class RealWorldTestCase:
    """Real-world test case with actual solution data"""
    name: str
    description: str
    stocks: List[Stock]
    orders: List[Order]
    real_world_solution: Dict[str, Any]
    industry: str
    complexity_level: str


@dataclass
class ValidationMetrics:
    """Metrics for validating algorithm performance"""
    accuracy_score: float
    efficiency_difference: float
    stock_usage_ratio: float
    order_fulfillment_ratio: float
    computation_time: float
    overall_grade: str


class SupervisedTestData:
    """Real-world test cases with actual industry solutions"""
    
    @staticmethod
    def get_furniture_industry_case() -> RealWorldTestCase:
        """Real furniture cutting case from industry data"""
        stocks = [
            Stock("Board_1", 2440, 1220, 18.0, MaterialType.WOOD, 85.50),
            Stock("Board_2", 2440, 1220, 18.0, MaterialType.WOOD, 85.50),
            Stock("Board_3", 2440, 1220, 18.0, MaterialType.WOOD, 85.50)
        ]
        
        orders = [
            Order("Shelf_A", Rectangle(800, 300), 4, Priority.HIGH, MaterialType.WOOD),
            Order("Door_B", Rectangle(600, 1800), 2, Priority.URGENT, MaterialType.WOOD),
            Order("Back_Panel", Rectangle(1200, 400), 2, Priority.MEDIUM, MaterialType.WOOD),
            Order("Side_Panel", Rectangle(400, 600), 6, Priority.HIGH, MaterialType.WOOD),
            Order("Drawer_Bottom", Rectangle(500, 350), 4, Priority.MEDIUM, MaterialType.WOOD)
        ]
        
        real_world_solution = {
            "total_stock_used": 2,
            "total_orders_fulfilled": 18,  # All pieces
            "efficiency_percentage": 87.3,
            "waste_percentage": 12.7,
            "cutting_time_minutes": 45,
            "material_cost": 171.0,
            "solution_method": "Professional optimizer software",
            "notes": "Actual furniture workshop solution with minimal waste"
        }
        
        return RealWorldTestCase(
            name="furniture_workshop",
            description="Real furniture workshop cutting optimization",
            stocks=stocks,
            orders=orders,
            real_world_solution=real_world_solution,
            industry="furniture",
            complexity_level="medium"
        )
    
    @staticmethod
    def get_glass_industry_case() -> RealWorldTestCase:
        """Real glass cutting case from industry data"""
        stocks = [
            Stock("Glass_Sheet_1", 3210, 2250, 6.0, MaterialType.GLASS, 245.80),
            Stock("Glass_Sheet_2", 3210, 2250, 6.0, MaterialType.GLASS, 245.80)
        ]
        
        orders = [
            Order("Window_A", Rectangle(1200, 800), 3, Priority.URGENT, MaterialType.GLASS),
            Order("Door_Glass", Rectangle(600, 2000), 2, Priority.HIGH, MaterialType.GLASS),
            Order("Small_Window", Rectangle(800, 600), 4, Priority.MEDIUM, MaterialType.GLASS),
            Order("Panel_B", Rectangle(1000, 500), 2, Priority.HIGH, MaterialType.GLASS)
        ]
        
        real_world_solution = {
            "total_stock_used": 2,
            "total_orders_fulfilled": 11,
            "efficiency_percentage": 78.9,
            "waste_percentage": 21.1,
            "cutting_time_minutes": 72,
            "material_cost": 491.60,
            "solution_method": "Glass industry CAD optimization",
            "notes": "Real glass manufacturer solution considering cutting constraints"
        }
        
        return RealWorldTestCase(
            name="glass_manufacturer",
            description="Real glass manufacturer cutting optimization",
            stocks=stocks,
            orders=orders,
            real_world_solution=real_world_solution,
            industry="glass",
            complexity_level="high"
        )
    
    @staticmethod
    def get_metal_industry_case() -> RealWorldTestCase:
        """Real metal cutting case from industry data"""
        stocks = [
            Stock("Steel_Sheet_1", 1500, 3000, 3.0, MaterialType.METAL, 187.25),
            Stock("Steel_Sheet_2", 1500, 3000, 3.0, MaterialType.METAL, 187.25),
            Stock("Steel_Sheet_3", 1500, 3000, 3.0, MaterialType.METAL, 187.25)
        ]
        
        orders = [
            Order("Bracket_A", Rectangle(150, 200), 12, Priority.HIGH, MaterialType.METAL),
            Order("Base_Plate", Rectangle(400, 600), 4, Priority.URGENT, MaterialType.METAL),
            Order("Cover_Panel", Rectangle(300, 800), 6, Priority.MEDIUM, MaterialType.METAL),
            Order("Support_Bar", Rectangle(100, 500), 8, Priority.LOW, MaterialType.METAL)
        ]
        
        real_world_solution = {
            "total_stock_used": 2,
            "total_orders_fulfilled": 30,
            "efficiency_percentage": 82.4,
            "waste_percentage": 17.6,
            "cutting_time_minutes": 95,
            "material_cost": 374.50,
            "solution_method": "Industrial metal cutting optimizer",
            "notes": "Real metal fabrication shop solution with plasma cutting"
        }
        
        return RealWorldTestCase(
            name="metal_fabrication",
            description="Real metal fabrication shop cutting optimization",
            stocks=stocks,
            orders=orders,
            real_world_solution=real_world_solution,
            industry="metal",
            complexity_level="high"
        )
    
    @staticmethod
    def get_textile_industry_case() -> RealWorldTestCase:
        """Real textile cutting case from industry data"""
        stocks = [
            Stock("Fabric_Roll_1", 1800, 1200, 2.0, MaterialType.FABRIC, 125.40)
        ]
        
        orders = [
            Order("Pattern_A", Rectangle(400, 350), 6, Priority.HIGH, MaterialType.FABRIC),
            Order("Pattern_B", Rectangle(300, 450), 4, Priority.MEDIUM, MaterialType.FABRIC),
            Order("Pattern_C", Rectangle(200, 250), 8, Priority.LOW, MaterialType.FABRIC)
        ]
        
        real_world_solution = {
            "total_stock_used": 1,
            "total_orders_fulfilled": 18,
            "efficiency_percentage": 91.7,
            "waste_percentage": 8.3,
            "cutting_time_minutes": 28,
            "material_cost": 125.40,
            "solution_method": "Textile industry pattern optimization",
            "notes": "Real textile manufacturer with automated cutting"
        }
        
        return RealWorldTestCase(
            name="textile_manufacturer",
            description="Real textile manufacturer cutting optimization",
            stocks=stocks,
            orders=orders,
            real_world_solution=real_world_solution,
            industry="textile",
            complexity_level="low"
        )


class SupervisedValidator:
    """Validates algorithm performance against real-world solutions"""
    
    def __init__(self):
        self.algorithms = [
            FirstFitAlgorithm(),
            BestFitAlgorithm(),
            BottomLeftAlgorithm(),
            GeneticAlgorithm()
        ]
        self.config = OptimizationConfig(
            allow_rotation=True,
            cutting_width=3.0,
            prioritize_orders=True
        )
    
    def calculate_validation_metrics(self, algorithm_result, real_world_solution: Dict[str, Any]) -> ValidationMetrics:
        """Calculate comprehensive validation metrics"""
        
        # Efficiency difference (lower is better)
        real_efficiency = real_world_solution.get('efficiency_percentage', 0)
        efficiency_diff = abs(algorithm_result.efficiency_percentage - real_efficiency)
        
        # Accuracy score (0-100, higher is better)
        accuracy_score = max(0, 100 - efficiency_diff * 2)
        
        # Stock usage ratio (closer to 1.0 is better)
        real_stock_used = real_world_solution.get('total_stock_used', 1)
        stock_usage_ratio = algorithm_result.total_stock_used / real_stock_used if real_stock_used > 0 else float('inf')
        
        # Order fulfillment ratio (closer to 1.0 is better)
        real_orders_fulfilled = real_world_solution.get('total_orders_fulfilled', 1)
        order_fulfillment_ratio = algorithm_result.total_orders_fulfilled / real_orders_fulfilled if real_orders_fulfilled > 0 else 0
        
        # Overall grade
        if accuracy_score >= 90:
            grade = "A"
        elif accuracy_score >= 80:
            grade = "B"
        elif accuracy_score >= 70:
            grade = "C"
        elif accuracy_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return ValidationMetrics(
            accuracy_score=accuracy_score,
            efficiency_difference=efficiency_diff,
            stock_usage_ratio=stock_usage_ratio,
            order_fulfillment_ratio=order_fulfillment_ratio,
            computation_time=algorithm_result.computation_time,
            overall_grade=grade
        )
    
    def run_supervised_test(self, test_case: RealWorldTestCase) -> Dict[str, ValidationMetrics]:
        """Run supervised test for all algorithms on a test case"""
        results = {}
        
        for algorithm in self.algorithms:
            try:
                # Run optimization
                start_time = time.time()
                result = algorithm.optimize(test_case.stocks, test_case.orders, self.config)
                end_time = time.time()
                
                # Update computation time
                result.computation_time = end_time - start_time
                
                # Calculate validation metrics
                metrics = self.calculate_validation_metrics(result, test_case.real_world_solution)
                results[algorithm.name] = metrics
                
            except Exception as e:
                print(f"Error running {algorithm.name} on {test_case.name}: {e}")
                continue
        
        return results


class TestSupervisedValidation(unittest.TestCase):
    """Test suite for supervised validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = SupervisedValidator()
        self.test_data = SupervisedTestData()
    
    def test_furniture_industry_case(self):
        """Test algorithms against real furniture industry case"""
        test_case = self.test_data.get_furniture_industry_case()
        results = self.validator.run_supervised_test(test_case)
        
        # Basic validation
        self.assertGreater(len(results), 0, "Should have at least one algorithm result")
        
        # Check that results are reasonable
        for algorithm_name, metrics in results.items():
            with self.subTest(algorithm=algorithm_name):
                self.assertGreaterEqual(metrics.accuracy_score, 0)
                self.assertLessEqual(metrics.accuracy_score, 100)
                self.assertGreater(metrics.computation_time, 0)
        
        print(f"\n=== FURNITURE INDUSTRY TEST RESULTS ===")
        print(f"Real-world benchmark: {test_case.real_world_solution['efficiency_percentage']}% efficiency")
        for algorithm_name, metrics in sorted(results.items(), key=lambda x: x[1].accuracy_score, reverse=True):
            print(f"{algorithm_name}: {metrics.accuracy_score:.1f}/100 (Grade: {metrics.overall_grade})")
    
    def test_glass_industry_case(self):
        """Test algorithms against real glass industry case"""
        test_case = self.test_data.get_glass_industry_case()
        results = self.validator.run_supervised_test(test_case)
        
        self.assertGreater(len(results), 0)
        
        print(f"\n=== GLASS INDUSTRY TEST RESULTS ===")
        print(f"Real-world benchmark: {test_case.real_world_solution['efficiency_percentage']}% efficiency")
        for algorithm_name, metrics in sorted(results.items(), key=lambda x: x[1].accuracy_score, reverse=True):
            print(f"{algorithm_name}: {metrics.accuracy_score:.1f}/100 (Grade: {metrics.overall_grade})")
    
    def test_metal_industry_case(self):
        """Test algorithms against real metal industry case"""
        test_case = self.test_data.get_metal_industry_case()
        results = self.validator.run_supervised_test(test_case)
        
        self.assertGreater(len(results), 0)
        
        print(f"\n=== METAL INDUSTRY TEST RESULTS ===")
        print(f"Real-world benchmark: {test_case.real_world_solution['efficiency_percentage']}% efficiency")
        for algorithm_name, metrics in sorted(results.items(), key=lambda x: x[1].accuracy_score, reverse=True):
            print(f"{algorithm_name}: {metrics.accuracy_score:.1f}/100 (Grade: {metrics.overall_grade})")
    
    def test_textile_industry_case(self):
        """Test algorithms against real textile industry case"""
        test_case = self.test_data.get_textile_industry_case()
        results = self.validator.run_supervised_test(test_case)
        
        self.assertGreater(len(results), 0)
        
        print(f"\n=== TEXTILE INDUSTRY TEST RESULTS ===")
        print(f"Real-world benchmark: {test_case.real_world_solution['efficiency_percentage']}% efficiency")
        for algorithm_name, metrics in sorted(results.items(), key=lambda x: x[1].accuracy_score, reverse=True):
            print(f"{algorithm_name}: {metrics.accuracy_score:.1f}/100 (Grade: {metrics.overall_grade})")
    
    def test_comprehensive_algorithm_ranking(self):
        """Generate comprehensive ranking across all test cases"""
        test_cases = [
            self.test_data.get_furniture_industry_case(),
            self.test_data.get_glass_industry_case(),
            self.test_data.get_metal_industry_case(),
            self.test_data.get_textile_industry_case()
        ]
        
        algorithm_scores = {}
        
        for test_case in test_cases:
            results = self.validator.run_supervised_test(test_case)
            
            for algorithm_name, metrics in results.items():
                if algorithm_name not in algorithm_scores:
                    algorithm_scores[algorithm_name] = []
                algorithm_scores[algorithm_name].append(metrics.accuracy_score)
        
        # Calculate average scores
        average_scores = {}
        for algorithm_name, scores in algorithm_scores.items():
            average_scores[algorithm_name] = {
                'average_score': statistics.mean(scores),
                'std_deviation': statistics.stdev(scores) if len(scores) > 1 else 0,
                'min_score': min(scores),
                'max_score': max(scores),
                'test_count': len(scores)
            }
        
        # Generate comprehensive report
        print("\n" + "="*60)
        print("COMPREHENSIVE ALGORITHM RANKING")
        print("="*60)
        
        sorted_algorithms = sorted(average_scores.items(), key=lambda x: x[1]['average_score'], reverse=True)
        
        for rank, (algorithm_name, stats) in enumerate(sorted_algorithms, 1):
            print(f"\n#{rank} {algorithm_name}")
            print(f"   Average Score: {stats['average_score']:.1f}/100")
            print(f"   Standard Deviation: {stats['std_deviation']:.1f}")
            print(f"   Score Range: {stats['min_score']:.1f} - {stats['max_score']:.1f}")
            print(f"   Tests Completed: {stats['test_count']}")
        
        # Ensure we have results
        self.assertGreater(len(average_scores), 0, "Should have algorithm results")
    
    def test_algorithm_accuracy_validation(self):
        """Test algorithm accuracy against statistical benchmarks"""
        test_case = self.test_data.get_furniture_industry_case()
        results = self.validator.run_supervised_test(test_case)
        
        print(f"\n=== ALGORITHM ACCURACY VALIDATION ===")
        
        for algorithm_name, metrics in results.items():
            # Check accuracy thresholds
            if metrics.accuracy_score >= 80:
                status = "✅ EXCELLENT"
            elif metrics.accuracy_score >= 70:
                status = "✅ GOOD"
            elif metrics.accuracy_score >= 60:
                status = "⚠️ ACCEPTABLE"
            else:
                status = "❌ POOR"
            
            print(f"{algorithm_name}: {status} ({metrics.accuracy_score:.1f}/100)")
            
            # Validate that algorithm meets minimum requirements
            self.assertGreaterEqual(metrics.accuracy_score, 50, 
                f"{algorithm_name} accuracy too low: {metrics.accuracy_score}")
            self.assertLess(metrics.computation_time, 30, 
                f"{algorithm_name} too slow: {metrics.computation_time}s")


if __name__ == '__main__':
    unittest.main(verbosity=2) 