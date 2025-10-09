# Knowledge Graph Completion System PRD Document

## 1. Overview of Requirements

This project aims to implement a knowledge graph completion system based on the TransE algorithm, meeting the following core requirements:
1. **Pure Python Implementation**: The entire process of data processing, model training, and evaluation is implemented solely with Python code.
2. **Local Execution**: All functions are executed locally via the command line, supporting mainstream operating systems.
3. **Complete Functional Loop**: Includes five core modules: data loading, vector training, link prediction, performance evaluation, and output of results.
4. **Verifiability**: Each functional module produces clear outputs or intermediate files, supporting step-by-step validation.

## 2. Basic Functional Requirements

### 1. Data Loading and Preprocessing

**Function Description**:
- Load the four core files of the FB15K-237 dataset.
- Build bidirectional mapping dictionaries for entities and relations.
- Validate data integrity and consistency.

**Implementation Methods**:
- Implement file parsers to handle different input file formats.
- Construct entity and relation ID mapping tables.
- Implement exception detection mechanisms to handle missing IDs and illegal triples.

### 2. TransE Model Training

**Function Description**:
- Vector space initialization and normalization.
- Configuration of training process parameters.
- Negative sample generation and loss calculation.
- Training process monitoring.

**Implementation Methods**:
- Initialize entity/relation vectors using uniform distribution.
- Implement batch sampling and negative sample generation strategies.
- Use margin-based loss function and SGD optimizer.
- Record loss values in real time and save the best parameter snapshots.

### 3. Link Prediction and Evaluation

**Function Description**:
- Support for three prediction modes.
- Distance calculation and candidate ranking.
- Evaluation metric calculation.

**Implementation Methods**:
- Implement L2 distance calculation function.
- Develop Top-N prediction results generation mechanism.
- Implement MeanRank and Hit@10 metric calculation logic.

### 4. Output of Results

**Function Description**:
- Model parameter persistence.
- Visualization of the training process.
- Generation of evaluation reports.

**Implementation Methods**:
- Implement vector file export function.
- Use matplotlib to draw loss curves.
- Generate evaluation reports in JSON format.

## 3. Data Requirements

### 1. Input Data Specifications

| File Type       | Format Requirements                       |
|-----------------|------------------------------------------|
| Entity mapping  | Each line: entity_name\tID               |
| Relation mapping| Each line: relation_name\tID              |
| Training/Test   | Each line: head_entity\ttail_entity\trelation |

**Quality Requirements**:
- Entity/relation IDs must be continuous without gaps.
- No overlapping triples between train/test sets.
- All entities/relations in triples must exist in the mapping files.

### 2. Output Data Specifications

| Output Type     | Format Description                        |
|-----------------|-------------------------------------------|
| Entity vector file  | Each line: ID + 50 float numbers      |
| Relation vector file| Each line: ID + 50 float numbers      |
| Loss curve      | PNG image file                            |
| Evaluation report| JSON format metric data                  |