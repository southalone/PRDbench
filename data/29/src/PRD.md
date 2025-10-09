# Takeaway Order Delivery System PRD

## 1. Demand Overview
This project aims to develop a command-line interactive takeaway order delivery system simulator, achieving rider management, order allocation, route planning, and delivery status monitoring through intelligent algorithms. The system uses an 8x8 grid coordinate system, supporting multiple riders for concurrent delivery, and integrates a distance-first allocation strategy and grid-based path planning algorithm to provide a complete business process simulation and decision support for takeaway delivery services.

## 2. Basic Functionality Requirements

### 2.1 System Initialization and Resource Management Module
- Automatically initialize core parameters when the system starts:
  - System funds: 1,000 yuan (supports rider recruitment and operational costs)
  - Rider list: empty list (dynamic management of rider resources)
  - Rider ID counter: 0 (ensures uniqueness of rider IDs)
  - System operational status: True (controls main loop execution)
  - Grid map: 8x8 grid (800x800 coordinate system, 100x100 grid units, each full hundred grid points represent restaurant/customer locations, non-full hundred points represent roads, initial courier location on the road)
  - Simulated time lapse, with the main program containing a loop where each iteration represents a time unit (tick)
- Implement an automatic rider recruitment mechanism:
  - Trigger condition: automatically create a new rider when system funds ≥ 400 yuan
  - Recruitment cost: 300 yuan per rider (deducted from system funds)
  - Rider initial attributes: number (auto-increment), location (435, 3385), speed (10 units/frame), status (0=idle)

### 2.2 Rider Management Module
- Rider object data structure design:
  - Core attributes: rider_id (unique identifier), x/y coordinate (current location), speed (movement speed)
  - Status management: state (0=idle/1=pickup/2=delivery), orders (order list), special_case (special state flag)
- Rider status transition logic:
  - Idle (0) → Pickup (1): when a new order is assigned
  - Pickup (1) → Delivery (2): when arriving at restaurant coordinates
  - Delivery (2) → Idle (0): upon order completion
- Rider movement algorithm implementation:
  - Path planning based on grid coordinate system (prefers moving along streets)
  - Supports horizontal/vertical movement and handles special location cases

### 2.3 Order Management Module
- Order creation and coordinate transformation:
  - User input format: [Restaurant x, Restaurant y, Customer x, Customer y] (range 0-800)
  - Automatic coordinate transformation: converts input coordinates to grid center points
- Intelligent order allocation algorithm:
  - Allocation strategy: closest distance first (based on Euclidean distance calculation)
  - Calculation method: √[(rider_x - restaurant_x)² + (rider_y - restaurant_y)²]
  - Supports multi-rider competitive allocation, ensuring load balancing
- Order completion process:
  - Automatically remove completed orders from rider's order list
  - Update rider status to idle, freeing up rider resources
  - Record order completion time and delivery efficiency data

### 2.4 Path Planning and Navigation Module
- Grid-based path planning algorithm:
  - Based on an 8x8 grid system (100x100 grid units)
  - Prioritize street paths (align x or y coordinate to grid lines)
  - Supports right-angle turns and straight-line movement
- Special case handling mechanism:
  - Movement strategy for riders directly above/below the target point
  - Multi-target path optimization (continuous path from pickup → delivery)
  - Avoid path conflicts and deadlock situations

### 2.5 System Monitoring and Status Display Module
- Status monitoring features:
  - Display system fund balance
  - Count of riders and detailed information
  - Each rider's location, status, order quantity
- Command-line map visualization:
  - Display ASCII character map (8x8 grid)
  - Symbol mapping: 'R'=Rider, 'S'=Restaurant, 'C'=Customer, '.'=Empty space, '#'=Street
  - Support for viewing rider locations and order status

### 2.6 User Interaction and Command System
- Multi-level command menu system:
  - 'start' (order input): input four integer coordinates (near restaurant + near customer),
    - return restaurant, customer grid coordinates,
    - whether a new rider was added
    - accepted rider route map, speed, time used (line graph connected on ASCII character map),
  - 'status' (state): provides a snapshot of the current macro state of the simulated world, including system funds, all rider statuses (idle, picking up, delivering) and order list
  - 'orders' (order details): all order details, including start time, restaurant location, customer location, distance, time used, delivery rider
  - 'riders' (rider details): record each rider's status change, including the order received, reaching pickup point, delivery to customer details including time, location, order number
  - 'quit'/'exit' (exit)
  - Supports shortcut key operations and command history
- Input verification and error handling:
  - Coordinate range verification (0-800)
  - Input format validation (integer type)
  - System state consistency check
  - Graceful error prompt and recovery mechanism

## 3. Data Requirements

### 3.1 Core System Data
- Global variable management structure:
  - System funds (integer type, supports negative handling)
  - Rider list (dynamic array, supports CRUD operations)
  - Rider ID counter (auto-increment integer, ensuring uniqueness)
  - System operational status (boolean, controls main loop)
- Data persistence requirements:
  - JSON format configuration file (system parameters, rider information, order history)

### 3.2 Rider Data Model
- Rider object attribute definition:
  - rider_id: rider number (integer, unique identifier)
  - x, y: current location coordinates (integers, range 0-800)
  - speed: movement speed (integer, units/frame)
  - state: current status (integer, 0-2 enum values)
  - orders: order list (array, supports multiple orders)
  - special_case: special status flag (boolean)
- Rider status enums:
  - 0: Idle state (ready to receive new orders)
  - 1: Pickup state (heading to restaurant)
  - 2: Delivery state (heading to customer)

### 3.3 Order Data Model
- Order data structure:
  - Format: [Restaurant x, Restaurant y, Customer x, Customer y]
  - Data type: integer array (4 elements)
  - Coordinate range: 0-800 (automatically converted to grid center points)
- Order lifecycle management:
  - Creation: user inputs coordinates
  - Allocation: to the closest rider
  - Execution: pickup → delivery process
  - Completion: status update and resource release

### 3.4 Map and Coordinate System
- Grid coordinate system specifications:
  - Map size: 800x800 pixels
  - Grid size: 100x100 pixels
  - Number of grids: 8x8=64 grid units
  - Coordinate range: 0-800 (integer coordinates)
- Coordinate conversion rules:
  - Input coordinate → grid center point conversion
  - Grid center point calculation: center_x = (grid_x // 100) * 100 + 50
  - Supports boundary handling and abnormal coordinate processing

## 4. Technical Implementation Requirements

### 4.1 Development Environment and Dependencies
- Programming language: Python 3.6+
- Dependency management: Use only Python standard library
- Development tools: Support command-line debugging and log output

### 4.2 Core Module Architecture
- SystemManager: Core system management (funds, riders, state management)
- Rider: Rider class (movement, state, order management)
- OrderManager: Order management (creation, allocation, completion handling)
- PathPlanner: Path planning (grid-based algorithm, special case handling)
- DisplayManager: Display management (status display, map visualization)
- InputManager: Input management (command parsing, validation handling)

### 4.3 Performance and Stability Requirements
- Concurrency: Support at least 10 riders running simultaneously
- Response time: System response time < 100ms
- Memory usage: Memory consumption < 100MB
- Stability: Support long-running operation (24hr+) without memory leaks
- Error recovery: Automatically recover system status in exceptional cases

### 4.4 Code Quality and Maintainability
- Code standards: Follow PEP 8 Python coding standards
- Documentation completeness: Provide detailed function and class documentation
- Unit testing: Core functional module test coverage > 80%
- Error handling: Comprehensive exception handling and logging mechanism

## 5. Testing Requirements

### 5.1 Functional Test Cases
- Rider management tests:
  - Rider creation and attribute initialization
  - Status transition logic validation
  - Movement algorithm accuracy test
- Order management tests:
  - Order creation and coordinate conversion
  - Allocation algorithm correctness verification
  - Order completion process test
- System integration tests:
  - Multi-rider concurrent delivery scenarios
  - System state consistency check
  - User interaction process verification

### 5.2 User Experience Testing
- Smoothness of command-line interaction test
- Clarity of error prompts verification
- Functional ease-of-use test

## 6. Deployment and Operation Requirements

### 6.1 Runtime Environment Configuration
- Operating System: Support for Windows/macOS/Linux
- Python version: 3.6+ (recommended 3.8+)

### 6.2 Deployment and Installation
- Dependency management: requirements.txt file (only standard library)
- Installation script: Provide a one-click install and configure script
- Configuration file: Support custom system parameters
- Documentation completeness: Installation guide, user manual, API document