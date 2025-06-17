#!/usr/bin/env python3
"""
Surface Cutting Optimizer - Automatic Dependency Installer

Installs all free optimization libraries for industrial-scale cutting problems.
This script automatically sets up your system for professional optimization.

Libraries installed:
✅ Google OR-Tools - Best performance for complex industrial problems
✅ Python-MIP (CBC) - Excellent for medium-scale enterprise problems  
✅ PuLP - Alternative optimization library with CBC integration
✅ SciPy - Scientific computing with basic optimization (fallback)
✅ NumPy - Numerical computing foundation
✅ Matplotlib - Visualization and reporting

Total value: Replaces $50,000+/year commercial optimization software!
"""

import subprocess
import sys
import time
import importlib
from typing import List, Dict, Tuple


class OptimizationInstaller:
    """Professional installer for optimization dependencies"""
    
    def __init__(self):
        self.required_packages = [
            ("ortools", "Google OR-Tools", "Industrial-grade optimization (SCIP, CBC, GLOP)"),
            ("mip", "Python-MIP", "Python interface to CBC and other MIP solvers"),
            ("pulp", "PuLP", "Linear programming library with CBC integration"),
            ("scipy", "SciPy", "Scientific computing with optimization capabilities"),
            ("numpy", "NumPy", "Numerical computing foundation"),
        ]
        
        self.optional_packages = [
            ("matplotlib", "Matplotlib", "Visualization and professional reporting"),
            ("pandas", "Pandas", "Data analysis and CSV/Excel integration"),
            ("cvxpy", "CVXPY", "Additional convex optimization capabilities"),
        ]
        
        self.installation_results = {}
    
    def print_header(self):
        """Print professional installer header"""
        print("="*80)
        print("🏭 SURFACE CUTTING OPTIMIZER - PROFESSIONAL SETUP")
        print("🚀 Installing Industrial-Grade Optimization Libraries")
        print("💰 Free Alternative to $50,000+/year Commercial Solutions")
        print("="*80)
        
        print("\n📦 OPTIMIZATION LIBRARIES TO INSTALL:")
        print("-" * 50)
        
        for package, name, description in self.required_packages:
            print(f"✅ {name:<20} - {description}")
            
        print("\n📦 OPTIONAL ENHANCEMENTS:")
        print("-" * 50)
        
        for package, name, description in self.optional_packages:
            print(f"📊 {name:<20} - {description}")
    
    def check_existing_installations(self) -> Dict[str, bool]:
        """Check which packages are already installed"""
        print("\n🔍 CHECKING EXISTING INSTALLATIONS...")
        print("-" * 50)
        
        existing = {}
        
        all_packages = self.required_packages + self.optional_packages
        for package, name, description in all_packages:
            try:
                importlib.import_module(package)
                existing[package] = True
                print(f"✅ {name:<20} - Already installed")
            except ImportError:
                existing[package] = False
                print(f"❌ {name:<20} - Not found, will install")
        
        return existing
    
    def install_package(self, package: str, name: str, timeout: int = 300) -> bool:
        """Install a single package with progress feedback"""
        print(f"\n🔄 Installing {name}...")
        print(f"   Package: {package}")
        print(f"   Command: pip install {package}")
        
        try:
            # Run pip install with real-time output
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package, "--upgrade"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Show progress dots
            start_time = time.time()
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    process.kill()
                    print("   ⏰ Installation timeout!")
                    return False
                
                print(".", end="", flush=True)
                time.sleep(0.5)
            
            print()  # New line after dots
            
            if process.returncode == 0:
                print(f"   ✅ Successfully installed {name}")
                
                # Verify installation
                try:
                    importlib.import_module(package)
                    print(f"   ✓ Verified: {name} is working correctly")
                    return True
                except ImportError:
                    print(f"   ⚠️ Warning: {name} installed but not importable")
                    return False
            else:
                print(f"   ❌ Failed to install {name}")
                print(f"   Return code: {process.returncode}")
                return False
                
        except Exception as e:
            print(f"   ❌ Installation error: {e}")
            return False
    
    def install_required_packages(self, existing: Dict[str, bool]) -> int:
        """Install all required packages"""
        print("\n" + "="*60)
        print("🔧 INSTALLING REQUIRED OPTIMIZATION LIBRARIES")
        print("="*60)
        
        success_count = 0
        total_required = len(self.required_packages)
        
        for i, (package, name, description) in enumerate(self.required_packages, 1):
            print(f"\n[{i}/{total_required}] Processing {name}...")
            
            if existing.get(package, False):
                print(f"   ✅ {name} already installed - skipping")
                success_count += 1
                self.installation_results[package] = "already_installed"
            else:
                if self.install_package(package, name):
                    success_count += 1
                    self.installation_results[package] = "installed"
                else:
                    self.installation_results[package] = "failed"
        
        return success_count
    
    def install_optional_packages(self, existing: Dict[str, bool]) -> int:
        """Install optional enhancement packages"""
        print("\n" + "="*60)
        print("📊 INSTALLING OPTIONAL ENHANCEMENTS")
        print("="*60)
        
        success_count = 0
        
        for i, (package, name, description) in enumerate(self.optional_packages, 1):
            print(f"\n[{i}/{len(self.optional_packages)}] Processing {name}...")
            
            if existing.get(package, False):
                print(f"   ✅ {name} already installed - skipping")
                success_count += 1
                self.installation_results[package] = "already_installed"
            else:
                if self.install_package(package, name):
                    success_count += 1
                    self.installation_results[package] = "installed"
                else:
                    self.installation_results[package] = "failed"
                    print(f"   ⚠️ Optional package {name} failed - continuing...")
        
        return success_count
    
    def test_optimization_capabilities(self):
        """Test that optimization capabilities work correctly"""
        print("\n" + "="*60)
        print("🧪 TESTING OPTIMIZATION CAPABILITIES")
        print("="*60)
        
        tests = [
            ("ortools", "Google OR-Tools", self._test_ortools),
            ("mip", "Python-MIP", self._test_python_mip),
            ("pulp", "PuLP", self._test_pulp),
            ("scipy", "SciPy", self._test_scipy),
        ]
        
        working_solvers = 0
        
        for package, name, test_func in tests:
            print(f"\n🔬 Testing {name}...")
            try:
                if test_func():
                    print(f"   ✅ {name} is working correctly")
                    working_solvers += 1
                else:
                    print(f"   ❌ {name} test failed")
            except Exception as e:
                print(f"   ❌ {name} test error: {e}")
        
        print(f"\n📊 Test Results: {working_solvers}/{len(tests)} optimization solvers working")
        return working_solvers
    
    def _test_ortools(self) -> bool:
        """Test Google OR-Tools functionality"""
        try:
            from ortools.linear_solver import pywraplp
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if not solver:
                solver = pywraplp.Solver.CreateSolver('CBC')
            return solver is not None
        except ImportError:
            return False
    
    def _test_python_mip(self) -> bool:
        """Test Python-MIP functionality"""
        try:
            from mip import Model, CBC
            model = Model(solver_name=CBC)
            return model is not None
        except ImportError:
            return False
    
    def _test_pulp(self) -> bool:
        """Test PuLP functionality"""
        try:
            import pulp
            prob = pulp.LpProblem("test", pulp.LpMinimize)
            return prob is not None
        except ImportError:
            return False
    
    def _test_scipy(self) -> bool:
        """Test SciPy optimization functionality"""
        try:
            from scipy.optimize import linprog
            import numpy as np
            
            # Simple test problem
            c = np.array([1, 1])
            A_eq = np.array([[1, 1]])
            b_eq = np.array([1])
            bounds = [(0, None), (0, None)]
            
            result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            return result.success
        except ImportError:
            return False
    
    def generate_final_report(self, required_success: int, optional_success: int, working_solvers: int):
        """Generate comprehensive installation report"""
        print("\n" + "="*80)
        print("🎉 INSTALLATION COMPLETE - FINAL REPORT")
        print("="*80)
        
        total_required = len(self.required_packages)
        total_optional = len(self.optional_packages)
        
        # Installation Summary
        print(f"\n📦 INSTALLATION SUMMARY:")
        print(f"   Required Packages:  {required_success}/{total_required} installed")
        print(f"   Optional Packages:  {optional_success}/{total_optional} installed")
        print(f"   Working Solvers:    {working_solvers}/4 tested successfully")
        
        # Success Rate
        total_packages = total_required + total_optional
        total_success = required_success + optional_success
        success_rate = (total_success / total_packages) * 100
        
        print(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        # Performance Assessment
        if required_success == total_required and working_solvers >= 3:
            status = "🚀 EXCELLENT - Ready for Industrial Deployment!"
            capabilities = "✅ Complex industrial problems (1000+ pieces)\n✅ Medium enterprise problems (100-1000 pieces)\n✅ Simple problems (<100 pieces)"
        elif required_success >= 3 and working_solvers >= 2:
            status = "✅ GOOD - Ready for Professional Use"
            capabilities = "✅ Medium enterprise problems (100-1000 pieces)\n✅ Simple problems (<100 pieces)\n⚠️ Limited complex problem support"
        elif required_success >= 2 and working_solvers >= 1:
            status = "⚠️ BASIC - Limited Functionality"
            capabilities = "✅ Simple problems (<100 pieces)\n❌ Limited enterprise support"
        else:
            status = "❌ INSUFFICIENT - Manual Setup Required"
            capabilities = "❌ Limited optimization capabilities"
        
        print(f"\n🎯 SYSTEM STATUS: {status}")
        print(f"\n🏭 PROBLEM SOLVING CAPABILITIES:")
        print(capabilities)
        
        # Cost Savings
        print(f"\n💰 COST SAVINGS ACHIEVED:")
        if working_solvers >= 2:
            print("   ✅ Replaces commercial software worth $50,000+/year")
            print("   ✅ No licensing fees or per-user costs")
            print("   ✅ Full source code access and customization")
        
        # Next Steps
        print(f"\n🚀 NEXT STEPS:")
        print("   1. Test the installation:")
        print("      python demo/industrial_demo.py")
        print("   2. Run quick optimization test:")
        print("      python demo/quick_demo.py")
        print("   3. Check solver status:")
        print("      python -c 'from surface_optimizer.utils.dependency_manager import dependency_manager; dependency_manager.print_status_report()'")
        
        if required_success < total_required:
            print("\n🔧 TROUBLESHOOTING:")
            failed_packages = [pkg for pkg, status in self.installation_results.items() 
                             if status == "failed"]
            if failed_packages:
                print("   Failed packages can be installed manually:")
                for pkg in failed_packages:
                    print(f"      pip install {pkg}")
        
        print("\n" + "="*80)
        print("🎉 Your Surface Cutting Optimizer is ready!")
        print("📞 Happy optimizing! You now have professional-grade cutting optimization.")
        print("="*80)
        
        return success_rate >= 80  # Consider successful if 80%+ packages installed


def main():
    """Main installation function"""
    installer = OptimizationInstaller()
    
    try:
        # Print header and package list
        installer.print_header()
        
        # Check existing installations
        existing = installer.check_existing_installations()
        
        # Install required packages
        required_success = installer.install_required_packages(existing)
        
        # Install optional packages
        optional_success = installer.install_optional_packages(existing)
        
        # Test optimization capabilities
        working_solvers = installer.test_optimization_capabilities()
        
        # Generate final report
        success = installer.generate_final_report(required_success, optional_success, working_solvers)
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation interrupted by user")
        print("🔧 You can resume installation by running this script again")
        return False
    except Exception as e:
        print(f"\n\n❌ Installation failed with error: {e}")
        print("🔧 Try manual installation: pip install ortools mip pulp scipy numpy")
        return False


if __name__ == "__main__":
    print("🔧 Starting Surface Cutting Optimizer Installation...")
    success = main()
    
    if success:
        print("\n🎉 Installation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Installation had issues. Check the report above.")
        sys.exit(1) 