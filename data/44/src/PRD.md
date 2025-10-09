# Beijing Subway Fare System PRD

## 1. Overview of Requirements
This project aims to develop a command-line-based Beijing Subway fare system, integrating graph theory algorithms with fare calculation functions. The system should support user input of starting and ending stations, calculate the optimal path using Dijkstra's shortest path algorithm, and automatically calculate fares according to Beijing Subway fare rules. It should also offer path visualization and multi-format export capabilities, providing passengers with a convenient service for querying subway travel expenses.

## 2. Basic Functional Requirements

### 2.1 Subway Network Modeling Module
- Support the import of data for all stations in the Beijing Subway network, including station names, numbers, and line information.
- Implement subway network modeling based on graph theory, constructing a weighted undirected graph data structure.
- Provide station distance data management, supporting maintenance of adjacent station connection relationships.
- Implement special processing for transfer stations, supporting path computation at intersections of multiple lines.

### 2.2 Path Calculation Module
- Integrate Beijing Subway network data (including station names, connections, distances, etc.)
- Implement Dijkstra's algorithm to calculate the shortest path between stations with the following weight factors:
  - Basic Weight: Actual distance between stations (unit: meters)
  - Optimization Factor: Time complexity optimization using priority queues
  - Path Traceback: Support generation of complete path sequences
- Provide various path query functions:
  - Shortest Distance Path: Minimizing total travel distance
  - Least Transfers Path: Minimizing the number of transfers
  - Optimal Comprehensive Path: Balancing distance and transfers with a comprehensive score
- Support setting maximum transfer limits and line preference settings

### 2.3 Fare Calculation Module
- Implement a fare calculation algorithm based on Beijing Subway fare rules, recognizing the following fare segments:
  - Basic Segment: 0-6 kilometers (3 yuan)
  - Incremental Segment: 6-12 kilometers (4 yuan), 12-22 kilometers (5 yuan), 22-32 kilometers (6 yuan)
  - Extended Segment: Over 32 kilometers (1 yuan added for every 20 kilometers)
- Provide accurate fare conversion based on the calculated distance:
  - Mapping conversion from distance to fare
  - Special handling of boundary situations (e.g., 6.1 kilometers calculated as 7 yuan)
  - Support for rounding up decimal distances

### 2.4 Path Display and Export Module
- Implement path visualization based on path information and generate the following content:
  - Complete path sequence (list of station names)
  - Total distance statistics (displayed in both meters and kilometers)
  - Transfer information prompt (transfer stations and lines)
  - Calculated fare result
- Support generating path reports in various formats:
  - Console text format (including path details and fare information)
  - Structured data format (JSON format for easy program calls)
- Implement path summary generation, automatically extracting key information:
  - Total travel distance (converted from meters to kilometers)
  - Total fare statistics
  - Transfer count statistics
  - Estimated travel time estimate

### 2.5 Command Line Interaction System
- Implement a simple command line interface, supporting standard input and output operations
- Provide real-time input validation, including:
  - Validation of station name norms (based on official Beijing Subway station names)
  - Input format validation (supporting "Starting Station; Ending Station" format)
  - Validation of station existence (ensuring the entered station exists in the system)
  - Logical validation (e.g., "Starting station cannot be the same as the ending station")
- Support multi-level error handling mechanisms:
  - Input format error prompt
  - Nonexistent station prompt
  - Path calculation exception handling
  - Fare calculation exception handling

### 2.6 Data Management Module
- Support comprehensive management of Beijing Subway network data, including:
  - Station data: station names, numbers, and lines
  - Connection data: adjacent station distances and bidirectional connection relationships
  - Line data: line names, station sequences, and transfer information
- Implement data integrity check functions:
  - Validation of station data coverage
  - Integrity check of connection relationships
  - Accuracy check of distance data
- Provide data update mechanisms:
  - Support for adding new lines
  - Station information modification functionality
  - Distance data update capability

## 3. Technical Implementation Requirements

### 3.1 Core Algorithm Implementation
- **Graph Data Structure**: Implement `Graph` class, supporting vertex and edge management
- **Priority Queue**: Implement `MinPQ` class, optimizing Dijkstra's algorithm based on heap data structure
- **Shortest Path Algorithm**: Implement `ShortestPath` class, using Dijkstra's algorithm for optimal path calculation
- **Fare Calculation**: Implement `Sum_money` function to calculate corresponding fare based on distance

### 3.2 Data Structure Design
- **Station Mapping**: Implement `station_to_number` dictionary for mapping station names to numbers
- **Network Graph**: Implement `graph` dictionary representing a weighted undirected graph with adjacency lists
- **Path Storage**: Array structure for storing calculated path sequences
- **Fare Rules**: Array or dictionary for storing mappings from distance segments to fare

### 3.3 Performance Optimization Requirements
- **Time Complexity**: Optimize Dijkstra's algorithm using priority queue to O((V+E)logV)
- **Space Complexity**: Control memory usage of graph data structure within 100MB
- **Response Time**: Single path query response time should not exceed 1 second
- **Concurrent Processing**: Support single-user multiple continuous query operations

## 4. Data Requirements

### 4.1 Subway Network Data
- **Station Data**: Cover all main lines of Beijing Subway with all stations
- **Connection Data**: Include actual distances and connection relationships between stations
- **Line Information**: Cover main lines like Line 1, Line 2, Line 4, Line 5, Line 6, Line 8, Line 10, Line 13, Line 14, Line 15, Changping Line, Yizhuang Line, Fangshan Line, Airport Line

### 4.2 Fare Rules Data
- **Basic Fare**: 3 yuan for 0-6 kilometers, 4 yuan for 6-12 kilometers, 5 yuan for 12-22 kilometers, 6 yuan for 22-32 kilometers
- **Extended Fare**: Over 32 kilometers, 1 yuan added for every 20 kilometers
- **Boundary Handling**: Support fare logic for rounding up distance

### 4.3 Data Quality Requirements
- **Accuracy**: Distance data between stations consistent with actual operational data
- **Completeness**: Cover all operational stations and connection relationships
- **Consistency**: Station names consistent with official naming
- **Maintainability**: Support data updates and expansions

## 5. Acceptance Criteria

### 5.1 Functional Acceptance
- All core functions run normally, including path calculation, fare calculation, and result display
- Fare calculation accuracy consistent with Beijing Subway official standards
- Correct path calculation, able to find the shortest path
- User-friendly interaction with clear error prompts

### 5.2 Performance Acceptance
- Response time meets requirements, single query not exceeding 1 second
- Reasonable memory usage within anticipated range
- Stable program operation, supporting long-term continuous use

### 5.3 Quality Acceptance
- Good code quality with complete comments and clear structure
- Sufficient test coverage, including unit testing and integration testing
- Complete and accurate documentation, with user instructions and API documentation
- Comprehensive error handling, capable of gracefully handling various exceptions