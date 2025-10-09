### Intelligent Analysis and Optimization System for Restaurant Supply Chains PRD

#### 1. Requirement Overview
This system aims to provide restaurant enterprises with a full lifecycle management solution for dishes. By integrating basic dish data, ingredient composition, sales performance, and supply chain information, it enables dish cost analysis and supply chain optimization. The system must support command-line interaction, fully implemented in Python, covering business logic for data management, ingredient analysis, sales statistics, and intelligent recommendation modules.

#### 2. Basic Functional Requirements

##### 2.1 Dish Data Management Module
- Supports CRUD operations for basic dish information (name, category, price, cooking time)
- Provides standardized dish data template import (CSV format) and bulk upload functionality
- Supports multi-criteria search based on dish ID, name, and category

##### 2.2 Ingredient Composition Analysis Module
- Supports uploading ingredient lists for dishes, including ingredient name, quantity, unit, and unit cost
- Provides dish cost structure analysis, calculating ingredient cost ratios and gross profit margins
- Supports allergen identification functions, allowing dishes containing the eight major allergens (such as shellfish, nuts) to be marked

##### 2.3 Sales Data Analysis Module
- Supports importing order data, including dish ID, sales quantity, sale time, and final price
- Implements dish sales trend analysis, with volume changes tracked by day/week/month

##### 2.4 Dish Similarity Matching Module
- Implements dish similarity algorithms based on name
- Supports uploading files of similar items, automatically identifying and categorizing similar dish groups
- Provides statistics on cumulative order volume, average final price, and sales volatility for similar dish groups

##### 2.5 Command-Line Interaction Features
- Implements a main menu navigation system, supporting seamless switching between modules
- Provides visual progress indicators (text progress bars) for data import/export
- Supports displaying analysis results as text tables or simple ASCII charts
- Implements confirmation mechanisms for critical operations and error handling processes