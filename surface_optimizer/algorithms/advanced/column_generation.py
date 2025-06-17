"""
Advanced Column Generation Algorithm for Industrial Cutting Stock Optimization

This module implements the Column Generation approach using free open source solvers
for handling both simple and complex industrial-scale cutting problems.

Supports:
- Small problems (< 100 pieces): Fast heuristics
- Medium problems (100-1000 pieces): Hybrid approach  
- Large problems (1000+ pieces): Full column generation with SCIP/CBC
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

try:
    from mip import Model, xsum, minimize, BINARY, INTEGER, CBC, GUROBI, CPLEX
    PYTHON_MIP_AVAILABLE = True
except ImportError:
    PYTHON_MIP_AVAILABLE = False

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from ..base import CuttingAlgorithm
from ...core.models import Surface, Piece, CuttingResult, CuttingPattern


@dataclass
class SolutionQuality:
    """Quality metrics for cutting solution"""
    efficiency: float
    waste_percentage: float
    total_surfaces: int
    computation_time: float
    algorithm_used: str
    problem_complexity: str


class ColumnGenerationSolver:
    """
    Industrial-grade Column Generation solver using free open source libraries
    
    Automatically selects the best available solver and approach based on:
    - Problem size and complexity
    - Available libraries  
    - Performance requirements
    """
    
    def __init__(self):
        self.available_solvers = self._detect_available_solvers()
        self.solver_preference = self._get_solver_preference()
        
    def _detect_available_solvers(self) -> Dict[str, bool]:
        """Detect which free solvers are available"""
        return {
            'ortools': ORTOOLS_AVAILABLE,
            'python_mip_cbc': PYTHON_MIP_AVAILABLE,
            'scipy': SCIPY_AVAILABLE
        }
    
    def _get_solver_preference(self) -> List[str]:
        """Get solver preference order (best to fallback)"""
        preferences = []
        
        # OR-Tools (Google) - Best for complex problems
        if self.available_solvers['ortools']:
            preferences.append('ortools')
            
        # Python-MIP with CBC - Good for medium problems  
        if self.available_solvers['python_mip_cbc']:
            preferences.append('python_mip_cbc')
            
        # SciPy - Fallback for simple linear programming
        if self.available_solvers['scipy']:
            preferences.append('scipy')
            
        return preferences
    
    def solve_master_problem(self, patterns: List[CuttingPattern], demands: List[int]) -> Tuple[List[float], float]:
        """
        Solve the master problem: minimize number of surfaces used
        
        Args:
            patterns: List of cutting patterns (columns)
            demands: Demand for each piece type
            
        Returns:
            Tuple of (pattern_usage, objective_value)
        """
        if not patterns:
            return [], float('inf')
            
        # Try solvers in preference order
        for solver_name in self.solver_preference:
            try:
                if solver_name == 'ortools':
                    return self._solve_master_ortools(patterns, demands)
                elif solver_name == 'python_mip_cbc':
                    return self._solve_master_python_mip(patterns, demands)
                elif solver_name == 'scipy':
                    return self._solve_master_scipy(patterns, demands)
            except Exception as e:
                print(f"Solver {solver_name} failed: {e}")
                continue
                
        # Fallback to simple greedy if all solvers fail
        return self._solve_master_greedy(patterns, demands)
    
    def _solve_master_ortools(self, patterns: List[CuttingPattern], demands: List[int]) -> Tuple[List[float], float]:
        """Solve using Google OR-Tools (best option)"""
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            solver = pywraplp.Solver.CreateSolver('CBC')
        if not solver:
            raise Exception("No OR-Tools solver available")
            
        # Decision variables: how many times to use each pattern
        x = []
        for i in range(len(patterns)):
            x.append(solver.IntVar(0, solver.infinity(), f'x_{i}'))
        
        # Constraints: satisfy all demands
        for piece_idx in range(len(demands)):
            constraint = solver.Constraint(demands[piece_idx], solver.infinity())
            for pattern_idx, pattern in enumerate(patterns):
                count = sum(1 for piece in pattern.pieces if piece.piece_id == piece_idx)
                constraint.SetCoefficient(x[pattern_idx], count)
        
        # Objective: minimize total surfaces used
        objective = solver.Objective()
        for i in range(len(patterns)):
            objective.SetCoefficient(x[i], 1)
        objective.SetMinimization()
        
        # Solve
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            solution = [x[i].solution_value() for i in range(len(patterns))]
            return solution, solver.Objective().Value()
        else:
            raise Exception("OR-Tools solver failed to find optimal solution")
    
    def _solve_master_python_mip(self, patterns: List[CuttingPattern], demands: List[int]) -> Tuple[List[float], float]:
        """Solve using Python-MIP with CBC solver"""
        model = Model(solver_name=CBC)
        
        # Decision variables
        x = [model.add_var(var_type=INTEGER, lb=0, name=f'x_{i}') for i in range(len(patterns))]
        
        # Constraints: satisfy all demands
        for piece_idx in range(len(demands)):
            model += xsum(
                sum(1 for piece in patterns[pattern_idx].pieces if piece.piece_id == piece_idx) * x[pattern_idx]
                for pattern_idx in range(len(patterns))
            ) >= demands[piece_idx]
        
        # Objective: minimize total surfaces
        model.objective = minimize(xsum(x))
        
        # Solve
        status = model.optimize()
        
        if status.name == 'OPTIMAL':
            solution = [x[i].x for i in range(len(patterns))]
            return solution, model.objective_value
        else:
            raise Exception("Python-MIP solver failed")
    
    def _solve_master_scipy(self, patterns: List[CuttingPattern], demands: List[int]) -> Tuple[List[float], float]:
        """Solve using SciPy (LP relaxation fallback)"""
        # Build constraint matrix A and bounds b for A @ x >= b
        num_patterns = len(patterns)
        num_pieces = len(demands)
        
        A = np.zeros((num_pieces, num_patterns))
        for pattern_idx, pattern in enumerate(patterns):
            for piece in pattern.pieces:
                if piece.piece_id < num_pieces:
                    A[piece.piece_id, pattern_idx] += 1
        
        # Objective: minimize sum of x (number of surfaces)
        c = np.ones(num_patterns)
        
        # Constraints: -A @ x <= -demands (equivalent to A @ x >= demands)
        A_ub = -A
        b_ub = -np.array(demands)
        
        # Bounds: x >= 0
        bounds = [(0, None) for _ in range(num_patterns)]
        
        # Solve LP relaxation
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if result.success:
            # Round up to get integer solution (may be suboptimal)
            solution = [max(0, np.ceil(x)) for x in result.x]
            return solution, sum(solution)
        else:
            raise Exception("SciPy solver failed")
    
    def _solve_master_greedy(self, patterns: List[CuttingPattern], demands: List[int]) -> Tuple[List[float], float]:
        """Greedy fallback when all solvers fail"""
        remaining_demands = demands.copy()
        solution = [0] * len(patterns)
        
        while any(d > 0 for d in remaining_demands):
            # Find pattern that satisfies most remaining demand
            best_pattern = 0
            best_score = 0
            
            for pattern_idx, pattern in enumerate(patterns):
                score = 0
                for piece in pattern.pieces:
                    if piece.piece_id < len(remaining_demands) and remaining_demands[piece.piece_id] > 0:
                        score += 1
                        
                if score > best_score:
                    best_score = score
                    best_pattern = pattern_idx
            
            if best_score == 0:
                break
                
            # Use this pattern
            solution[best_pattern] += 1
            for piece in patterns[best_pattern].pieces:
                if piece.piece_id < len(remaining_demands):
                    remaining_demands[piece.piece_id] = max(0, remaining_demands[piece.piece_id] - 1)
        
        return solution, sum(solution)


class IndustrialCuttingOptimizer(CuttingAlgorithm):
    """
    Industrial-grade cutting optimizer that automatically selects the best approach
    based on problem size and complexity
    """
    
    def __init__(self, 
                 max_iterations: int = 100,
                 time_limit: float = 300.0,  # 5 minutes default
                 gap_tolerance: float = 0.01):  # 1% gap tolerance
        super().__init__()
        self.max_iterations = max_iterations
        self.time_limit = time_limit
        self.gap_tolerance = gap_tolerance
        self.column_solver = ColumnGenerationSolver()
        
    def optimize(self, 
                 surface: Surface, 
                 pieces: List[Piece],
                 **kwargs) -> CuttingResult:
        """
        Optimize cutting problem using the best available approach
        
        Automatically determines:
        - Problem complexity (simple/medium/complex)
        - Best algorithm (heuristic/hybrid/column generation)
        - Optimal solver configuration
        """
        start_time = time.time()
        
        # Analyze problem complexity
        complexity = self._analyze_problem_complexity(surface, pieces)
        
        # Select optimization strategy
        if complexity == "simple":
            result = self._solve_simple_problem(surface, pieces)
        elif complexity == "medium":
            result = self._solve_medium_problem(surface, pieces)
        else:  # complex
            result = self._solve_complex_problem(surface, pieces)
        
        computation_time = time.time() - start_time
        
        # Add quality metrics
        quality = self._calculate_solution_quality(result, computation_time, complexity)
        result.metadata = result.metadata or {}
        result.metadata['quality_metrics'] = quality
        
        return result
    
    def _analyze_problem_complexity(self, surface: Surface, pieces: List[Piece]) -> str:
        """Analyze problem to determine optimal solving approach"""
        num_pieces = len(pieces)
        total_demand = sum(getattr(piece, 'quantity', 1) for piece in pieces)
        
        # Calculate complexity factors
        surface_area = surface.width * surface.height
        total_pieces_area = sum(piece.width * piece.height * getattr(piece, 'quantity', 1) 
                               for piece in pieces)
        
        area_ratio = total_pieces_area / surface_area if surface_area > 0 else 0
        
        # Determine complexity
        if num_pieces <= 20 and total_demand <= 50:
            return "simple"
        elif num_pieces <= 100 and total_demand <= 500 and area_ratio <= 10:
            return "medium"
        else:
            return "complex"
    
    def _solve_simple_problem(self, surface: Surface, pieces: List[Piece]) -> CuttingResult:
        """Solve simple problems with fast heuristics"""
        from ..advanced.genetic import GeneticAlgorithm
        
        genetic = GeneticAlgorithm(
            population_size=50,
            generations=100,
            mutation_rate=0.1
        )
        
        return genetic.optimize(surface, pieces)
    
    def _solve_medium_problem(self, surface: Surface, pieces: List[Piece]) -> CuttingResult:
        """Solve medium problems with hybrid approach"""
        from ..advanced.hybrid_genetic import HybridGeneticAlgorithm
        
        hybrid = HybridGeneticAlgorithm(
            population_size=100,
            generations=200,
            mutation_rate=0.1,
            local_search_prob=0.3
        )
        
        return hybrid.optimize(surface, pieces)
    
    def _solve_complex_problem(self, surface: Surface, pieces: List[Piece]) -> CuttingResult:
        """Solve complex industrial problems with Column Generation"""
        return self._column_generation_solve(surface, pieces)
    
    def _column_generation_solve(self, surface: Surface, pieces: List[Piece]) -> CuttingResult:
        """
        Solve using Column Generation approach for large industrial problems
        """
        # Prepare piece demands
        piece_demands = {}
        for piece in pieces:
            key = (piece.width, piece.height)
            piece_demands[key] = piece_demands.get(key, 0) + getattr(piece, 'quantity', 1)
        
        unique_pieces = list(piece_demands.keys())
        demands = list(piece_demands.values())
        
        # Initialize with simple patterns (one piece per surface)
        patterns = []
        for i, (width, height) in enumerate(unique_pieces):
            if width <= surface.width and height <= surface.height:
                pattern_pieces = [Piece(width, height, piece_id=i)]
                pattern = CuttingPattern(surface_id=0, pieces=pattern_pieces)
                patterns.append(pattern)
        
        best_objective = float('inf')
        iteration = 0
        start_time = time.time()
        
        while iteration < self.max_iterations:
            if time.time() - start_time > self.time_limit:
                break
                
            # Solve master problem
            try:
                solution, objective = self.column_solver.solve_master_problem(patterns, demands)
                
                if objective < best_objective:
                    best_objective = objective
                    best_solution = solution
                
                # Check for convergence
                if iteration > 0 and abs(objective - best_objective) / best_objective < self.gap_tolerance:
                    break
                    
            except Exception as e:
                print(f"Column generation iteration {iteration} failed: {e}")
                break
            
            # Generate new columns (simplified pricing problem)
            new_pattern = self._solve_pricing_problem(surface, unique_pieces, demands)
            if new_pattern and self._is_pattern_beneficial(new_pattern, patterns):
                patterns.append(new_pattern)
            else:
                break  # No beneficial patterns found
                
            iteration += 1
        
        # Convert solution to CuttingResult
        return self._build_cutting_result(surface, patterns, best_solution, unique_pieces)
    
    def _solve_pricing_problem(self, surface: Surface, unique_pieces: List[Tuple], demands: List[int]) -> Optional[CuttingPattern]:
        """
        Simplified pricing problem: find the best combination of pieces for one surface
        Using a greedy knapsack-like approach
        """
        # Sort pieces by value density (area / demand satisfaction)
        piece_values = []
        for i, (width, height) in enumerate(unique_pieces):
            if demands[i] > 0:
                area = width * height
                value_density = area / demands[i]
                piece_values.append((value_density, i, width, height))
        
        piece_values.sort(reverse=True)
        
        # Greedy packing
        pattern_pieces = []
        remaining_width = surface.width
        remaining_height = surface.height
        
        for _, piece_id, width, height in piece_values:
            if width <= remaining_width and height <= remaining_height:
                pattern_pieces.append(Piece(width, height, piece_id=piece_id))
                # Simplified space update (can be improved)
                if width == remaining_width:
                    remaining_height -= height
                else:
                    remaining_width -= width
        
        if pattern_pieces:
            return CuttingPattern(surface_id=0, pieces=pattern_pieces)
        return None
    
    def _is_pattern_beneficial(self, new_pattern: CuttingPattern, existing_patterns: List[CuttingPattern]) -> bool:
        """Check if new pattern is significantly different from existing ones"""
        new_signature = self._get_pattern_signature(new_pattern)
        
        for pattern in existing_patterns:
            existing_signature = self._get_pattern_signature(pattern)
            if new_signature == existing_signature:
                return False
        
        return True
    
    def _get_pattern_signature(self, pattern: CuttingPattern) -> Tuple:
        """Get a signature for pattern comparison"""
        piece_counts = {}
        for piece in pattern.pieces:
            key = (piece.width, piece.height, piece.piece_id)
            piece_counts[key] = piece_counts.get(key, 0) + 1
        
        return tuple(sorted(piece_counts.items()))
    
    def _build_cutting_result(self, 
                             surface: Surface, 
                             patterns: List[CuttingPattern], 
                             solution: List[float],
                             unique_pieces: List[Tuple]) -> CuttingResult:
        """Convert column generation solution to CuttingResult"""
        used_surfaces = []
        total_area_used = 0
        
        for pattern_idx, usage in enumerate(solution):
            if usage > 0.5:  # Use pattern if usage is significant
                for _ in range(int(round(usage))):
                    # Create surface with pieces from this pattern
                    surface_copy = Surface(surface.width, surface.height)
                    
                    for piece in patterns[pattern_idx].pieces:
                        total_area_used += piece.width * piece.height
                        
                    used_surfaces.append(patterns[pattern_idx])
        
        # Calculate efficiency
        total_surface_area = len(used_surfaces) * surface.width * surface.height
        efficiency = (total_area_used / total_surface_area * 100) if total_surface_area > 0 else 0
        
        return CuttingResult(
            patterns=used_surfaces,
            total_surfaces_used=len(used_surfaces),
            efficiency=efficiency,
            total_waste=total_surface_area - total_area_used,
            algorithm_name="Industrial Column Generation"
        )
    
    def _calculate_solution_quality(self, 
                                   result: CuttingResult, 
                                   computation_time: float,
                                   complexity: str) -> SolutionQuality:
        """Calculate comprehensive solution quality metrics"""
        waste_percentage = 100 - result.efficiency
        
        # Determine algorithm used based on complexity and result
        if complexity == "simple":
            algorithm_used = "Genetic Algorithm (Fast)"
        elif complexity == "medium":
            algorithm_used = "Hybrid Genetic Algorithm"
        else:
            algorithm_used = "Column Generation (Industrial)"
        
        return SolutionQuality(
            efficiency=result.efficiency,
            waste_percentage=waste_percentage,
            total_surfaces=result.total_surfaces_used,
            computation_time=computation_time,
            algorithm_used=algorithm_used,
            problem_complexity=complexity
        ) 