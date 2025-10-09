# Higashino Keigo Novel Text Mining & Semantic Analysis Tool PRD

## 1. Requirement Overview
This tool is designed to provide literary researchers and text mining analysts with in-depth text analysis capabilities for Higashino Keigo's novels. It supports automatic extraction of key entities (characters, locations, time, professions) from novel texts, statistics on entity frequency distributions, construction of semantic vector models, as well as character relationship inference and similarity analysis. The tool operates via command-line interaction. Core features include entity recognition and extraction, frequency statistics analysis, semantic vectorization modeling, relationship inference analysis, and result presentation.

## 2. Core Functional Requirements

### 2.1 Entity Recognition and Extraction
- Provides a command-line interface for entering text file paths, supports specifying novel file path, and automatically detects file encoding (GBK/UTF-8).
- Utilizes professional Chinese word segmentation tools for text preprocessing, supporting mixed recognition of Chinese and Japanese names.
- Uses part-of-speech tagging to automatically identify four key entity types: character names (nr), geographical names (ns), temporal expressions (t), professional titles (nn).
- Displays dynamic progress prompts during extraction (e.g., "Processing novel 3: 45%"), supports interrupt operations (users can terminate processing by pressing Ctrl+C).
- Returns extraction status (success/failure), and if it fails, outputs the specific reason (e.g., file encoding error, tokenization failure, insufficient memory).
- Automatically saves the latest 10 entity extraction records; users can quickly reuse historical extraction results via their code/number.
- Outputs entity list containing entity name, type, occurrence frequency, and context information (8 characters before and after).

### 2.2 Frequency Statistics and Distribution Analysis
- Based on the extracted entity list, calculates the occurrence frequency of each entity type by novel, and generates a frequency ranking.
- Offers preset entity type filters: character filter, location filter, time filter, profession filter.
- Supports user-defined frequency interval filtering (enter minimum frequency threshold); filtered results must include entity name, novel, occurrence frequency, entity type tag.
- Allows combination of filtering conditions, and can add dimensions such as entity type, novel, etc. Conditions support "AND/OR" logic relations.
- Statistical results must support ascending/descending sorting (by frequency or user-specified fields), and pagination display (10 items per page, with previous/next page switching).

### 2.3 Semantic Vectorization and Similarity Analysis
- Allows users to select target entities for analysis from extracted entities (e.g., "Yukiho", "Kaga Kyoichiro"), targets must be character entities.
- Automatically trains word vector models using Word2Vec; model parameters: vector dimension 300, window size 5, minimum word frequency 20, number of worker threads 8.
- Calculates semantic similarity between target and other entities using cosine similarity, and outputs the top 10 ranked results.
- For the most similar entities (similarity > 0.7), performs in-depth analysis and outputs that entity's context characteristics and relationship network.

### 2.4 Relationship Inference and Pattern Discovery
- Supports user input of analogy inference queries, in the format "The relationship between A and B is similar to the relationship between C and who".
- Uses vector space analogy inference algorithm (D = C + B - A) to compute target entity D, searching for the best match within character entities.
- Automatically identifies relationship patterns, outputs relationship type labels (e.g., "Mentor-apprentice", "Couple", "Rival").
- Performs statistical analysis on identified relationship patterns, outputting pattern frequencies and distribution characteristics.

### 2.5 Command-Line Interaction and Result Presentation
- Main interface uses a menu-based interaction, including function options: [1] Enter novel file path [2] Entity recognition and extraction [3] Frequency statistics analysis [4] Semantic similarity analysis [5] Relationship inference analysis [6] View history [7] Exit.
- All user input undergoes validity checks (option must be digit 1-7, file path must exist, entity name must be in extraction results). Displays Chinese error prompts for invalid input.
- When generating analysis results, users can choose whether to display in textual table format.
- All output results support saving as TXT files (user can specify save path). Files must contain extracted entities, statistical results, similarity matrix, relationship inference results, and textual tables.

## 3. Data Requirements

### 3.1 Input Data
- **Novel Text Files**: Saved in txt/folder, containing Higashino Keigo's novels, format is .txt files, encoded GBK or UTF-8, data scale is 50+ novels totaling around 10 million characters.
- **External Dependencies**: Chinese word segmentation dictionary, Japanese name recognition model, part-of-speech tagging model.

### 3.2 Intermediate Data
- **Tokenization Results**: Text processed by professional tools, containing part-of-speech tagging information.
- **Entity Extraction Data**: Lists and frequency information for the four entity types: character, location, time, profession.
- **Manually Annotated Data**: Manually verified and revised entity lists, including entity type tags and importance ratings.

### 3.3 Output Data
- **Statistical Reports**: Frequency statistics tables for entities in each novel, high-frequency entity rankings, entity distribution analysis reports.
- **Semantic Models**: Trained word vector model files, word similarity matrices, semantic space mapping data.
- **Analysis Results**: Character similarity analysis reports, relationship inference case sets, pattern discovery summaries.

## 4. Performance Requirements

### 4.1 Processing Capability
- Supports processing more than 10 million characters of text data; processing time per novel does not exceed 5 minutes.
- Entity recognition accuracy: character names ≥ 90%, geo-names ≥ 85%, time expressions ≥ 80%, profession ≥ 75%.
- Semantic similarity calculation accuracy ≥ 85%, relationship inference results must be reasonably explainable.

### 4.2 Scalability
- Supports adding new entity types, processing works by other authors.
- Supports integration of new algorithm models (such as FastText, BERT, etc.).
- Supports customization of analytical dimensions and filter conditions.