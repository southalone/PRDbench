## Bank Personal Credit Intelligent Assessment System PRD (Product Requirements Document)

### 1. Overview of Requirements

1. This system provides banks/financial institutions with an intelligent personal credit assessment tool based on AI algorithms, facilitating efficient, automated credit approval decision-making through command line or web interaction.

2. The core goal of the system is: automatic extraction and processing of customer data, using various algorithms (such as neural networks and Logistic regression) for credit evaluation and analysis, providing accurate scoring of customer credit, and displaying results through multi-dimensional data visualization and indicator systems to assist staff in quick and scientific loan approval.

3. Design approach:
   - Supports data management, feature engineering, and algorithm analysis based on the UCI standard credit data set (1000 records), achieving a full-cycle closed loop of data preprocessing, algorithm application, scoring, and visualization.
   - Capable of extending to real business data integration, enhancing the generalization capability and usability of algorithms.
   - Comprehensive utilization of ROC curves, LIFT charts, K-S curves, AUC, and other statistical indicators for multi-angle comparison and selection of algorithm performance.

---

### 2. Functional Requirements

#### 2.1 Data Management and Intelligent Processing Module

- **Data Import/Export**
  - Support batch import of raw customer credit data via CSV/Excel (UTF-8 encoding), with field structures compatible with UCI credit data set formats.
  - Support export of processed data and AI analysis results to CSV/Excel.
  - Implement field mapping and validity verification (missing values, abnormal data, type mismatch alerts) during data import.

- **Data Preprocessing**
  - Support missing value processing (choice of mean/median/mode filling, outlier removal, binning).
  - Achieve automatic recognition and encoding of numerical and categorical fields (such as one-hot encoding/label encoding).
  - Provide feature selection functions (e.g., Pearson correlation coefficient to filter redundant features) and statistical distribution information for each field.
  - Support random sampling of customer samples (setting proportion and random seed possible).
  - Support data standardization/normalization and binning (such as reserved interfaces for Woe encoding).

#### 2.2 Algorithm Analysis and Scoring

- **Algorithm Selection and Configuration**
  - Offer two mainstream credit evaluation algorithms: Logistic regression & neural networks (MLP) for credit analysis.
  - Support algorithm parameter configuration; users can customize adjustments through command line/configuration files.
  - Provide expandable interfaces, facilitating inclusion of additional algorithms such as decision trees.

- **Algorithm Application and Analysis**
  - Automate algorithm analysis execution, output analysis logs and key parameters.
  - Support multi-algorithm performance comparison, output performance indicators.
  - Support analysis result saving and loading.

- **Scoring and Prediction**
  - Implement batch scoring on test sets/new customer data, output score results, credit ratings (scoring rules configurable).
  - Results output with unique customer ID, score probability, algorithm category, etc.

#### 2.3 Model Evaluation and Visualization

- **Evaluation Indicators and Output**
  - Automatically generate and save:
    - ROC curve and AUC (curve PNG, AUC value)
    - K-S curve (showing maximum KS distance and position)
    - LIFT chart (showing lift across different tiers)
    - Accuracy, recall, F1 score, confusion matrix
  - Output main evaluation indicator comparison table (Logistic regression vs neural network).

- **Visual Reports**
  - Support one-click generation of evaluation reports (including various statistical charts, key parameters, business interpretations), export as HTML.
  - All charts need to adapt to data quantity and labels.
  - Support automatic generation of "Model Effect Summary": pointing out the model with the highest accuracy, application suggestions, model stability, etc.

- **Parameter/Feature Interpretation**
  - Logistic regression: Output coefficients of each feature and their positive/negative impacts, Top-N importance visualization.
  - Neural network: Output representative weights, feature contribution visualization (expandable to Permutation Importance, SHAP values).

#### 2.4 System Extension and Business Integration

- **Real Business Integration**
  - Support integration with actual bank data files (CSV, Excel format, require desensitization/permission control).
  - Adapt real business field mapping, additional feature analysis.
  - Provide AI prediction interface (RESTful style), input multiple customer fields information to return AI credit score and rating.

- **Permission and Security Management**
  - Support management/operator role configuration (view/AI analysis/import/predict hierarchical permission control).
  - Internal encryption of sensitive data transmission and minimized storage, log all key operations.

- **Log and Error Handling**
  - Global exception capture, automatically record important steps (such as data import, AI algorithm execution) in logs (including timestamps/parameters/error stacks).
  - Support log file rotation and review, critical errors automatic email alert (optional).

---

### 3. Technical Requirements

- **Programming Language**
  - Python 3.9+

- **Core Technology Stack**
  - Data Processing: Pandas, NumPy
  - Machine Learning: scikit-learn (Logistic regression), PyTorch/TensorFlow (Neural networks, optional one preferred PyTorch)
  - Visualization: Matplotlib, Seaborn (Statistical charts)
  - Indicator Evaluation: scikit-learn.metrics (AUC, ROC, KS curve LIFT, etc.)
  - Configuration Management: YAML (Parameter configuration)
  - Command Line Interface: Argparse
  - Logging System: logging
  - Data Import/Export: csv, openpyxl
  - Report Generation: Jinja2 (HTML)
  - Web/API Extension Port (if needed): FastAPI

- **Algorithm Usage Requirements**
  - Use existing machine learning libraries' Logistic regression and neural network algorithms.
  - No model training, directly use algorithms for data analysis and scoring.
  - Algorithm results are interpretable, support parameter analysis.
  - Support multi-algorithm performance comparison and result output.

- **Code and Performance Requirements**
  - Modular design, strict decoupling of functional layer/service layer/CLI layer, code compliant with PEP8 standards.
  - Critical data processing and algorithm execution support breakpoint continuation and interrupt recovery.
  - Unit testing (pytest), core process coverage rate ≥ 85%, interface parameters and exception flow need verification.
  - Under basic test data volume (1000 records) algorithm analysis + evaluation ≤ 30 seconds.

- **Security and Compliance**
  - Sensitive field processing (desensitized logs, export optional field hiding).
  - User authentication (if enabled Web/API) interface token authentication, minimal operation principle.
  - Retain historical record of key parameters and algorithm results for traceability and inspection.