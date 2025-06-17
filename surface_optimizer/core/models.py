"""
Core models for Surface Cutting Optimizer
Enhanced data structures with logging and advanced features
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from .geometry import Shape, Rectangle, Circle
from .exceptions import InvalidDimensionsError, ValidationError
import json


class MaterialType(Enum):
    """Types of materials that can be cut"""
    GLASS = "glass"
    METAL = "metal" 
    WOOD = "wood"
    PLASTIC = "plastic"
    FABRIC = "fabric"
    LEATHER = "leather"
    PAPER = "paper"
    CERAMIC = "ceramic"
    COMPOSITE = "composite"
    
    @classmethod
    def from_string(cls, value: str) -> 'MaterialType':
        """Create MaterialType from string"""
        for material in cls:
            if material.value.lower() == value.lower():
                return material
        raise ValueError(f"Unknown material type: {value}")


class Priority(Enum):
    """Order priority levels with weights"""
    LOW = (1, "Low Priority")
    MEDIUM = (2, "Medium Priority")
    HIGH = (3, "High Priority")
    URGENT = (4, "Urgent")
    
    def __init__(self, weight: int, description: str):
        self.weight = weight
        self.description = description
    
    @classmethod
    def from_weight(cls, weight: int) -> 'Priority':
        """Get priority from weight value"""
        for priority in cls:
            if priority.weight == weight:
                return priority
        raise ValueError(f"Unknown priority weight: {weight}")


class StockStatus(Enum):
    """Stock availability status"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_USE = "in_use"
    DEPLETED = "depleted"
    MAINTENANCE = "maintenance"


class OrderStatus(Enum):
    """Order processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


@dataclass
class MaterialProperties:
    """Properties specific to material types"""
    density: float = 1.0  # kg/m²
    cost_per_area: float = 0.0  # currency per m²
    cutting_speed: float = 1.0  # relative cutting speed
    tool_wear_factor: float = 1.0  # tool wear multiplier
    waste_factor: float = 0.05  # expected waste percentage
    min_piece_size: float = 50.0  # minimum useful piece size (mm)
    max_piece_size: float = 5000.0  # maximum piece size (mm)
    
    @classmethod
    def get_default_properties(cls, material_type: MaterialType) -> 'MaterialProperties':
        """Get default properties for material type"""
        defaults = {
            MaterialType.GLASS: cls(density=2.5, cost_per_area=15.0, cutting_speed=0.8, waste_factor=0.08),
            MaterialType.METAL: cls(density=7.8, cost_per_area=25.0, cutting_speed=0.6, waste_factor=0.05),
            MaterialType.WOOD: cls(density=0.6, cost_per_area=10.0, cutting_speed=1.2, waste_factor=0.10),
            MaterialType.PLASTIC: cls(density=1.4, cost_per_area=8.0, cutting_speed=1.0, waste_factor=0.06),
            MaterialType.FABRIC: cls(density=0.3, cost_per_area=20.0, cutting_speed=1.5, waste_factor=0.15),
        }
        return defaults.get(material_type, cls())


@dataclass
class Stock:
    """Enhanced stock representation with tracking and validation"""
    id: str
    width: float
    height: float
    thickness: float = 6.0  # mm
    material_type: MaterialType = MaterialType.GLASS
    cost_per_unit: float = 0.0
    location: str = ""
    status: StockStatus = StockStatus.AVAILABLE
    material_properties: Optional[MaterialProperties] = None
    purchase_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    supplier: str = ""
    batch_number: str = ""
    quality_grade: str = "A"
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise InvalidDimensionsError(f"Stock dimensions must be positive: {self.width}x{self.height}")
        
        if self.thickness <= 0:
            raise InvalidDimensionsError(f"Stock thickness must be positive: {self.thickness}")
        
        if self.material_properties is None:
            self.material_properties = MaterialProperties.get_default_properties(self.material_type)
    
    @property
    def area(self) -> float:
        """Calculate area in mm²"""
        return self.width * self.height
    
    @property
    def area_m2(self) -> float:
        """Calculate area in m²"""
        return self.area / 1_000_000
    
    @property
    def volume(self) -> float:
        """Calculate volume in mm³"""
        return self.area * self.thickness
    
    @property
    def weight_kg(self) -> float:
        """Estimate weight in kg"""
        return self.area_m2 * self.thickness * self.material_properties.density / 1000
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost"""
        if self.cost_per_unit > 0:
            return self.cost_per_unit
        return self.area_m2 * self.material_properties.cost_per_area
    
    @property
    def is_available(self) -> bool:
        """Check if stock is available for use"""
        return self.status == StockStatus.AVAILABLE
    
    @property
    def is_expired(self) -> bool:
        """Check if stock has expired"""
        if self.expiry_date is None:
            return False
        return datetime.now() > self.expiry_date
    
    def can_fit_shape(self, shape: Shape) -> bool:
        """Check if a shape can fit in this stock"""
        if isinstance(shape, Rectangle):
            return shape.fits_in_rectangle(self.width, self.height)
        elif isinstance(shape, Circle):
            return (2 * shape.radius <= self.width and 
                   2 * shape.radius <= self.height)
        return False
    
    def reserve(self) -> bool:
        """Reserve this stock for use"""
        if self.status == StockStatus.AVAILABLE:
            self.status = StockStatus.RESERVED
            return True
        return False
    
    def release(self) -> bool:
        """Release stock back to available"""
        if self.status == StockStatus.RESERVED:
            self.status = StockStatus.AVAILABLE
            return True
        return False
    
    def validate(self) -> List[str]:
        """Validate stock and return list of issues"""
        issues = []
        
        if self.is_expired:
            issues.append(f"Stock {self.id} has expired")
        
        if not self.is_available:
            issues.append(f"Stock {self.id} is not available (status: {self.status.value})")
        
        if self.area < 1000:  # Less than 1000 mm²
            issues.append(f"Stock {self.id} area is very small: {self.area:.1f} mm²")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "thickness": self.thickness,
            "material_type": self.material_type.value,
            "cost_per_unit": self.cost_per_unit,
            "location": self.location,
            "status": self.status.value,
            "area": self.area,
            "total_cost": self.total_cost,
            "tags": self.tags,
            "notes": self.notes
        }
    
    def __str__(self):
        return f"Stock({self.id}: {self.width}x{self.height}x{self.thickness}mm, {self.material_type.value}, {self.status.value})"


@dataclass
class Order:
    """Enhanced order representation with tracking and validation"""
    id: str
    shape: Shape
    quantity: int = 1
    priority: Priority = Priority.MEDIUM
    material_type: MaterialType = MaterialType.GLASS
    thickness: float = 6.0  # mm
    tolerance: float = 1.0  # mm allowable error
    customer_id: str = ""
    order_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    special_requirements: Dict[str, Any] = field(default_factory=dict)
    unit_price: float = 0.0
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise InvalidDimensionsError(f"Order quantity must be positive: {self.quantity}")
        
        if self.tolerance < 0:
            raise InvalidDimensionsError(f"Tolerance cannot be negative: {self.tolerance}")
        
        if self.order_date is None:
            self.order_date = datetime.now()
    
    @property
    def total_area(self) -> float:
        """Calculate total area needed"""
        return self.shape.area() * self.quantity
    
    @property
    def total_value(self) -> float:
        """Calculate total order value"""
        return self.unit_price * self.quantity
    
    @property
    def is_urgent(self) -> bool:
        """Check if order is urgent"""
        return self.priority == Priority.URGENT
    
    @property
    def is_overdue(self) -> bool:
        """Check if order is overdue"""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date
    
    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date"""
        if self.due_date is None:
            return None
        delta = self.due_date - datetime.now()
        return delta.days
    
    def can_be_fulfilled_by_stock(self, stock: Stock) -> bool:
        """Check if this order can be fulfilled by given stock"""
        return (self.material_type == stock.material_type and
                abs(self.thickness - stock.thickness) <= self.tolerance and
                stock.can_fit_shape(self.shape))
    
    def mark_fulfilled(self, fulfilled_quantity: int = None):
        """Mark order as fulfilled"""
        if fulfilled_quantity is None or fulfilled_quantity >= self.quantity:
            self.status = OrderStatus.FULFILLED
        else:
            self.status = OrderStatus.PARTIALLY_FULFILLED
    
    def validate(self) -> List[str]:
        """Validate order and return list of issues"""
        issues = []
        
        if self.is_overdue:
            issues.append(f"Order {self.id} is overdue")
        
        if self.days_until_due is not None and self.days_until_due <= 1:
            issues.append(f"Order {self.id} is due soon ({self.days_until_due} days)")
        
        if self.total_area > 10_000_000:  # More than 10 m²
            issues.append(f"Order {self.id} has very large area: {self.total_area/1_000_000:.1f} m²")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "quantity": self.quantity,
            "priority": self.priority.name,
            "material_type": self.material_type.value,
            "thickness": self.thickness,
            "tolerance": self.tolerance,
            "customer_id": self.customer_id,
            "status": self.status.value,
            "total_area": self.total_area,
            "total_value": self.total_value,
            "is_urgent": self.is_urgent,
            "days_until_due": self.days_until_due,
            "tags": self.tags,
            "notes": self.notes
        }
    
    def __str__(self):
        return f"Order({self.id}: {self.shape} x{self.quantity}, {self.priority.name}, {self.status.value})"


@dataclass
class PlacedShape:
    """Enhanced placed shape with metadata"""
    order_id: str
    shape: Shape
    stock_id: str
    placement_time: datetime = field(default_factory=datetime.now)
    rotation_applied: float = 0.0  # degrees
    cutting_sequence: int = 0
    estimated_cutting_time: float = 0.0  # minutes
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get position as tuple"""
        return (self.shape.x, self.shape.y)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "order_id": self.order_id,
            "stock_id": self.stock_id,
            "position": self.position,
            "area": self.shape.area(),
            "rotation_applied": self.rotation_applied,
            "cutting_sequence": self.cutting_sequence,
            "estimated_cutting_time": self.estimated_cutting_time
        }
    
    def __str__(self):
        return f"PlacedShape({self.order_id} on {self.stock_id} at {self.shape.x:.1f},{self.shape.y:.1f})"


@dataclass
class CuttingResult:
    """Enhanced cutting optimization results"""
    total_stock_used: int = 0
    total_orders_fulfilled: int = 0
    total_waste_area: float = 0.0
    efficiency_percentage: float = 0.0
    placed_shapes: List[PlacedShape] = field(default_factory=list)
    unfulfilled_orders: List[Order] = field(default_factory=list)
    algorithm_used: str = ""
    computation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    optimization_date: datetime = field(default_factory=datetime.now)
    total_cost: float = 0.0
    estimated_cutting_time: float = 0.0  # total cutting time in minutes
    
    @property
    def total_area_used(self) -> float:
        """Calculate total area of placed shapes"""
        return sum(ps.shape.area() for ps in self.placed_shapes)
    
    @property
    def waste_percentage(self) -> float:
        """Calculate waste percentage"""
        return 100.0 - self.efficiency_percentage
    
    @property
    def cost_per_area(self) -> float:
        """Calculate cost per unit area"""
        if self.total_area_used > 0:
            return self.total_cost / (self.total_area_used / 1_000_000)  # per m²
        return 0.0
    
    @property
    def fulfillment_rate(self) -> float:
        """Calculate order fulfillment rate"""
        total_orders = self.total_orders_fulfilled + len(self.unfulfilled_orders)
        if total_orders > 0:
            return (self.total_orders_fulfilled / total_orders) * 100
        return 100.0
    
    def get_shapes_by_stock(self, stock_id: str) -> List[PlacedShape]:
        """Get all shapes placed on a specific stock"""
        return [ps for ps in self.placed_shapes if ps.stock_id == stock_id]
    
    def get_stock_efficiency(self, stock_id: str, stock_area: float) -> float:
        """Calculate efficiency for a specific stock"""
        shapes_on_stock = self.get_shapes_by_stock(stock_id)
        used_area = sum(ps.shape.area() for ps in shapes_on_stock)
        return (used_area / stock_area * 100) if stock_area > 0 else 0.0
    
    def get_material_summary(self) -> Dict[MaterialType, Dict[str, Any]]:
        """Get summary by material type"""
        summary = {}
        
        # Group by material type
        for order in self.unfulfilled_orders:
            mat = order.material_type
            if mat not in summary:
                summary[mat] = {
                    "orders_unfulfilled": 0,
                    "area_unfulfilled": 0.0,
                    "orders_fulfilled": 0,
                    "area_fulfilled": 0.0
                }
            summary[mat]["orders_unfulfilled"] += 1
            summary[mat]["area_unfulfilled"] += order.total_area
        
        # Add fulfilled orders (would need order lookup)
        for placed in self.placed_shapes:
            # Note: This is simplified - in reality we'd need to lookup the original order
            pass
        
        return summary
    
    def export_summary(self, filepath: str):
        """Export result summary to JSON"""
        summary = {
            "optimization_date": self.optimization_date.isoformat(),
            "algorithm_used": self.algorithm_used,
            "computation_time": self.computation_time,
            "stocks_used": self.total_stock_used,
            "orders_fulfilled": self.total_orders_fulfilled,
            "orders_unfulfilled": len(self.unfulfilled_orders),
            "efficiency_percentage": self.efficiency_percentage,
            "waste_percentage": self.waste_percentage,
            "fulfillment_rate": self.fulfillment_rate,
            "total_cost": self.total_cost,
            "cost_per_area": self.cost_per_area,
            "estimated_cutting_time": self.estimated_cutting_time,
            "placed_shapes": [ps.to_dict() for ps in self.placed_shapes],
            "metadata": self.metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def __str__(self):
        return (f"CuttingResult(Stocks: {self.total_stock_used}, "
                f"Orders: {self.total_orders_fulfilled}/{self.total_orders_fulfilled + len(self.unfulfilled_orders)}, "
                f"Efficiency: {self.efficiency_percentage:.1f}%)")


@dataclass
class OptimizationConfig:
    """Enhanced configuration for optimization algorithms"""
    allow_rotation: bool = True
    cutting_width: float = 3.0  # kerf width in mm
    min_waste_size: float = 100.0  # minimum useful waste size
    max_computation_time: float = 60.0  # seconds
    prioritize_orders: bool = True
    algorithm_name: str = "bottom_left"
    
    # Advanced options
    enable_nesting: bool = False  # Allow shapes inside other shapes
    minimize_cuts: bool = False  # Prefer fewer cuts over efficiency
    group_by_thickness: bool = True  # Group orders by thickness
    group_by_material: bool = True  # Group orders by material
    allow_partial_fulfillment: bool = True  # Allow partial order fulfillment
    
    # Quality settings
    placement_precision: float = 0.1  # mm precision for placement
    angle_precision: float = 1.0  # degree precision for rotation
    
    # Performance settings
    max_iterations: int = 10000
    enable_parallel_processing: bool = False
    cache_calculations: bool = True
    
    # Cost optimization
    optimize_for_cost: bool = False
    optimize_for_time: bool = False
    waste_penalty_factor: float = 1.0
    
    def validate(self) -> List[str]:
        """Validate configuration"""
        issues = []
        
        if self.cutting_width < 0:
            issues.append("Cutting width cannot be negative")
        
        if self.max_computation_time <= 0:
            issues.append("Max computation time must be positive")
        
        if self.placement_precision <= 0:
            issues.append("Placement precision must be positive")
        
        if not (0 <= self.waste_penalty_factor <= 10):
            issues.append("Waste penalty factor should be between 0 and 10")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "allow_rotation": self.allow_rotation,
            "cutting_width": self.cutting_width,
            "min_waste_size": self.min_waste_size,
            "max_computation_time": self.max_computation_time,
            "prioritize_orders": self.prioritize_orders,
            "algorithm_name": self.algorithm_name,
            "enable_nesting": self.enable_nesting,
            "minimize_cuts": self.minimize_cuts,
            "group_by_thickness": self.group_by_thickness,
            "group_by_material": self.group_by_material,
            "placement_precision": self.placement_precision,
            "optimize_for_cost": self.optimize_for_cost,
            "optimize_for_time": self.optimize_for_time
        }


@dataclass
class Surface:
    """Simple surface representation for cutting optimization"""
    width: float
    height: float
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise InvalidDimensionsError(f"Surface dimensions must be positive: {self.width}x{self.height}")
    
    @property
    def area(self) -> float:
        """Calculate surface area"""
        return self.width * self.height
    
    def __str__(self):
        return f"Surface({self.width}x{self.height})"


@dataclass  
class Piece:
    """Simple piece representation for cutting optimization"""
    width: float
    height: float
    piece_id: int = 0
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise InvalidDimensionsError(f"Piece dimensions must be positive: {self.width}x{self.height}")
    
    @property
    def area(self) -> float:
        """Calculate piece area"""
        return self.width * self.height
    
    def __str__(self):
        return f"Piece({self.width}x{self.height}, id={self.piece_id})"


@dataclass
class CuttingPattern:
    """Cutting pattern for column generation algorithms"""
    surface_id: int
    pieces: List[Piece] = field(default_factory=list)
    
    @property
    def total_area(self) -> float:
        """Calculate total area of pieces in pattern"""
        return sum(piece.area for piece in self.pieces)
    
    def __str__(self):
        return f"CuttingPattern(surface={self.surface_id}, pieces={len(self.pieces)})" 