# Genealogy Data Management and Relationship Analysis System PRD

## 1. Requirement Overview

This system aims to realize the full lifecycle management of family member information and intelligent analysis of complex kinship relationships through command-line interaction. The system constructs a family relationship network based on a tree data structure, supporting basic member information CRUD, multidimensional kinship queries, family statistical analysis, and data persistent storage. Core business scenarios include family member archive management, tracing blood kinship, family demographic statistical analysis, etc., providing a digital support tool for family history research, genealogy compilation, population statistics, and related fields.

## 2. Functional Requirements

### 2.1 Member Basic Information Management Module

#### 2.1.1 Member Information Entry Function
- **Data Field Standards**: The system supports the input of the following standardized fields:
  - Basic Identity Information: Name (string), Gender (enum: Male/Female)
  - Lifecycle Information: Date of Birth (YYYYMMDD format), Date of Death (YYYYMMDD format, 0 if alive), Birthplace (string)
  - Physical Characteristics: Height (float, unit: cm)
  - Social Attributes: Education (enum: Elementary/Junior/High School/Bachelor/Master/PhD), Occupation (string), Highest Title (string)
  - Relationship Attributes: Relative’s Name (used to establish family relationships), Relationship Type (enum: 0-Spouse, 1-Child)

- **Data Validation Mechanisms**:
  - Date Format Validation: Birth/Death dates must conform to the YYYYMMDD format, checked with regex `^\d{8}$`
  - Value Range Validation: Height should be between 50-300cm; if out of range, prompt user to re-enter
  - Education Level Validation: The education field must match predefined enum values, converting using a mapping dictionary (Elementary=1, Junior=2...PhD=6)
  - Relationship Logic Validation: When specifying a relationship upon adding a member, check if the target relative exists in the system

#### 2.1.2 Member Information Storage Function
- **Storage Format**: Structured storage using CSV format, with field order: Name, Birthplace, Date of Birth, Date of Death, Height, Education, Occupation, Highest Title, Relative, Relationship, Gender
- **File Management**:
  - Default Data File: `data.csv`, auto-created on first run
  - Incremental Storage: New member info is appended to avoid overwriting existing data
  - Data Integrity: Uses pandas DataFrame for processing to ensure standardized and complete CSV format

### 2.2 Family Relationship Network Construction Module

#### 2.2.1 Tree Structure Construction Algorithm
- **Data Structure Design**:
  - `Member` Class Definition: Each family member corresponds to a Member object with attributes:
    - `idx`: member’s index in the data list
    - `kids`: list of child member indices (supports multiple children)
    - `spouse`: spouse member index (-1 if no spouse)
  - Root Node Selection: The first entered member is the default family tree root node, relationship type set to -1

- **Relationship Establishment Logic**:
  - Spousal Relationship: Bidirectionally establish spouse pointers, share kids list for joint children
  - Parent-Child Relationship: Add child index to parent Member's kids list
  - Relationship Lookup: Locate the target member’s position in the family list by searching name

#### 2.2.2 Relationship Query Algorithm Implementation
- **Ancestor Query Algorithm**:
  - Input Parameters: target member index, number of generations to query, gender filter
  - Query Logic: Recursively traverse the family list to find members whose kids list contains the target member
  - Generation Control: Control queried generations via recursion depth parameter (1st = parents, 2nd = grandparents)
  - Gender Filtering: Filter results by user-specified gender (0-unrestricted, 1-male, 2-female)

- **Descendant Query Algorithm**:
  - Query Logic: Start from the target member’s kids list and recursively traverse all descendants for the specified generations
  - Result Collection: Collect qualifying descendant member indices in a list, and support cross-generation queries
  - Gender Filter: Apply a second filter on result list by gender

- **Spouse Query Algorithm**:
  - Direct Query: Retrieve spouse info from the Member object's spouse attribute
  - Exception Handling: Return "No spouse found" prompt if spouse is -1

### 2.3 Basic Information Retrieval Module

#### 2.3.1 Multidimensional Query Function
- **Query Dimensions**: Supports member search by the following nine dimensions:
  1. Exact name matching
  2. Fuzzy birthplace matching
  3. Exact date of birth matching
  4. Education level matching
  5. Occupation keyword search
  6. Highest title matching
  7. Gender classification search

- **Query Algorithm**:
  - Traversal Mechanism: Use the `circle()` function for linear traversal of all members
  - Data Type Handling: Type convert and match numeric fields (DOB, DOD, Height)
  - Result Aggregation: Collect indices of all matching members, supports multiple results (e.g., same names)
  - Exception Handling: Return -1 code when no match is found

### 2.4 Statistical Analysis Module

#### 2.4.1 Basic Statistical Functions
- **Height Statistics**:
  - Average Height Calculation: Use pandas’ mean() function to calculate family average height to one decimal place
  - Data Handling: Automatically filter out invalid height data (e.g., 0 or outlier values)

- **Education Statistics**:
  - Average Education Level: Convert education text to numeric level (Elementary=1...PhD=6), compute mean, then map back to text

#### 2.5.2 Demographic Statistics Function
- **Gender Ratio Statistics**:
  - Statistical Logic: Traverse gender field and count males and females respectively
  - Ratio Simplification: Use greatest common divisor algorithm to simplify the male:female ratio (e.g., 6:4 to 3:2)
  - Output Format: Output simplified gender ratio as "Male:Female" 

### 2.6 Tree Visualization Module

#### 2.6.1 Genealogy Visualization Output
- **Display Format**: Text-based tree structure to show family relationships:
  - Hierarchy Indentation: Add 2 spaces for each descendant generation
  - Member Identifier: Display as "--Name"
  - Spousal Relationship: Directly show spouse name after member’s name (e.g., "--John Doe Jane Doe")
  - Line Breaks: Each member on its own line, with clear hierarchy

- **Traversal Algorithm**:
  - Depth-First Traversal: Start from root node and recursively traverse each member’s kids
  - Level Recording: Use `layer` parameter to record current recursion depth and control indentation
  - Display Control: Real-time output to console during traversal for immediate genealogy display

## 3. Technical Requirements

### 3.1 Development Environment & Dependencies
- **Python Version Requirement**: Python 3.7+ to ensure compatibility with pandas, tkinter, etc.
- **Core Dependency Libraries**:
  - `pandas >= 1.0.0`: For CSV file and DataFrame processing
  - `tkinter`: Python standard library, retains GUI support for compatibility with existing GUIs
  - `os`: File system and path management

### 3.2 Data Storage Architecture

- **Data Integrity Assurance**:
  - Atomic Operations: Use pandas’ to_csv() method to ensure atomic file writes
  - Exception Recovery: On file operation failure, original data is kept to prevent data loss
  - Unified Encoding: UTF-8 encoding for all file operations to support Chinese characters

### 3.3 Algorithm Complexity Requirements
- **Query Performance**:
  - Basic Information Query: O(n) linear time complexity, where n is total number of family members
  - Relationship Query: O(h×k) time complexity, where h is tree height, k is average number of children
  - Statistical Calculation: O(n) linear time, supports real-time stats for families with thousands of members

- **Space Complexity**:
  - Memory Usage: O(n) space complexity, each member uses a fixed-size Member object
  - Storage Efficiency: CSV file size about 200 bytes per member, supports large-scale family data

### 3.4 Error Handling & Exception Management
- **Input Validation**:
  - Rigorous format checking: date formats, value ranges, enum values, etc.

- **Exception Handling Mechanisms**:
  - Query Exceptions: User-friendly error messages if member doesn’t exist or query condition is invalid