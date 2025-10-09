# NetEase Cloud Music Data Collection and Analysis Platform PRD

## Demand Overview

This platform aims to build a NetEase Cloud Music data collection and intelligent analysis system based on distributed crawler technology. The system automates the collection of playlist data from the NetEase Cloud Music platform using the Scrapy crawler framework, and integrates data cleaning, storage, visualization analysis, and machine learning prediction technologies to provide data-driven decision support for the music industry.

The core value of the platform lies in: integrating data visualization analysis across five dimensions, including song popularity distribution, user preference analysis, etc.; built-in machine learning models to predict play counts, providing intelligent recommendations for content creators and platform operators.

The system is targeted towards music data analysts, content operators, academic research institutions, etc. By offering standardized data interfaces and visual reports, it reduces the technical barrier to music data analysis and improves the efficiency and accuracy of data insights. The system uses a command-line interface design suitable for local development environments, with all visualization results saved locally as image files.

## Functional Requirements

### 2.1 Distributed Data Collection Module

#### 2.1.1 Playlist Index Crawler Subsystem
- **URL Queue Management**: Supports dynamic generation of Chinese music playlist URLs (pagination parameter offset ranging from 0 to 1715, with a step of 35), ensuring an automated URL push mechanism.
- **Data Parsing Engine**: Uses BeautifulSoup parser to extract key information from the playlist index page:
  - Playlist details page URL (retrieved using CSS selector `.dec a` to obtain href attribute)
  - Playlist title (automatically converts commas to avoid conflicts with CSV format)
  - Play count data (supports automatic conversion for "万" unit to a numeric value)
  - Creator's username (precisely located through `p > a` selector)
- **Queue Transfer Mechanism**: Automatically pushes the parsed details page URLs to the detail_url_queue for streamlined crawling tasks.

#### 2.1.2 Playlist Detail Crawler Subsystem
- **Deep Information Extraction**: Obtains extensive metadata from playlist detail pages:
  - Playlist tag system (multi-tags connected with "-", default "none" if no tags)
  - Playlist introduction text (automatically cleans new line, handles special characters)
  - Favorites count statistics (removes brackets and other formatting characters)
  - Play count, number of songs, comment count (extracts accurately using various CSS selectors)
- **Exception Handling Mechanism**: Implements null value detection and default value filling (default "none") for all data fields to ensure data integrity.

### 2.2 Data Storage and Management Module

#### 2.2.1 Data Storage
- **Data Storage**: Stores in CSV files with two key files:
  - music_list.csv: stores basic information of playlists (URL, title, play count, creator)
  - music_detail.csv: stores detailed information of playlists (title, tags, description, favorites, play count, number of songs, comment count)

#### 2.2.3 CSV File Export Layer
- **Field Mapping**: Automatically handles Chinese character encoding (UTF-8-sig) to ensure correct display in tools like Excel.
- **File Management**: Uniformly saved in the music_data directory containing music_list.csv and music_detail.csv.

### 2.3 Data Visualization and Analysis Module

#### 2.3.1 Multidimensional Statistical Analysis
- **Song Popularity Analysis**:
  - Top 10 Bar Chart of Song Occurrences: group statistics based on the title field, output as horizontal bar chart
  - Supports Chinese font rendering (Microsoft YaHei), chart size 16x8 inches, DPI 80
  - Custom color schemes (RGB: 16,152,168), transparency 0.7, enhancing visual effects
- **User Contribution Analysis**:
  - Top 10 Playlist Contributions by Creators: ranks the number of playlists created by users
  - Top 10 Play Counts for Western Playlists: sorts Western-type playlists by play count
- **Data Distribution Analysis**:
  - Histogram of Favorites Distribution: displays distribution characteristics in the favorites count range
  - Histogram of Play Counts Distribution: analyzes distribution patterns of play counts

#### 2.3.2 Chart Generation and Export
- **Progress Bar Display**: 60-step progress bar, shows chart generation progress in real-time (using ▓ and - characters).
- **Image Saving**: All charts automatically saved to music_image directory in PNG format, supporting high-resolution output.
- **Command-Line Friendly**: Removes plt.show() interactive display function, only supports file saving, adapts to the local command-line environment.
- **Generation Confirmation**: Outputs confirmation of the save path in the console after each chart is generated.

### 2.4 Data Pre-processing and Cleaning Module

#### 2.4.1 Data Standardization
- **Value Conversion Engine**:
  - Play Count Standardization: converts the "万" unit strings to numeric values (e.g., "5万" to 50000)
  - Favorites Handling: replaces "favorites" text with 0, ensuring consistency in numerical fields
  - Comment Count Cleaning: removes formatted characters, converting to integer values
- **Data Quality Control**:
  - Missing Values Handling: dropna() automatically deletes records containing null values
  - Duplicate Cleaning: drop_duplicates() ensures data uniqueness
  - Data Type Validation: forced conversion to int type, ensuring accuracy in numerical calculations

#### 2.4.2 Data Cleaning Export
- **Standardized Output**: Generates cleaned_music_list.csv and cleaned_music_detail.csv
- **Field Mapping**: Adds standard column names (playlist_id, title, plays, creator, etc.) to raw data
- **Encoding Processing**: Supports UTF-8 encoding to ensure correct display of Chinese characters

### 2.5 Machine Learning Prediction Module

#### 2.5.1 Play Count Prediction Algorithm
- **Feature Engineering**: Uses favorites count (favorite) and comment count (comments) as input features
- **Model Architecture**: Trains a regression model using the scikit-learn framework (stored as play_count_prediction_model_detail.pkl)
- **Prediction Service**: Supports batch prediction, inputs favorites count and comment count, outputs predicted play counts
- **Result Handling**: Takes the absolute value of negative prediction results to ensure reasonableness in play counts

#### 2.5.2 Model Management and Deployment
- **Model Persistence**: Uses joblib for model serialization, supporting fast loading and deployment
- **Sample Data Testing**: Includes 20 groups of test data for validating model prediction effectiveness
- **Scalability Design**: Supports new feature addition and model retraining to adapt to business requirement changes

### 2.6 System Interaction and Control Module

#### 2.6.1 Command-Line Interface (CLI)
- **Menu System**: Offers 5 data visualization options (A-G) with user interactive selection
- **Function Navigation**:
  - A: Generate Top 10 Song Occurrence Chart
  - B: Generate Top 10 Playlist Contribution Creators Chart
  - C: Generate Top 10 Play Counts for Western Playlists Chart
  - D: Generate Top 10 Comment Counts for Western Playlists Chart
  - E: Generate Play Count Distribution Chart
- **Exit Mechanism**: Supports quit command for safe system exit

#### 2.6.2 Batch Execution Mode
- **Automated Execution**: main.py supports non-interactive mode, automatically executing all visualization tasks
- **Screen Clearing Function**: Uses os.system('cls') for screen cleaning, enhancing user experience
- **Exception Handling**: Contains complete error capture and logging mechanisms

## Technical Requirements

### 3.1 System Architecture Requirements

#### 3.1.1 Distributed Crawler Architecture
- **Core Framework**: Based on Scrapy 2.11.2
- **Fault Tolerance Mechanism**: Implements checkpoints resuming crawling, retry on fail, and exception recovery, ensuring data collection stability

### 3.2 Tech Stack and Dependency Management

#### 3.2.1 Python Environment Requirements
- **Python Version**: Python 3.8+, compatible with asynchronous programming and type annotation
- **Core Dependencies**:
  - Crawler Engine: Scrapy 2.11.2
  - Data Processing: pandas 2.2.3, numpy 2.1.3
  - Data Visualization: matplotlib (configured for non-GUI backend, supports file saving only)
  - Machine Learning: scikit-learn, joblib (model persistence)

#### 3.2.2 Third-Party Service Integration
- **HTTP Client**: requests 2.32.3 + pyppeteer 2.0.0 for dynamic page rendering support
- **Data Parsing**: beautifulsoup4 4.12.3 + lxml 5.3.0 + cssselect 1.2.0
- **Security Encryption**: cryptography 43.0.3, pyOpenSSL 24.2.1 for secure data transmission

### 3.3 Deployment Environment Requirements

#### 3.3.1 Local Environment Configuration
- **Operating System**: Windows 10+, macOS 10.15+ or Linux distribution, supports command-line operation
- **Hardware Requirements**:
  - CPU: Dual-core or above, supports basic crawler operation
  - Memory: 4GB or more, meeting data processing demand
  - Storage: 20GB or more available space for data storage
- **Network Environment**: Stable internet connection, supports HTTP/HTTPS protocol access

#### 3.3.2 Local Service Installation
- **Python Environment**: Use virtualenv or conda to create isolated environment, avoiding package conflicts
- **Matplotlib Backend**: Configure Agg backend (non-GUI), supports chart generation in local environments

### 3.4 Performance and Monitoring Requirements

#### 3.4.1 Performance Indicators
- **Crawling Efficiency**: Supports processing 20+ URL requests per second, with a daily collection volume of 50,000+ playlists in local environments
- **Data Processing**: pandas data processing supports records of hundreds of thousands, keeping processing time to within minutes
- **Visualization Response**: Chart generation time controlled within 30 seconds, with real-time progress bar display
- **Storage Performance**: MongoDB local writing performance meets data storage needs, smooth Redis queue operations

### 3.5 Security and Compliance Requirements

#### 3.5.1 Compliance Requirements
- **Crawler Etiquette**: Complies with robots.txt protocol, sets reasonable request intervals and concurrency limits
- **Data Usage**: Follows NetEase Cloud Music service terms, used only for academic research and non-commercial purposes
- **Privacy Protection**: Does not collect users' personal privacy information, complies with GDPR and other data protection regulations
- **Open Source License**: Code follows MIT open-source license, dependency package license compatibility check

### 3.6 Operations and Deployment Requirements

#### 3.6.1 Local Installation Process
- **Dependency Installation**: Uses requirements.txt for batch installation of Python packages and version locking
- **Configuration Management**: Database connection string, Redis configuration, etc., managed through configuration files
- **Startup Script**: Provides a simple startup method, supporting the operation of crawler, data processing, and visualization analysis

#### 3.6.2 Maintenance and Scalability
- **Code Structure**: Modular design supports independent maintenance of crawler, data processing, analysis prediction, etc.
- **Error Handling**: Comprehensive exception capture and error recovery mechanisms to avoid system crashes caused by single point failure
- **Expansion Interfaces**: Reserved for data source expansion, new analysis dimensions, model algorithm upgrades, and other extension points
- **Documentation Maintenance**: Complete README documentation, API specifications, and deployment guide to facilitate team collaboration and knowledge inheritance

### 3.7 Command-Line Interface Optimization Requirements

#### 3.7.1 User Experience Design
- **Progress Visualization**: Provides progress bar display for long-running tasks (data processing, chart generation)
- **Operation Confirmation**: Important operations (data cleaning, file overwrite) provide confirmation prompts to avoid misoperation
- **Result Feedback**: Provides clear success/failure feedback and result file path for each operation completion
- **Error Friendly**: Provides clear error information and resolutions in case of exceptions