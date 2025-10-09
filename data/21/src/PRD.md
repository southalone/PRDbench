# Chengqingdao Area 1 Lottery System PRD

## 1. Requirements Overview

The Chengqingdao Area 1 Lottery System is a command-line lottery tool designed for internal regional activities, supporting multi-prize draws based on an employee roster. The system must implement roster import and management, custom lottery rule configuration, weighted random sampling for draws, result visualization, and fairness verification features, ensuring the draw process is transparent and traceable, and the results meet statistical randomness requirements.

## 2. Basic Functional Requirements

### 2.1 Roster Management Module

- Supports importing employee rosters in CSV/text format. The file must include fields for Name, Employee ID, Participation Points (integer), and Length of Service (months). If any field is missing or formatting errors are detected, display a Chinese error prompt and terminate import.
- After import, display roster statistics: total number of employees, percentage of each department (department code is parsed from the first 2 digits of employee ID), distribution of participation points (maximum/minimum/average value).
- Provides roster preview functionality, displaying the top 10 records sorted by length of service (ascending/descending). Supports precise employee information lookup by Employee ID.

### 2.2 Draw Rule Configuration Module

- Supports adding multiple prize categories (up to 5); each prize must be configured with: Prize Name (unique), Number of Prizes (positive integer), Weight Calculation Rule (single-selection: equal weight/points weighted/length of service weighted), Whether Repeat Winners are Allowed (boolean).
- Weight Calculation Rule Explanation: With equal weight, all employees have an equal chance of being drawn. With points weighted, probability is positively correlated with participation points. With length of service weighted, probability is positively correlated with length of service (weight formula: individual weight = individual indicator value / total indicator value).
- After configuration, display a summary of the rules, listing prizes, total number of prizes, and whether there is a risk of repeat winners (prompt if allowed). Upon user confirmation, proceed to the draw process.

### 2.3 Draw Execution Module

- Draw prizes sequentially according to prize order (user can adjust order), using the A-Res algorithm (Algorithm A-Res) for weighted random sampling; each draw result is calculated in real time.
- If repeat winners are not allowed, already drawn employees are excluded from the candidate pool for subsequent prizes; if the pool is insufficient for the required prize count, terminate the draw for that prize and issue a prompt.
- During the draw, display dynamic progress (e.g., "Drawing First Prize (1/3)..."). If a single draw takes more than 3 seconds, show a "Drawing, please wait..." message.

### 2.4 Result Display & Verification Module

- Winning results are displayed grouped by prize. Use different command-line text colors for different prizes (First Prize: red, Second Prize: blue, Third Prize: green, others: default color). Each group includes: sequence number, name, employee ID, department.
- Automatically generate a lottery fairness report, including: difference between the average participation points of winners per prize vs. overall average (Z-test, show p-value); goodness of fit between department winner ratio vs. department representation (Chi-square test, show χ² and p-values). Mark "Statistical results meet randomness requirements" for p > 0.05.
- Support saving winning results and fairness report to a TXT file, with file name format "Lottery_Result_YYYYMMDD_HHMMSS.txt".