### Command-Line Data Preprocessing and Analysis Tool PRD

#### 1. Overview of Requirements
This tool is designed to offer comprehensive data preprocessing and analysis capabilities in a command-line environment. It supports importing Excel data, multi-mode data transformations, statistical analysis, and rule-based splitting and exporting functions. Users can complete the entire process from raw data cleaning to formatted output through command interactions, meeting the fundamental needs of Exploratory Data Analysis (EDA) in the field of data science.

#### 2. Basic Functional Requirements

##### 2.1 Data Import and Metadata Parsing
- Support reading .xlsx/.xls files, automatically detecting the number and names of worksheets.
- Parse and display data metadata: field names, data types (numerical/categorical/date), and proportion of missing values.
- Provide data preview functionality, displaying the first N rows of data (N is configurable, default 10 rows).
- Support selecting specific worksheets or batch import of multiple worksheets.

##### 2.2 Data Formatting Operations
- **Row/Column Transformation Module**:
  - Support row-to-column conversion (specifying aggregation key and value columns).
  - Support column-to-row conversion (row-by-row mode), automatically recognizing common delimiters (comma/semicolon/space/Tab).
  - Allow the addition of intermediate joiners, prefix text, and suffix text during transformation.
  - Provide a "text quoting" option in row-by-row mode, supporting single quote/double quote/no quoting modes.

- **Data Formatting Module**:
  - Support enumerated value replacement (user must provide a key-value mapping table).
  - Provide numerical formatting (decimal places, percentage, scientific notation).
  - Support date type normalization (ISO 8601/custom format).
  - String processing (case conversion, trim extra spaces, filter special characters).

##### 2.3 Data Content Cleaning Functionality
- **Missing Value Handling**:
  - Provide missing value statistics (by field and record dimensions).
  - Support removing missing values or filling them (mean/median/mode/custom value).

- **Outlier Detection**:
  - Implement the IQR (Interquartile Range) algorithm to identify outliers in numeric fields.
  - Provide Z-score normalization (user must specify threshold).
  - Support marking or replacing outliers.

##### 2.4 Statistical Analysis Functionality
- **Descriptive Statistics**:
  - Numerical fields: calculate mean, median, standard deviation, range, quartiles.
  - Categorical fields: calculate frequency, frequency rate, mode, and number of unique values.

- **Data Distribution Analysis**:
  - Generate frequency distribution tables of numerical fields (supporting equal-width/equal-frequency binning).
  - Calculate correlation coefficients between fields (option for Pearson/Spearman methods).

##### 2.5 Data Splitting and Export
- Support splitting datasets based on the values of specified categorical fields.
- Check and use valid field values as new worksheet names, outputting independent Excel files.
- Option to apply configured formatting rules during export.
- Support batch export to CSV format (delimiter and encoding must be specified).

##### 2.6 Command-Line Interaction and State Management
- Implement an interactive command menu system, allowing direct switching between functions without returning to the main menu.
- Provide operation history viewing, supporting historical result saving, loading, and display.
- All user inputs must be validated, and errors should provide Chinese prompts.