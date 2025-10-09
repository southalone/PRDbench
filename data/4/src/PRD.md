### Satellite Store Business Planning and Forecasting System PRD

#### 1. Requirement Overview
This system is a business tool designed for chain restaurant enterprises, integrating order volume prediction, cost structure analysis, and profit measurement functions to provide data support for store operation strategies. The system uses a command-line interaction method, allowing users to input basic parameters, adjust business strategy variables, and ultimately output a scientific store evaluation report. Additionally, related README files and unit tests are provided.

#### 2. Basic Functional Requirements

##### 2.1 Data Input and Parameter Management
- Support for creating/loading/saving project files, retaining historical parameter configurations
- Input module includes: basic information (city/area/business district type), physical location (latitude and longitude coordinates), category structure (three-level category proportions), cost parameters (ingredients/packaging/labor/rent, etc.)
- Parameter input supports range validation and rationality prompts, with industry benchmark values provided for key parameters
- Support for batch data import (CSV format), automatically extracting key indicators. Provide CSV format template and a small set of sample data

##### 2.2 Order Volume Prediction Engine
- Basic model includes: exposure prediction (based on location factors) → in-store conversion rate (based on category matching degree) → order conversion rate (based on price sensitivity), forming a three-level conversion chain
- Support setting commercial subsidy/service subsidy parameters to simulate the impact of platform subsidies on customer unit price (according to price elasticity coefficient model)
- Implement time series decomposition algorithm (STL) to predict order volume fluctuation curves for weekdays/weekends/holidays
- Provide adjustable influence factors for three-level categories, supporting simulation of how category structure adjustment affects overall order volume

##### 2.3 Cost Structure Analysis
- Automatically distinguish between fixed costs (rent/equipment depreciation/key personnel) and variable costs (ingredients/packaging/commissions/promotions)
- Implement contribution margin analysis to calculate the unit contribution value of individual products/categories
- Support tiered cost parameters (e.g., ingredient discounts for bulk purchasing, free shipping subsidies for reaching certain amounts)
- Generate break-even analysis charts to show breakeven points at different order volumes
- Provide key decision recommendations, automatically generating 3-5 operational optimization directions based on data

##### 2.4 Result Output and Report Generation
- Core indicator display: average daily order volume, customer unit price, gross profit margin, net profit, payback period
- Generate dynamic break-even analysis, including sensitivity factor ranking (by degree of impact)
- Support exporting Markdown format feasibility analysis reports, including key data charts