# 1. Overview of Requirements

This project aims to develop a localized data processing and automated testing platform, targeted at data engineering or business analytics teams. The goal is to enable developers or analysts to perform a series of common data processing, transformation, and validation operations in the local environment using Python, and quickly verify the correctness of algorithms via automated test scripts. The platform does not require a frontend interface; all functions are operated via command-line interaction, facilitating integration into CI/CD or data pipeline scripts.

# 2. Functional Requirements

1. **Data Processing Module**

   - **Numeric Comparator**: Provides a general-purpose numeric comparison function that returns -1/0/1, suitable for sorting, threshold judgment, and other business scenarios.
   - **Conditional Filter**: Supports custom condition functions to filter input data lists, retaining items that meet the criteria. Applicable to data cleaning, log filtering, etc.
   - **Dynamic Adder Generator**: Dynamically generates addition functions based on input parameters, commonly used in parameterized configuration or batch data correction.
   - **Unique List Extractor**: Extracts the first occurrence of unique elements from the original data, maintaining the original order. Suitable for deduplication needs in logs, user IDs, etc.
   - **Recursive Replacer**: Recursively replaces specified elements within nested data structures. Applicable to configuration templates, text processing, complex data migration, and similar scenarios.
   - **Batch Mapper & Replacer**: Supports batch mapping and replacement of multiple groups of elements, ideal for bulk word lists, labels, ID mapping, and other business needs.

2. **Automated Testing and Feedback**

   - **Automated Unit Testing**: Each functional module is accompanied by independent unit tests covering normal, abnormal, and boundary scenarios. All test cases are managed uniformly under the `tests/` directory.
   - **Local Score Feedback and Reporting**: Provides a local scoring script to automatically tally the pass rates of each module, outputting detailed scores and totals for easy self-check and quality control among team members.

3. **Command-Line Interaction Experience**

   - **One-Click Execution and Testing**: Users can run all functions and tests with a single command-line instruction, without needing a graphical interface, making it suitable for automated integration.
   - **Parameterized Submission & Identity Marking**: Supports specifying user identity (such as employee ID, name) via command-line parameters, facilitating team collaboration and result archiving.

4. **User Guide and Documentation**

   - **Detailed Operation Documentation**: Provides a `README.md` containing environment setup, module description, testing methods, command-line usage, and FAQs.

