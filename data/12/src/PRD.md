### Retail Brand High-Value Store Operation Data Analysis Tool PRD

#### 1. Requirements Overview

The goal of this project is to develop a Python command-line tool to comprehensively analyze the operational data of high-value retail brand stores. This tool should extract and consolidate core store information from a variety of simulated data sources, perform data cleaning and deduplication, apply feature engineering transformations (including the RFM customer segmentation model), and execute time series decomposition. Ultimately, it should present the analysis results in a structured table format and support generating detailed access links for the data. The entire process must encompass data extraction, cleaning, analysis, and presentation phases, addressing the operational needs for effectively managing high-value stores (defined as `a_value_type='High Value'`).

#### 2. Basic Functional Requirements

##### 2.1 Multi-Source Data Extraction and Integration

- Support configuration of simulated data sources, including the store dimension table (store primary key `store_key`, store ID `store_id`, brand information `brand_name`, organizational structure `org_path`, private domain type `private_domain_type`), sales details table (transaction date `trans_date`, store primary key `store_key`, transaction amount `amount`, business group `biz_id`), and warehouse information table (business group `biz_id`, warehouse code `git_repo`).

- Implement multi-table join logic, connecting the store dimension table and the sales details table via `store_key`, and linking the sales details table with the warehouse information table through `biz_id`.

- Support conditional filtering extraction: retain only store data where `a_value_type='High Value'`, and the private domain type `private_domain_type` should be either 'Headquarters Direct' or 'Regional Focus'.

##### 2.2 Data Cleaning and Deduplication

- Handle missing values: Fill in the default value 'Unknown Brand' for records with an empty `brand_name` in the store dimension table, and remove records with NULL `amount` in the sales details table.

- Outlier filtering: Identify and remove abnormal transaction data from the sales details table where `amount` is ≤0 or `trans_date` is earlier than the store opening date (simulated field `opening_date`).

- Deduplication of duplicate data: Remove duplicates based on the composite key (`biz_id` + `trans_date` + `store_id`), retaining the latest transaction record (determined as the first entry in descending order by `trans_date`).

##### 2.3 Feature Engineering and Metrics Calculation

- RFM metrics calculation: Using sales details table data, calculate the store's recency (Recency, unit: days), transaction frequency (Frequency, unit: average monthly transactions), and monetary value (Monetary, unit: average monthly transaction amount).

- Time series decomposition: Apply STL (Seasonal and Trend decomposition using Loess) decomposition to the store's average monthly transaction amount, extracting trend, seasonal, and residual components as supplementary features for high-value attributes.

- High-value attribute label generation: Combine RFM metrics and STL trend components to generate label fields `value_tag` (e.g., "Growth High Value," "Stable High Value," "Potential High Value").

##### 2.4 RFM Customer Segmentation Analysis

- Implement the RFM customer segmentation model: Divide Recency, Frequency, and Monetary into high/mid/low levels using industry thresholds (configurable), generating 8 types of store segments (e.g., "Important Value Clients," "Important Retaining Clients," "Important Development Clients").

- Segmentation result statistics: Calculate the store count proportion and transaction amount contribution proportion for each segment type, supporting data filtering by segmentation type.

##### 2.5 Command-Line Result Display and Interaction

- Tabular data display: Display data rows expanded by business group (`biz_id`) and transaction date (`trans_date`), with column information including store ID, brand, organizational structure, private domain type, RFM segmentation type, average monthly transaction amount, and `value_tag`.

- Data detail link generation: Add a "Data Detail Link" column at the table's end, formatted as "repo://{git_repo}/detail?store_id={store_id}&date={trans_date}", enabling users to copy links for accessing pages with simulated data details.

- Interactive query: Allow users to input segmentation type (e.g., "Important Value Clients") or date ranges, with the tool filtering and presenting store data tables that meet the criteria in real time.