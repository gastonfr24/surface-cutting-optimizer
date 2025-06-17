"""
Dependency Manager for Surface Cutting Optimizer

Automatically detects, installs and manages free optimization libraries:
- Google OR-Tools (best for complex problems)
- Python-MIP with CBC (good for medium problems)  
- SciPy (fallback for simple problems)
- PuLP (alternative open source solver)

Provides intelligent fallbacks when libraries are not available.
"""

import subprocess
import sys
import importlib
import warnings
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SolverType(Enum):
    """Types of optimization solvers"""
    ORTOOLS = "ortools"
    PYTHON_MIP = "python-mip"
    PULP = "pulp"
    SCIPY = "scipy"
    CVXPY = "cvxpy"


@dataclass
class SolverInfo:
    """Information about an optimization solver"""
    name: str
    package_name: str
    import_name: str
    description: str
    install_command: str
    capabilities: List[str]
    performance_level: int  # 1-5, 5 being best
    is_available: bool = False


class DependencyManager:
    """
    Manages optimization library dependencies with automatic installation
    and intelligent fallbacks for industrial-scale problems
    """
    
    def __init__(self):
        self.solvers = self._initialize_solver_info()
        self.check_all_dependencies()
    
    def _initialize_solver_info(self) -> Dict[SolverType, SolverInfo]:
        """Initialize information about available free optimization solvers"""
        return {
            SolverType.ORTOOLS: SolverInfo(
                name="Google OR-Tools",
                package_name="ortools",
                import_name="ortools.linear_solver.pywraplp",
                description="Google's open source optimization toolkit (best for complex problems)",
                install_command="pip install ortools",
                capabilities=["linear_programming", "integer_programming", "constraint_programming", "routing"],
                performance_level=5
            ),
            
            SolverType.PYTHON_MIP: SolverInfo(
                name="Python-MIP",
                package_name="mip",
                import_name="mip",
                description="Python interface to CBC and Gurobi (good for medium problems)",
                install_command="pip install mip",
                capabilities=["linear_programming", "integer_programming"],
                performance_level=4
            ),
            
            SolverType.PULP: SolverInfo(
                name="PuLP",
                package_name="pulp",
                import_name="pulp",
                description="Python linear programming library with CBC integration",
                install_command="pip install pulp",
                capabilities=["linear_programming", "integer_programming"],
                performance_level=3
            ),
            
            SolverType.SCIPY: SolverInfo(
                name="SciPy",
                package_name="scipy",
                import_name="scipy.optimize",
                description="Scientific computing library with basic optimization (fallback)",
                install_command="pip install scipy",
                capabilities=["linear_programming"],
                performance_level=2
            ),
            
            SolverType.CVXPY: SolverInfo(
                name="CVXPY",
                package_name="cvxpy",
                import_name="cvxpy",
                description="Convex optimization library with multiple solver backends",
                install_command="pip install cvxpy",
                capabilities=["linear_programming", "convex_optimization"],
                performance_level=3
            )
        }
    
    def check_all_dependencies(self) -> Dict[SolverType, bool]:
        """Check availability of all optimization libraries"""
        results = {}
        
        for solver_type, solver_info in self.solvers.items():
            is_available = self._check_single_dependency(solver_info)
            self.solvers[solver_type].is_available = is_available
            results[solver_type] = is_available
        
        return results
    
    def _check_single_dependency(self, solver_info: SolverInfo) -> bool:
        """Check if a single optimization library is available"""
        try:
            importlib.import_module(solver_info.import_name)
            return True
        except ImportError:
            return False
    
    def install_recommended_solvers(self, auto_install: bool = False) -> Dict[str, bool]:
        """
        Install recommended free optimization solvers
        
        Args:
            auto_install: If True, automatically install without user confirmation
            
        Returns:
            Dictionary with installation results
        """
        recommended = [SolverType.ORTOOLS, SolverType.PYTHON_MIP, SolverType.SCIPY]
        results = {}
        
        for solver_type in recommended:
            solver_info = self.solvers[solver_type]
            
            if not solver_info.is_available:
                if auto_install or self._confirm_installation(solver_info):
                    success = self._install_package(solver_info)
                    results[solver_info.name] = success
                    if success:
                        self.solvers[solver_type].is_available = True
                else:
                    results[solver_info.name] = False
            else:
                results[solver_info.name] = True
        
        return results
    
    def _confirm_installation(self, solver_info: SolverInfo) -> bool:
        """Ask user confirmation for package installation"""
        print(f"\n📦 Package not found: {solver_info.name}")
        print(f"   Description: {solver_info.description}")
        print(f"   Install command: {solver_info.install_command}")
        
        response = input(f"Install {solver_info.name}? (y/n): ").lower().strip()
        return response in ['y', 'yes', '1', 'true']
    
    def _install_package(self, solver_info: SolverInfo) -> bool:
        """Install a package using pip"""
        try:
            print(f"🔄 Installing {solver_info.name}...")
            
            # Use subprocess to install package
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", solver_info.package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {solver_info.name}")
                return True
            else:
                print(f"❌ Failed to install {solver_info.name}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Installation timeout for {solver_info.name}")
            return False
        except Exception as e:
            print(f"❌ Installation error for {solver_info.name}: {e}")
            return False
    
    def get_best_available_solver(self, problem_complexity: str = "medium") -> Optional[SolverType]:
        """
        Get the best available solver for a given problem complexity
        
        Args:
            problem_complexity: "simple", "medium", or "complex"
            
        Returns:
            Best available solver type or None if no solvers available
        """
        available_solvers = [
            (solver_type, solver_info) 
            for solver_type, solver_info in self.solvers.items() 
            if solver_info.is_available
        ]
        
        if not available_solvers:
            return None
        
        # Sort by performance level (descending)
        available_solvers.sort(key=lambda x: x[1].performance_level, reverse=True)
        
        # Filter by complexity requirements
        if problem_complexity == "complex":
            # Need high-performance solvers for complex problems
            for solver_type, solver_info in available_solvers:
                if solver_info.performance_level >= 4:
                    return solver_type
        elif problem_complexity == "medium":
            # Medium performance solvers are fine
            for solver_type, solver_info in available_solvers:
                if solver_info.performance_level >= 3:
                    return solver_type
        
        # Return best available solver for simple problems or as fallback
        return available_solvers[0][0]
    
    def get_solver_recommendations(self) -> Dict[str, List[str]]:
        """Get solver recommendations based on problem types"""
        available = [info.name for info in self.solvers.values() if info.is_available]
        missing = [info.name for info in self.solvers.values() if not info.is_available]
        
        recommendations = {
            "available_solvers": available,
            "missing_solvers": missing,
            "recommendations": []
        }
        
        if not self.solvers[SolverType.ORTOOLS].is_available:
            recommendations["recommendations"].append(
                "Install Google OR-Tools for best performance on complex industrial problems"
            )
        
        if not self.solvers[SolverType.PYTHON_MIP].is_available:
            recommendations["recommendations"].append(
                "Install Python-MIP for excellent medium-scale problem solving with CBC"
            )
        
        if not any(solver.is_available for solver in self.solvers.values()):
            recommendations["recommendations"].append(
                "No optimization solvers found! Install at least SciPy for basic functionality"
            )
        
        return recommendations
    
    def print_status_report(self):
        """Print a comprehensive status report of all solvers"""
        print("\n" + "="*70)
        print("🔧 SURFACE CUTTING OPTIMIZER - SOLVER STATUS REPORT")
        print("="*70)
        
        # Available solvers
        available_solvers = [(st, si) for st, si in self.solvers.items() if si.is_available]
        if available_solvers:
            print("\n✅ AVAILABLE SOLVERS:")
            for solver_type, solver_info in available_solvers:
                performance_stars = "⭐" * solver_info.performance_level
                print(f"   {solver_info.name:<25} {performance_stars} - {solver_info.description}")
        
        # Missing solvers
        missing_solvers = [(st, si) for st, si in self.solvers.items() if not si.is_available]
        if missing_solvers:
            print("\n❌ MISSING SOLVERS:")
            for solver_type, solver_info in missing_solvers:
                print(f"   {solver_info.name:<25} - {solver_info.install_command}")
        
        # Recommendations
        recommendations = self.get_solver_recommendations()
        if recommendations["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations["recommendations"]:
                print(f"   • {rec}")
        
        # Problem solving capabilities
        print("\n🎯 PROBLEM SOLVING CAPABILITIES:")
        if self.solvers[SolverType.ORTOOLS].is_available:
            print("   ✅ Complex Industrial Problems (1000+ pieces) - OR-Tools")
        if self.solvers[SolverType.PYTHON_MIP].is_available:
            print("   ✅ Medium Enterprise Problems (100-1000 pieces) - Python-MIP")
        if any(self.solvers[st].is_available for st in [SolverType.PULP, SolverType.SCIPY]):
            print("   ✅ Simple Problems (<100 pieces) - Multiple solvers")
        
        if not any(solver.is_available for solver in self.solvers.values()):
            print("   ❌ No optimization capabilities available")
        
        print("\n" + "="*70)
    
    def create_installation_script(self, filename: str = "install_optimizers.py"):
        """Create a standalone installation script"""
        script_content = f'''#!/usr/bin/env python3
"""
Automatic installer for Surface Cutting Optimizer dependencies
Installs all free optimization libraries for industrial-scale cutting problems
"""

import subprocess
import sys

REQUIRED_PACKAGES = [
    "ortools",      # Google OR-Tools (best performance)
    "mip",          # Python-MIP with CBC
    "pulp",         # PuLP optimization library
    "scipy",        # SciPy (fallback)
    "numpy",        # Numerical computing
]

OPTIONAL_PACKAGES = [
    "cvxpy",        # CVXPY for convex optimization
    "matplotlib",   # For visualization
    "pandas",       # For data handling
]

def install_package(package_name):
    """Install a single package"""
    try:
        print(f"🔄 Installing {{package_name}}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully installed {{package_name}}")
            return True
        else:
            print(f"❌ Failed to install {{package_name}}")
            print(f"Error: {{result.stderr}}")
            return False
    except Exception as e:
        print(f"❌ Error installing {{package_name}}: {{e}}")
        return False

def main():
    print("🚀 Installing Surface Cutting Optimizer Dependencies...")
    print("="*60)
    
    success_count = 0
    total_packages = len(REQUIRED_PACKAGES)
    
    # Install required packages
    print("📦 Installing required packages...")
    for package in REQUIRED_PACKAGES:
        if install_package(package):
            success_count += 1
    
    # Install optional packages
    print("\n📦 Installing optional packages...")
    for package in OPTIONAL_PACKAGES:
        install_package(package)
    
    print("\n" + "="*60)
    print(f"🎉 Installation complete! {{success_count}}/{{total_packages}} required packages installed.")
    
    if success_count == total_packages:
        print("✅ All required packages installed successfully!")
        print("🚀 Your Surface Cutting Optimizer is ready for industrial use!")
    else:
        print("⚠️  Some packages failed to install. Basic functionality may be limited.")
    
    print("\n💡 To test your installation, run:")
    print("   python -c 'from surface_optimizer.utils.dependency_manager import DependencyManager; DependencyManager().print_status_report()'")

if __name__ == "__main__":
    main()
'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"📝 Created installation script: {filename}")
        print(f"💡 Run with: python {filename}")


# Global instance for easy access
dependency_manager = DependencyManager()


def ensure_solver_available(problem_complexity: str = "medium") -> bool:
    """
    Ensure that at least one suitable solver is available for the given complexity
    
    Args:
        problem_complexity: "simple", "medium", or "complex"
        
    Returns:
        True if a suitable solver is available, False otherwise
    """
    best_solver = dependency_manager.get_best_available_solver(problem_complexity)
    
    if best_solver is None:
        print(f"⚠️  No optimization solver available for {problem_complexity} problems!")
        print("🔧 Installing recommended solvers...")
        
        # Try to install automatically
        results = dependency_manager.install_recommended_solvers(auto_install=True)
        success = any(results.values())
        
        if success:
            dependency_manager.check_all_dependencies()
            best_solver = dependency_manager.get_best_available_solver(problem_complexity)
            return best_solver is not None
        else:
            return False
    
    return True


def get_solver_status() -> Dict[str, any]:
    """Get current solver status for reporting"""
    available_solvers = []
    missing_solvers = []
    
    for solver_type, solver_info in dependency_manager.solvers.items():
        if solver_info.is_available:
            available_solvers.append({
                "name": solver_info.name,
                "performance": solver_info.performance_level,
                "capabilities": solver_info.capabilities
            })
        else:
            missing_solvers.append({
                "name": solver_info.name,
                "install_command": solver_info.install_command
            })
    
    return {
        "available_solvers": available_solvers,
        "missing_solvers": missing_solvers,
        "total_available": len(available_solvers),
        "recommendations": dependency_manager.get_solver_recommendations()
    } 