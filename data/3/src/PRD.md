### Intelligent Set Meal Management System for Restaurant Vendors PRD

#### 1. Requirement Overview
This system is a command-line tool designed for restaurant vendors, aiming to manage the complete lifecycle of set meals. It accurately calculates the ingredient cost of set meals (including processing loss), combines nutrition balance standards and inventory optimization strategies to automatically generate single/double-person set meals that meet price constraints, and outputs cost breakdowns and profit evaluations. The system needs to support ingredient data maintenance, dynamic cost calculation, intelligent meal combination, and visualized result presentation, helping vendors balance cost control and product attractiveness.

#### 2. Basic Functional Requirements

##### 2.1 Ingredient and Cost Base Data Management

- Supports manual entry or CSV import of ingredient information. Fields include: Ingredient ID, name (e.g., "Wuchang Rice"), category (staple/protein/vegetable/seasoning), unit (kg/item/portion), purchase price (Yuan/unit), processing loss rate (%)—e.g., leafy vegetables 8%, meat 5%, referencing food science "ingredient processing loss rate" standards.
- Maintains a database of additional cost items, such as packaging box (preset unit price by set meal type: single-person meal 1.5 Yuan/box, double-person meal 2.8 Yuan/box), disposable cutlery (optional, 0.8 Yuan/set), and supports manually adding custom extra cost items (e.g., sauce pack 0.5 Yuan/portion).
- Provides ingredient data query function, supporting searching by name or category, displaying current unit price, loss rate, and inventory quantity (integer, in the same unit as the ingredient).

##### 2.2 Set Meal Cost Calculation Module

- Supports creation of new set meals by importing a product list (including product names, corresponding ingredients, and their quantities); ingredient quantities must support two decimal places (e.g., "Rice 0.15kg").
- Automatically matches ingredient unit price and loss rate to calculate actual cost for each item: Item Cost = Quantity × Purchase Price × (1 + Loss Rate/100), result rounded to two decimal places.
- Automatically summarizes total set meal cost: Total Cost = Σ(item ingredient costs) + Σ(selected extra cost items). The system will list all available extra cost items (e.g., packaging box, disposable cutlery), and allow users to choose which to include. Selected extras will automatically be counted in the total cost.
- Outputs a detailed cost report including: set meal name, list of ingredients (name/quantity/unit price/loss rate/item cost), extra cost items (name/amount), total cost.

##### 2.3 Intelligent Set Meal Generation Module

- Supports choosing set meal type (single-person/double-person), setting basic parameters: single-person meal price range 28-40 Yuan, double-person meal 40-60 Yuan; discount rate (e.g., 10% off, supports decimal input 0.1–1.0, default 1.0); inventory priority (high/medium/low—high priority selects ingredients with >50 units in stock first).
- Applies "Dietary Guidelines for Chinese Residents" 2022 core recommendations to construct nutrition constraints: single-person meals must include at least 1 staple (quantity ≥0.1kg), 1 protein ingredient (≥0.08kg), 1 vegetable (≥0.1kg); double-person meals: staple ≥0.2kg, protein ≥0.15kg, vegetable ≥0.2kg.
- Automatically combines set meals based on cost and nutrition constraints: traverses the ingredient database, filters ingredients by nutrition category, sorts them by inventory priority, and generates 3–5 sets of candidate meals (each set includes staple + protein + vegetable; each category can have multiple ingredients; may include 1 seasoning).
- Calculates recommended sale price for each candidate meal: Recommended Price = Total Cost × (1 + Target Profit Margin), default target profit margin is 30% (can be manually set to 20%–50%), final price rounded to integer (rounding), and must satisfy meal type price constraint (e.g., single-person meal calculates as 27.6 Yuan—automatically raised to 28 Yuan).
- Extra cost items are not considered when generating set meals.

##### 2.4 Set Meal Evaluation and Result Output

- Evaluates generated candidate meals by two dimensions: Profit Indicator (Profit Margin = (Sale Price × Discount – Total Cost)/Total Cost × 100%), Nutrition Score (based on dietary guidelines—≥3 types of ingredients gets 5 points, each additional type adds 1 point, max 8 points).
- Sorts candidate meals by descending profit margin, displays results: meal number, included product list (ingredient name + quantity, merge same type ingredients), total cost, suggested sale price, discount price, profit margin, nutrition score.
- Supports user selection of a meal to save; saved content includes: Meal ID, name (auto-generated as "[Type] Nutritious Meal X", X is serial number), product list, cost details, sale price, discount, creation time.
- Command-line output must use table format (Python tabulate library), with borders and headers, and aligned data.

##### 2.5 Interaction and Data Validation

- All user inputs must be validated for correctness (e.g., loss rate 0–30%, quantity >0, discount 0.1–1.0). If input is invalid, show Chinese prompt (e.g., "损耗率需为0-30之间的数字" / "Loss rate must be a number between 0-30") and allow re-entry.
- Supports quitting the current operation midway ("q" to return to previous menu), including a three-level menu: Main Menu (Data Management/Cost Calculation/Meal Generation/Exit) → Function Menu → Operation Menu.
- CSV import must validate format (field match, correct value types). If import fails, display specific error line number and reason.