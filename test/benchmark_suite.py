#!/usr/bin/env python3
"""
Comprehensive Benchmarking Suite for Surface Cutting Optimizer

This script runs extensive benchmarks comparing algorithm performance
against real-world industry solutions and generates detailed reports.
"""

import time
import json
import os
import statistics
from datetime import datetime
from typing import Dict, List, Any

from test_supervised_validation import SupervisedTestData, SupervisedValidator, ValidationMetrics
from surface_optimizer.core.models import OptimizationConfig


class BenchmarkRunner:
    """Runs comprehensive benchmarks and generates reports"""
    
    def __init__(self):
        self.validator = SupervisedValidator()
        self.test_data = SupervisedTestData()
        self.results = {}
        self.benchmark_start_time = None
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests and collect results"""
        self.benchmark_start_time = datetime.now()
        
        print("🚀 Starting Comprehensive Algorithm Benchmarking...")
        print("=" * 60)
        
        # Define test cases
        test_cases = {
            "furniture_workshop": self.test_data.get_furniture_industry_case(),
            "glass_manufacturer": self.test_data.get_glass_industry_case(),
            "metal_fabrication": self.test_data.get_metal_industry_case(),
            "textile_manufacturer": self.test_data.get_textile_industry_case()
        }
        
        benchmark_results = {
            "timestamp": self.benchmark_start_time.isoformat(),
            "test_cases": {},
            "algorithm_rankings": {},
            "performance_summary": {}
        }
        
        # Run tests for each case
        for test_name, test_case in test_cases.items():
            print(f"\n🔧 Testing {test_name}...")
            
            start_time = time.time()
            results = self.validator.run_supervised_test(test_case)
            end_time = time.time()
            
            benchmark_results["test_cases"][test_name] = {
                "industry": test_case.industry,
                "complexity": test_case.complexity_level,
                "real_world_benchmark": test_case.real_world_solution,
                "algorithm_results": {
                    alg_name: {
                        "accuracy_score": metrics.accuracy_score,
                        "efficiency_difference": metrics.efficiency_difference,
                        "stock_usage_ratio": metrics.stock_usage_ratio,
                        "order_fulfillment_ratio": metrics.order_fulfillment_ratio,
                        "computation_time": metrics.computation_time,
                        "overall_grade": metrics.overall_grade
                    }
                    for alg_name, metrics in results.items()
                },
                "test_duration": end_time - start_time
            }
            
            # Print immediate results
            self._print_test_results(test_name, test_case, results)
        
        # Calculate overall rankings
        benchmark_results["algorithm_rankings"] = self._calculate_rankings(benchmark_results["test_cases"])
        
        # Generate performance summary
        benchmark_results["performance_summary"] = self._generate_performance_summary(benchmark_results)
        
        self.results = benchmark_results
        return benchmark_results
    
    def _print_test_results(self, test_name: str, test_case, results: Dict[str, ValidationMetrics]):
        """Print results for a single test case"""
        print(f"\n📊 Results for {test_name.replace('_', ' ').title()}:")
        print(f"   Industry: {test_case.industry}")
        print(f"   Real-world benchmark: {test_case.real_world_solution['efficiency_percentage']}% efficiency")
        
        sorted_results = sorted(results.items(), key=lambda x: x[1].accuracy_score, reverse=True)
        
        for rank, (algorithm_name, metrics) in enumerate(sorted_results, 1):
            grade_emoji = {
                "A": "🥇", "B": "🥈", "C": "🥉", "D": "📊", "F": "❌"
            }.get(metrics.overall_grade, "📊")
            
            print(f"   {rank}. {algorithm_name}: {metrics.accuracy_score:.1f}/100 "
                  f"({metrics.overall_grade}) {grade_emoji}")
    
    def _calculate_rankings(self, test_cases: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall algorithm rankings across all test cases"""
        algorithm_scores = {}
        
        # Collect all scores
        for test_name, test_data in test_cases.items():
            for alg_name, alg_data in test_data["algorithm_results"].items():
                if alg_name not in algorithm_scores:
                    algorithm_scores[alg_name] = []
                algorithm_scores[alg_name].append(alg_data["accuracy_score"])
        
        # Calculate statistics
        rankings = {}
        for alg_name, scores in algorithm_scores.items():
            rankings[alg_name] = {
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "std_deviation": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min_score": min(scores),
                "max_score": max(scores),
                "test_count": len(scores)
            }
        
        return rankings
    
    def _generate_performance_summary(self, benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall performance summary"""
        rankings = benchmark_results["algorithm_rankings"]
        
        # Find best overall algorithm
        best_algorithm = max(rankings.items(), key=lambda x: x[1]["average_score"])
        
        # Find most consistent algorithm
        most_consistent = min(rankings.items(), key=lambda x: x[1]["std_deviation"])
        
        return {
            "best_overall_algorithm": {
                "name": best_algorithm[0],
                "average_score": best_algorithm[1]["average_score"]
            },
            "most_consistent_algorithm": {
                "name": most_consistent[0],
                "std_deviation": most_consistent[1]["std_deviation"]
            },
            "total_tests_run": sum(data["test_count"] for data in rankings.values()),
            "benchmark_duration": (datetime.now() - self.benchmark_start_time).total_seconds()
        }
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed benchmark report"""
        if not self.results:
            return "No benchmark results available. Run benchmarks first."
        
        report = f"""
{'='*80}
           SURFACE CUTTING OPTIMIZER - BENCHMARK REPORT
{'='*80}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Benchmark Duration: {self.results['performance_summary']['benchmark_duration']:.2f} seconds
Total Tests: {self.results['performance_summary']['total_tests_run']}

{'='*80}
                              OVERALL RANKINGS
{'='*80}
"""
        
        # Sort algorithms by average score
        sorted_algorithms = sorted(
            self.results["algorithm_rankings"].items(),
            key=lambda x: x[1]["average_score"],
            reverse=True
        )
        
        for rank, (alg_name, stats) in enumerate(sorted_algorithms, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f" {rank}."
            
            report += f"""
{medal} {alg_name}
   📊 Average Score: {stats['average_score']:.1f}/100
   📈 Score Range: {stats['min_score']:.1f} - {stats['max_score']:.1f}
   🎯 Consistency: {stats['consistency_rating']} (σ={stats['std_deviation']:.1f})
   ✅ Tests Completed: {stats['test_count']}/4
"""
        
        report += f"""

{'='*80}
                           INDUSTRY-SPECIFIC RESULTS
{'='*80}
"""
        
        for test_name, test_data in self.results["test_cases"].items():
            industry = test_data["industry"].title()
            complexity = test_data["complexity"].title()
            real_efficiency = test_data["real_world_benchmark"]["efficiency_percentage"]
            
            report += f"""
🏭 {industry} Industry ({complexity} Complexity)
   Real-world benchmark: {real_efficiency}% efficiency
   Test case: {test_name.replace('_', ' ').title()}
   
   Algorithm Performance:
"""
            
            sorted_results = sorted(
                test_data["algorithm_results"].items(),
                key=lambda x: x[1]["accuracy_score"],
                reverse=True
            )
            
            for alg_name, metrics in sorted_results:
                grade_emoji = {
                    "A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"
                }.get(metrics["overall_grade"], "⚪")
                
                report += f"   {grade_emoji} {alg_name}: {metrics['accuracy_score']:.1f}/100 "
                report += f"(Δ{metrics['efficiency_difference']:.1f}%, {metrics['computation_time']:.3f}s)\n"
        
        report += f"""

{'='*80}
                              KEY INSIGHTS
{'='*80}

🏆 Best Overall: {self.results['performance_summary']['best_overall_algorithm']['name']} 
   ({self.results['performance_summary']['best_overall_algorithm']['average_score']:.1f}/100 avg)

🎯 Most Consistent: {self.results['performance_summary']['most_consistent_algorithm']['name']}
   (σ={self.results['performance_summary']['most_consistent_algorithm']['std_deviation']:.1f})

🏭 Industry Specialists:
"""
        
        for industry, algorithm in self.results['performance_summary']['industry_specialists'].items():
            report += f"   • {industry.title()}: {algorithm}\n"
        
        report += f"""

{'='*80}
                            RECOMMENDATIONS
{'='*80}

Based on this comprehensive analysis:

1. 🚀 For general use: {sorted_algorithms[0][0]}
2. 🎯 For consistent results: {self.results['performance_summary']['most_consistent_algorithm']['name']}
3. ⚡ For speed-critical applications: Check computation times above
4. 🏭 For industry-specific needs: Use the specialists listed above

Note: These recommendations are based on comparison with real-world industry
solutions and may vary based on your specific requirements.

{'='*80}
"""
        
        return report
    
    def save_results(self, filename: str = None):
        """Save benchmark results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
    
    def save_report(self, filename: str = None):
        """Save detailed report to text file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"benchmark_report_{timestamp}.txt"
        
        report = self.generate_detailed_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {filename}")


def main():
    """Main benchmark execution function"""
    print("🎯 Surface Cutting Optimizer - Supervised Testing Suite")
    print("Comparing algorithms against real-world industry solutions...")
    
    # Run benchmarks
    runner = BenchmarkRunner()
    results = runner.run_all_benchmarks()
    
    # Generate and display report
    print("\n" + "="*80)
    print("GENERATING DETAILED BENCHMARK REPORT")
    print("="*80)
    
    report = runner.generate_detailed_report()
    print(report)
    
    # Save results
    runner.save_results()
    runner.save_report()
    
    print("\n✅ Benchmark complete! Check the generated files for detailed results.")


if __name__ == "__main__":
    main() 