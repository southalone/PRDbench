### US Stock Quantitative Analysis & Multidimensional Indicator Diagnostic Tool PRD

#### 1. Overview of Requirements
This tool aims to provide US stock quantitative analysts with comprehensive data querying and deep analysis capabilities. It supports user-defined SQL queries on US stock market data, enables stock screening (by market capitalization category and other dimensions) based on query results, and diagnoses the causes of volatility for specified financial/trading indicators (such as return volatility, PE ratio deviation) across multiple dimensions. The tool operates via command-line interaction, with core functionalities including SQL query management, market capitalization tier-based screening, variance decomposition for dimensional contribution analysis, and result presentation.

#### 2. Basic Functional Requirements

##### 2.1 SQL Query Management
- Provides a command-line SQL entry interface, supports multi-line input and syntax checking (implementing keyword check and bracket match validation using Python’s `sqlparse` library).
- Offers documentation for supported SQL statements, including sample usage and expected result previews.
- Displays dynamic progress indicators while executing queries (e.g., "Executing query: 30%"), and allows operation interruption (users can terminate queries with Ctrl+C).
- Returns query status (success/failure); on failure, outputs specific reasons (such as error position in syntax, non-existent fields, or data source connection failure).
- Automatically saves the last 10 valid SQL query records, allowing users to quickly reuse historical queries by reference number.
- Data sources support user-specified local CSV files (configured via command-line file path), with query fields strictly matching the CSV headers.

##### 2.2 Stock Market Capitalization Tier-Based Screening
- Provides preset market cap category screening based on the "Market Cap" field in query results, referencing NYSE official definitions: Micro-cap (<$300M), Small-cap ($300M≤Market Cap<$2B), Mid-cap ($2B≤Market Cap<$10B), Large-cap ($10B+).
- Allows users to set custom market cap ranges (input upper/lower limit values); screening results must include stock ticker, company name, market cap, and category label.
- Supports combined screening criteria; users can add dimensions such as sector (e.g., "Technology"), exchange (e.g., "NASDAQ"), etc. (based on respective fields in the SQL query results), with "AND/OR" logical relationships between conditions.
- Screening results must support ascending/descending sorting (by market cap or user-specified fields) and paginated display (10 items per page, with navigation for next/previous pages).

##### 2.3 Multidimensional Indicator Volatility Diagnosis
- Enables users to select indicators to analyze from the query results (e.g., "Daily Return Volatility", "Price-Earnings Ratio PE"), restricted to numeric fields.
- Automatically extracts non-numeric fields from SQL results as candidate analysis dimensions (e.g., "Sector", "Market Cap Category", "Region"), and allows users to pick 1-3 dimensions for combined analysis by reference number.
- Uses Multivariate Variance Decomposition algorithm to calculate each dimension’s contribution to indicator volatility, outputting explained variance proportions (e.g., "Sector: 42%, Market Cap Category: 28%, Interaction Effects: 15%").
- Performs in-depth analysis on the top contributing dimension (contribution > 30%), presenting the mean and standard deviation of the indicator for each sub-category under that dimension (e.g., "In the Sector dimension, Technology sector volatility mean is 1.2% (σ=0.3%), Healthcare sector volatility mean is 0.8% (σ=0.2%)").

##### 2.4 Command-Line Interaction & Result Presentation
- Main interface uses a menu-driven interaction scheme with options: [1] Enter CSV File Path [2] SQL Query [3] Stock Screening [4] Indicator Volatility Analysis [5] View Query History [6] Exit.
- User inputs require validity checks (e.g., options must be numbers 1-6; SQL fields must exist in the data source; selected dimensions must be within candidate range), with error messages presented in Chinese (e.g., "错误：请输入1-6之间的数字" – "Error: Please enter a number between 1-6").
- When generating analysis results, users can choose to display them as a textual table.
- All output results can be saved as TXT files (user-specified save path); files must include the query SQL, screening conditions, analysis dimensions, contribution data, and textual table.