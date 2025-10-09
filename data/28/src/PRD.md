PRD - Intelligent Diagnosis and Optimization Recommendation System for SME Financing
1. Requirement Overview
The system interacts via command line, automatically collects basic information, business status, and innovation capability indicators input by enterprises to conduct multidimensional diagnosis of their current financing situation.

Technical highlights include:

Structured data collection
Rule engine diagnosis
Local data analysis
Intelligent report generation
2. Functional Requirements
2.1 Data Collection and Diagnosis
Collect enterprise basic information, business status, and innovation capability indicators through command line interaction.
Diagnose the current financing situation of the enterprise using locally stored data and rule-based analysis.
2.2 Policy Information
Basic policy information display (based on a preset SME policy database).
Policy information is stored and updated as local files.
2.3 Suggestions Generation
Basic suggestions generation:
Outputs standardized suggestions for R&D investment, intellectual property, and management compliance, etc., based on rule engine.
Provides preset improvement suggestion templates for weak management areas.
Generates a simple suggestion list.
2.4 Report Generation
Automatically compiles a structured diagnostic report based on analysis module output, consisting of:
Company profile
Financing score
Basic analysis
Simple suggestions
Supports saving reports as local text files.
Report includes basic charts (e.g., asset-liability bar chart, score radar chart), generated and saved using matplotlib.
2.5 User Data Management
Supports basic user authentication, with user data stored locally.
Provides simple operation log recording functionality.
3. Technical Requirements
Data Processing and Statistical Analysis: Pandas, NumPy
Rule Engine: Custom rule judgment logic based on Python
Visualization: Matplotlib (chart plotting and saving to files)
Code Structure/Specifications:
Layered architecture (data collection layer / analysis layer / report output layer)
Basic logging functionality
Independent functional module design
Supports basic unit testing
Compatible with Windows/Linux/MacOS terminal environments
Performance requirement: single enterprise diagnosis process completes within a reasonable time
Basic exception handling and input validation
Supports basic command line debugging output
Fully supports UTF-8 Chinese environment
4. Summary
The system focuses on core enterprise data analysis and basic suggestion generation, with all features implemented using Python standard libraries and commonly used third-party libraries. No GPU, model training, or pre-trained models are required. The report is generated in text format with basic charts saved locally. All data and policy information are managed locally, ensuring feasibility and ease of deployment.