# Logistics Center Site Selection System PRD

## 1. Requirement Overview
This project aims to develop an optimized logistics center site selection system based on mathematical modeling and machine learning, providing a scientific logistics distribution network planning solution for McDonald's stores in Anhui Province. The system integrates the centroid method and K-means clustering algorithm, combined with GIS analysis. Through multidimensional data modeling and visual presentation, it provides data-driven site selection recommendations for logistics distribution decision-making, achieving the dual goals of minimizing delivery costs and maximizing service efficiency.

## 2. Basic Functional Requirements

### 2.1 Data Management Module
- Support reading geographical location and weight data of McDonald's stores from Excel files, including four core fields: address, longitude, latitude, and weight
- Implement data quality validation mechanisms, including validity checks for longitude (range: 73-135) and latitude (range: 3-54), non-negativity verification of weight data, and data integrity check (no missing values)
- Provide data preprocessing functions: weight normalization (conversion to probability distribution), coordinate standardization (using StandardScaler), anomaly detection and processing
- Support compatibility with multiple data formats, ensuring seamless integration with existing Excel files

### 2.2 Single Centroid Site Selection Module
- Implement the centroid method algorithm based on weighted averages, calculation formulas:
  - Centroid Longitude = Σ(longitude_i × weight_i) / Σ(weight_i)
  - Centroid Latitude = Σ(latitude_i × weight_i) / Σ(weight_i)
- Provide globally optimal site selection results, outputting the geographic coordinates of the optimal logistics center
- Implement visualization features: scatter plot rendering (stores as blue dots, centroid as red dot), axis labels (longitude, latitude), legend annotation
- Support Chinese font display, ensuring correct rendering of chart labels

### 2.3 K-means Clustering Analysis Module
- Implement automatic determination of optimal number of clusters:
  - Silhouette coefficient analysis: calculate silhouette coefficients for different K values (2-92)
  - Optimal K value selection: choose K with the highest silhouette coefficient as the final number of clusters
  - Visual analysis: plot the relationship between K values and silhouette coefficients to assist in decision-making
- Provide K-means clustering algorithm implementation:
  - Use scikit-learn’s KMeans algorithm for clustering
  - Standardize longitude and latitude coordinates to ensure clustering effectiveness
  - Calculate the center coordinates for each cluster
  - Allocate each store to its nearest cluster center
- Output clustering results: cluster center coordinates, cluster member assignments, results exported as Excel files

### 2.4 Partition Centroid Calculation Module
- Independently calculate the centroid for each cluster area, applying the single centroid algorithm within each cluster
- Provide comparative analysis between global centroid and partition centroids, showing differences in site selection strategies
- Support comparison across multiple scenario site selection plans to support decision-making

### 2.5 Result Visualization Module
- Implement clustering result visualization:
  - Scatter plot: use different colors to show store distribution within each cluster
  - Cluster centers: display each cluster center with red X marker
  - Color bar: displays cluster numbers to facilitate distinction
  - Chinese font support: ensure all labels display correctly
- Provide analysis chart generation functions:
  - Silhouette coefficient graph: curve of K value versus silhouette coefficient
  - Centroid comparison chart: comparison of positions between global and partition centroids
  - Support chart export in high-quality image formats

### 2.6 Data Export Module
- Support Excel file export:
  - Clustering results: each cluster in a separate worksheet, containing all store coordinates in that cluster
  - Centroid coordinates: export longitude and latitude information of all centroids
  - Analysis report: includes algorithm parameters, result summary, performance metrics
- Provide console output functions: global centroid coordinates, optimal K value, coordinates of each cluster center, silhouette coefficient analysis results

## 3. Data Requirements

### 3.1 Input Data Format
- **Store Data File** (total_data.xlsx): contains four fields—address (string), longitude (float, range 73-135), latitude (float, range 3-54), weight (positive integer)
- **Data Quality Requirements**: completeness (no empty fields), accuracy (coordinates must be correct), reasonableness (weight reflects actual delivery demand), consistency (coordinate system unified to WGS84)

### 3.2 Output Data Format
- **Clustering Result File** (cluster_points.xlsx): each cluster in a worksheet (Cluster 1, Cluster 2, ...), columns for longitude and latitude
- **Analysis Result Output**: console output of global centroid coordinates, optimal cluster number K, each cluster center coordinates, silhouette coefficient analysis results

### 3.3 Data Scale and Performance Requirements
- **Data Scale**: 92 McDonald's stores, entire geographic region of Anhui Province, 4-dimensional data (address, longitude, latitude, weight), clustering range 2-92
- **Performance Requirements**: single clustering analysis time <30 seconds, memory usage <500MB, coordinate precision to 6 decimal places, support batch data processing

## 4. System Architecture

### 4.1 Module Division
```
Logistics Center Site Selection System
├── Data Management Module
│   ├── Data Reading
│   ├── Data Preprocessing
│   └── Data Validation
├── Algorithm Calculation Module
│   ├── Single Centroid Method
│   ├── K-means Clustering
│   └── Silhouette Coefficient Analysis
├── Visualization Module
│   ├── Scatter Plot Rendering
│   ├── Cluster Result Display
│   └── Analysis Chart Generation
└── Result Output Module
    ├── Excel Export
    ├── Console Output
    └── Image Saving
```

### 4.2 Tech Stack and Dependencies
- **Programming Language**: Python 3.8+
- **Core Libraries**: pandas (data processing), numpy (numerical computation), scikit-learn (machine learning algorithms), matplotlib (data visualization), openpyxl (Excel file operations)
- **Configuration Requirements**: Chinese font file support, sufficient disk space, environment supporting matplotlib chart display