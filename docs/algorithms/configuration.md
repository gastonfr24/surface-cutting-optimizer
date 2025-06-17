# ⚙️ Algorithm Configuration

## 📋 **Overview**

The Surface Cutting Optimizer provides comprehensive configuration options to fine-tune algorithm behavior for specific use cases. Each algorithm can be customized through the `OptimizationConfig` class to achieve optimal performance for your particular cutting requirements.

## 🎛️ **OptimizationConfig Class**

### Core Configuration
```python
from surface_optimizer.core.models import OptimizationConfig

config = OptimizationConfig(
    # Basic parameters
    allow_rotation=True,
    precision_tolerance=0.001,
    max_computation_time=60,
    
    # Algorithm-specific
    algorithm_specific_params={},
    
    # Performance
    parallel_processing=True,
    memory_optimization=False
)
```

## 🔧 **Universal Parameters**

### Basic Settings
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_rotation` | bool | True | Allow 90° rotation of pieces |
| `precision_tolerance` | float | 0.001 | Floating point precision (mm) |
| `max_computation_time` | int | 60 | Maximum time in seconds |
| `early_termination` | bool | True | Stop early if target reached |

### Material Constraints
```python
material_config = OptimizationConfig(
    # Material properties
    material_thickness=10.0,        # Material thickness (mm)
    cutting_blade_width=3.0,        # Kerf width (mm)
    edge_margin=5.0,               # Minimum edge distance (mm)
    
    # Material compatibility
    enforce_grain_direction=True,   # Wood grain alignment
    material_waste_factor=0.05,    # 5% waste allowance
    
    # Cutting constraints
    max_cutting_length=3000,       # Maximum cut length (mm)
    min_piece_size=50,             # Minimum viable piece size (mm)
)
```

### Performance Optimization
```python
performance_config = OptimizationConfig(
    # Processing
    parallel_processing=True,       # Use multiple cores
    max_threads=4,                 # Maximum thread count
    memory_optimization=True,      # Optimize memory usage
    
    # Caching
    enable_caching=True,           # Cache intermediate results
    cache_size_limit=1000,         # Maximum cache entries
    
    # Progress tracking
    progress_callback=None,        # Progress callback function
    verbose_logging=False          # Detailed logging
)
```

## 🎯 **Algorithm-Specific Configurations**

### Basic Algorithms

#### First Fit Configuration
```python
first_fit_config = OptimizationConfig(
    algorithm_specific_params={
        'scan_direction': 'left_to_right',  # 'left_to_right', 'top_to_bottom'
        'position_strategy': 'first_valid',  # 'first_valid', 'best_corner'
        'sort_pieces': False,               # Sort pieces before placement
        'sort_criterion': 'area_desc'       # 'area_desc', 'width_desc', 'height_desc'
    },
    
    # Speed optimization
    precision_tolerance=1.0,        # Lower precision for speed
    max_computation_time=1,         # 1 second limit
    parallel_processing=True
)
```

#### Best Fit Configuration
```python
best_fit_config = OptimizationConfig(
    algorithm_specific_params={
        'fit_strategy': 'minimum_waste',    # 'minimum_waste', 'maximum_density'
        'tie_breaking': 'smallest_stock',   # 'smallest_stock', 'largest_stock'
        'look_ahead': 2,                    # Positions to look ahead
        'waste_threshold': 0.1              # Minimum waste to consider
    },
    
    # Balanced performance
    precision_tolerance=0.5,
    max_computation_time=5
)
```

#### Bottom Left Configuration
```python
bottom_left_config = OptimizationConfig(
    algorithm_specific_params={
        'placement_priority': 'bottom_first', # 'bottom_first', 'left_first'
        'compaction_strategy': 'horizontal',  # 'horizontal', 'vertical', 'both'
        'overlap_resolution': 'strict',       # 'strict', 'relaxed'
        'corner_optimization': True           # Optimize corner placements
    },
    
    # Quality focus
    precision_tolerance=0.1,
    max_computation_time=10
)
```

### Advanced Algorithms

#### Genetic Algorithm Configuration
```python
genetic_config = OptimizationConfig(
    algorithm_specific_params={
        # Population parameters
        'population_size': 50,              # Population size
        'generations': 100,                 # Maximum generations
        'auto_scaling': True,               # Enable auto-scaling
        
        # Genetic operators
        'crossover_rate': 0.8,             # Crossover probability
        'mutation_rate': 0.1,              # Mutation probability
        'elitism_rate': 0.1,               # Elite preservation
        
        # Selection
        'selection_method': 'tournament',   # 'tournament', 'roulette', 'rank'
        'tournament_size': 3,               # Tournament selection size
        
        # Convergence
        'convergence_patience': 10,         # Generations without improvement
        'target_efficiency': 0.85,          # Target efficiency to stop
        'min_improvement': 0.01,            # Minimum improvement threshold
        
        # Initialization
        'initialization_strategy': 'mixed', # 'random', 'greedy', 'mixed'
        'seed_best_heuristics': True,       # Seed with heuristic solutions
        
        # Advanced features
        'adaptive_parameters': True,        # Adapt parameters during evolution
        'local_search': False,              # Apply local search to best solutions
        'parallel_evaluation': True         # Parallel fitness evaluation
    },
    
    # Performance settings
    max_computation_time=60,
    parallel_processing=True,
    memory_optimization=True
)
```

#### Simulated Annealing Configuration
```python
simulated_annealing_config = OptimizationConfig(
    algorithm_specific_params={
        # Temperature schedule
        'initial_temperature': 1000.0,     # Starting temperature
        'final_temperature': 0.1,          # End temperature
        'cooling_rate': 0.95,              # Temperature reduction factor
        'cooling_schedule': 'exponential',  # 'exponential', 'linear', 'adaptive'
        
        # Iteration control
        'max_iterations': 10000,           # Maximum iterations
        'iterations_per_temp': 100,        # Iterations at each temperature
        'auto_scaling': True,              # Enable auto-scaling
        
        # Neighbor generation
        'neighbor_strategy': 'mixed',       # 'swap', 'insert', 'rotate', 'mixed'
        'neighbor_probability': {           # Probability for each strategy
            'swap': 0.4,
            'insert': 0.3,
            'rotate': 0.2,
            'reposition': 0.1
        },
        
        # Acceptance criteria
        'acceptance_strategy': 'metropolis', # 'metropolis', 'boltzmann'
        'reheat_threshold': 0.95,           # Reheat if acceptance < threshold
        'reheat_factor': 1.5,               # Temperature increase factor
        
        # Convergence
        'equilibrium_threshold': 0.01,      # Thermal equilibrium threshold
        'stagnation_limit': 1000,           # Iterations without improvement
        'target_efficiency': 0.90           # Target efficiency to stop
    },
    
    max_computation_time=120,
    parallel_processing=False  # SA is inherently sequential
)
```

## 🏭 **Industry-Specific Configurations**

### Furniture Manufacturing
```python
furniture_config = OptimizationConfig(
    # Material constraints
    enforce_grain_direction=True,
    material_thickness=18.0,        # Standard furniture board
    cutting_blade_width=3.0,
    edge_margin=2.0,
    
    # Cutting preferences
    algorithm_specific_params={
        'minimize_crosscuts': True,     # Reduce cross-grain cuts
        'group_similar_pieces': True,   # Group similar pieces together
        'optimize_cut_sequence': True,  # Optimize cutting order
        'waste_piece_threshold': 100   # Minimum size for waste pieces (mm²)
    },
    
    # Quality requirements
    precision_tolerance=0.5,        # Furniture-grade precision
    allow_rotation=True,
    max_computation_time=30
)
```

### Glass Cutting
```python
glass_config = OptimizationConfig(
    # Glass-specific constraints
    allow_rotation=False,           # Glass typically can't be rotated
    material_thickness=4.0,         # Standard glass thickness
    cutting_blade_width=1.0,        # Glass scoring width
    edge_margin=10.0,              # Safety margin for glass
    
    algorithm_specific_params={
        'minimize_stress_points': True,  # Reduce stress concentrations
        'avoid_small_strips': True,      # Avoid narrow strips
        'min_strip_width': 50,          # Minimum strip width (mm)
        'breaking_safety_factor': 1.2,  # Safety factor for breakage
        'cutting_pattern': 'straight_line' # Prefer straight cuts
    },
    
    # High precision required
    precision_tolerance=0.1,
    max_computation_time=45
)
```

### Metal Fabrication
```python
metal_config = OptimizationConfig(
    # Metal cutting constraints
    material_thickness=3.0,         # Sheet metal thickness
    cutting_blade_width=2.0,        # Plasma/laser kerf
    edge_margin=5.0,
    
    algorithm_specific_params={
        'optimize_cutting_path': True,   # Minimize torch travel
        'group_by_cutting_method': True, # Group by cutting tool
        'thermal_considerations': True,  # Consider heat effects
        'pierce_time_optimization': True, # Minimize pierce points
        'material_utilization_priority': 0.8 # 80% priority on material vs speed
    },
    
    # Medium precision
    precision_tolerance=0.2,
    allow_rotation=True,
    max_computation_time=60
)
```

### Textile Cutting
```python
textile_config = OptimizationConfig(
    # Textile-specific constraints
    material_thickness=2.0,
    cutting_blade_width=1.0,
    edge_margin=3.0,
    
    algorithm_specific_params={
        'respect_fabric_direction': True, # Maintain fabric grain
        'pattern_matching': True,        # Match patterns across pieces
        'minimize_waste_strips': True,   # Avoid small waste pieces
        'nesting_efficiency': 0.9,      # High nesting efficiency target
        'cutting_speed_optimization': True # Optimize for cutting speed
    },
    
    precision_tolerance=1.0,
    allow_rotation=False,           # Usually fixed orientation
    max_computation_time=20
)
```

## 🎮 **Configuration Presets**

### Quick Presets
```python
from surface_optimizer.core.models import ConfigurationPresets

# Ultra-fast preset (development/testing)
fast_config = ConfigurationPresets.ULTRA_FAST
# Equivalent to:
# OptimizationConfig(
#     algorithm_specific_params={'population_size': 10, 'generations': 20},
#     precision_tolerance=2.0,
#     max_computation_time=5,
#     allow_rotation=False
# )

# Balanced preset (general use)
balanced_config = ConfigurationPresets.BALANCED

# High-quality preset (production)
quality_config = ConfigurationPresets.HIGH_QUALITY

# Maximum efficiency preset (critical optimization)
max_efficiency_config = ConfigurationPresets.MAX_EFFICIENCY
```

### Custom Preset Creation
```python
def create_custom_preset(industry="general", priority="balanced"):
    """
    Create custom configuration preset
    """
    base_configs = {
        "speed": {
            "precision_tolerance": 2.0,
            "max_computation_time": 5,
            "algorithm_specific_params": {"population_size": 15, "generations": 25}
        },
        "balanced": {
            "precision_tolerance": 0.5,
            "max_computation_time": 30,
            "algorithm_specific_params": {"population_size": 30, "generations": 60}
        },
        "quality": {
            "precision_tolerance": 0.1,
            "max_computation_time": 120,
            "algorithm_specific_params": {"population_size": 60, "generations": 120}
        }
    }
    
    industry_modifiers = {
        "furniture": {"enforce_grain_direction": True, "edge_margin": 2.0},
        "glass": {"allow_rotation": False, "edge_margin": 10.0},
        "metal": {"optimize_cutting_path": True, "edge_margin": 5.0}
    }
    
    config = OptimizationConfig(**base_configs[priority])
    
    if industry in industry_modifiers:
        for key, value in industry_modifiers[industry].items():
            setattr(config, key, value)
    
    return config
```

## 🔍 **Configuration Validation**

### Automatic Validation
```python
def validate_configuration(config, orders, stock):
    """
    Validate configuration against problem constraints
    """
    warnings = []
    errors = []
    
    # Check precision vs problem size
    total_pieces = sum(order['quantity'] for order in orders)
    if total_pieces > 1000 and config.precision_tolerance < 0.1:
        warnings.append("High precision with large problem may be slow")
    
    # Check memory requirements
    if hasattr(config, 'population_size'):
        estimated_memory = config.population_size * total_pieces * 0.001  # MB
        if estimated_memory > 1000:  # > 1GB
            warnings.append(f"Estimated memory usage: {estimated_memory:.1f}MB")
    
    # Check time constraints
    if config.max_computation_time < 5 and total_pieces > 100:
        warnings.append("Short time limit for complex problem")
    
    # Check material constraints
    min_stock_area = min(s['width'] * s['height'] for s in stock)
    max_piece_area = max(o['width'] * o['height'] for o in orders)
    
    if max_piece_area > min_stock_area * 0.9:
        errors.append("Some pieces may not fit in available stock")
    
    return {'warnings': warnings, 'errors': errors}
```

### Configuration Optimization
```python
def optimize_configuration_for_problem(orders, stock, time_limit=None):
    """
    Automatically optimize configuration for specific problem
    """
    total_pieces = sum(order['quantity'] for order in orders)
    problem_complexity = total_pieces * len(stock)
    
    # Determine optimal algorithm
    if problem_complexity <= 50:
        algorithm = "first_fit"
        config = OptimizationConfig(
            precision_tolerance=1.0,
            max_computation_time=1
        )
    elif problem_complexity <= 200:
        algorithm = "best_fit"
        config = OptimizationConfig(
            precision_tolerance=0.5,
            max_computation_time=5
        )
    else:
        algorithm = "genetic"
        config = OptimizationConfig(
            algorithm_specific_params={
                'auto_scaling': True,
                'population_size': min(50, max(20, total_pieces // 10)),
                'generations': min(100, max(30, total_pieces // 5))
            },
            max_computation_time=time_limit or 60
        )
    
    return algorithm, config
```

## 📊 **Performance Tuning Guide**

### Speed Optimization
```python
speed_optimized_config = OptimizationConfig(
    # Reduce precision
    precision_tolerance=2.0,
    
    # Limit computation time
    max_computation_time=10,
    
    # Algorithm tweaks
    algorithm_specific_params={
        'population_size': 15,      # Smaller population
        'generations': 30,          # Fewer generations
        'early_stopping': True,     # Stop early
        'convergence_patience': 5   # Less patience
    },
    
    # Performance features
    parallel_processing=True,
    memory_optimization=True
)
```

### Quality Optimization
```python
quality_optimized_config = OptimizationConfig(
    # High precision
    precision_tolerance=0.01,
    
    # Extended computation time
    max_computation_time=300,
    
    # Algorithm tweaks
    algorithm_specific_params={
        'population_size': 100,     # Larger population
        'generations': 200,         # More generations
        'target_efficiency': 0.95,  # High target
        'convergence_patience': 20  # More patience
    },
    
    # Quality features
    allow_rotation=True,
    early_termination=False
)
```

## 🔗 **Configuration Templates**

### Template Generation
```python
def generate_configuration_template(use_case):
    """
    Generate configuration template for specific use case
    """
    templates = {
        "rapid_prototyping": {
            "algorithm": "first_fit",
            "config": OptimizationConfig(
                precision_tolerance=2.0,
                max_computation_time=1,
                allow_rotation=False
            )
        },
        
        "production_planning": {
            "algorithm": "genetic",
            "config": OptimizationConfig(
                algorithm_specific_params={
                    'auto_scaling': True,
                    'target_efficiency': 0.85
                },
                max_computation_time=60,
                precision_tolerance=0.1
            )
        },
        
        "cost_optimization": {
            "algorithm": "genetic",
            "config": OptimizationConfig(
                algorithm_specific_params={
                    'population_size': 75,
                    'generations': 150,
                    'target_efficiency': 0.95
                },
                max_computation_time=300,
                precision_tolerance=0.01
            )
        }
    }
    
    return templates.get(use_case, templates["production_planning"])
```

## 🔗 **References**

- **[Algorithm Overview](README.md)** - Complete algorithm comparison
- **[Basic Algorithms](basic/)** - Configuration for basic algorithms
- **[Advanced Algorithms](advanced/)** - Configuration for advanced algorithms
- **[Performance Guide](benchmarks.md)** - Performance optimization tips
- **[Troubleshooting](troubleshooting.md)** - Common configuration issues

---

**Related**: [Genetic Algorithm Configuration](advanced/genetic.md#advanced-configuration) | [Industry Examples](../examples/industry_specific.md) 