# Library Management System PRD (Product Requirements Document)

## 1. Overview of Requirements
The project aims to develop a command-line-based library management system that integrates book management, user management, and loan management features. The system should support both administrator and regular user roles, enabling CRUD operations on book information through database interactions, providing basic permission control, and offering capabilities for tracking loan status and data export. This will support full-process business management for libraries.

## 2. Basic Functional Requirements

### 2.1 User Management Module

- Support user registration, including input of student ID, name, password, and contact information.
- Support user login verification, distinguishing between regular user and administrator privilege levels.
- Provide user information management functions, allowing administrators to perform CRUD operations on users.
- Implement password encryption storage using the MD5 hashing algorithm to protect user privacy.
- Support user permission settings, allowing administrators to modify user privilege levels.

### 2.2 Book Information Management Module

- Integrate basic book data (including title, book ID, author, category, publisher, publication date, and stock quantity—8 parameters).
- Implement CRUD operations for book information, allowing administrators to add, delete, update, and query books.
- Provide book search functionality with multi-condition combination search support:
  - Fuzzy search by title (supports partial matching)
  - Exact search by author
  - Filter search by category
  - Exact search by book ID
  - Search by publisher
- Implement a book inventory management mechanism that automatically maintains the available quantity and reserved quantity.
- Support batch import and export of book information.

### 2.3 Loan Management Module

- Implement book borrowing functionality, including the following business rules:
  - User identity verification (must be logged in)
  - Book inventory check (available quantity > 0)
  - Duplicate borrowing check (a user cannot borrow the same book more than once)
  - Borrowing quantity limit check (limit on the number of books a user can borrow simultaneously)
- Provide book return functionality, automatically updating inventory status and loan records.
- Implement book reservation functionality, supporting a queue mechanism for reserved books that are out of stock.
- Automatically maintain loan status, including borrowed status, return time, and reservation queue.

### 2.4 Query and Statistics Module

- Implement personal loan query functionality, displaying the user's current and historical loan records.
- Provide book status query functionality to display detailed book information and loan status.
- Implement system statistics functionality, allowing administrators to view:
  - Total number of books and users
  - Current loan and reservation numbers
  - List of books with insufficient stock
  - Loan frequency statistics
- Support visualization of loan data, generating statistical charts (using matplotlib to create basic charts like bar graphs and pie charts).

### 2.5 System Management Module

- Role-based permission management:
  - Regular user permissions: borrow, return, reserve, query
  - Administrator permissions: user management, book management, system statistics, data export
- Implement data backup and recovery functionality, supporting periodic automatic backups.
- Provide system log recording functionality to log key operations and exceptions.
- Support data import and export functionality in formats including JSON and CSV.

### 2.6 Command Line Interaction System

- Implement a multi-level command menu system with support for shortcut operations.
- Provide real-time input validation, including:
  - Student ID format validation (length 1-20 characters)
  - Password strength verification (length 6-32 characters)
  - Check for book ID uniqueness
  - Date format validation
- Implement an operation confirmation mechanism for important actions requiring user confirmation.
- Provide help information functionality, supporting command prompts and operational guidance.

## 3. Data Requirements

### 3.1 Database Design

#### 3.1.1 User Table (user)

```sql
CREATE TABLE user (
    StudentId VARCHAR(20) PRIMARY KEY COMMENT 'Student ID',
    Name VARCHAR(20) NOT NULL COMMENT 'Name',
    Password VARCHAR(32) NOT NULL COMMENT 'Password (MD5 encryption)',
    IsAdmin INT DEFAULT 0 COMMENT 'Is Administrator (0: Regular user, 1: Administrator)',
    tel VARCHAR(30) COMMENT 'Contact',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time'
);
```

#### 3.1.2 Book Table (book)

```sql
CREATE TABLE book (
    BookName VARCHAR(30) NOT NULL COMMENT 'Book Name',
    BookId CHAR(30) PRIMARY KEY COMMENT 'Book ID',
    Auth VARCHAR(20) NOT NULL COMMENT 'Author',
    Category VARCHAR(10) COMMENT 'Category',
    Publisher VARCHAR(30) COMMENT 'Publisher',
    PublishTime DATE COMMENT 'Publication Time',
    NumStorage INT DEFAULT 0 COMMENT 'Stock Quantity',
    NumCanBorrow INT DEFAULT 0 COMMENT 'Available Quantity',
    NumBookinged INT DEFAULT 0 COMMENT 'Reservation Quantity',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time'
);
```

#### 3.1.3 User Loan Table (user_book)

```sql
CREATE TABLE user_book (
    StudentId CHAR(10) NOT NULL COMMENT 'Student ID',
    BookId CHAR(6) NOT NULL COMMENT 'Book ID',
    BorrowTime DATE NOT NULL COMMENT 'Borrow Time',
    ReturnTime DATE COMMENT 'Return Time',
    BorrowState BIT(1) DEFAULT b'0' COMMENT 'Borrow Status (0: Returned, 1: Borrowed)',
    BookingState INT DEFAULT 0 COMMENT 'Reservation Queue (0: Not Reserved, >0: Queue Number)',
    CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    UpdateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time',
    PRIMARY KEY (StudentId, BookId)
);
```

### 3.2 Data Validation Rules

#### 3.2.1 User Data Validation

- Student ID: Non-empty, unique, length 1-20 characters, supports alphanumeric combination
- Name: Non-empty, length 1-20 characters, supports Chinese and English
- Password: Non-empty, length 6-32 characters, recommended to include an alphanumeric combination
- Contact: Optional, length 1-30 characters, supports phone/email format
- Administrator flag: 0 or 1, default is 0

#### 3.2.2 Book Data Validation

- Book ID: Non-empty, unique, length 1-30 characters, recommended to use ISBN format
- Book Name: Non-empty, length 1-30 characters, supports Chinese and English
- Author: Non-empty, length 1-20 characters, supports Chinese and English
- Category: Optional, length 1-10 characters, recommended to use a standard classification system
- Publisher: Optional, length 1-30 characters
- Publication Date: Optional, valid date format (YYYY-MM-DD)
- Stock Quantity: Non-negative integer, default is 0
- Available Quantity: Non-negative integer, cannot exceed stock quantity
- Reservation Quantity: Non-negative integer, cannot exceed stock quantity

#### 3.2.3 Loan Data Validation

- Student ID: Must exist in the user table
- Book ID: Must exist in the book table
- Borrow Time: Non-empty, valid date format, default is current date
- Return Time: Optional, valid date format, must be later than the borrow time
- Borrow Status: 0 (Returned) or 1 (Borrowed), default is 1
- Reservation Status: Non-negative integer, 0 indicates non-reserved status

### 3.3 Business Constraints

#### 3.3.1 Loan Constraints

- Limit on the number of books a user can borrow simultaneously: Regular users up to 5 books, administrators up to 10 books
- Book loan period: Default 30 days, configurable
- Overdue handling mechanism: Automatically marked as overdue after exceeding the loan period
- Reservation priority management: Queue in order of reservation time

#### 3.3.2 Inventory Constraints

- Available quantity cannot exceed stock quantity: NumCanBorrow ≤ NumStorage
- Reservation quantity cannot exceed stock quantity: NumBookinged ≤ NumStorage
- Reservation queue mechanism when stock is insufficient: Supports reservation up to the stock quantity
- Automatic reservation queue processing when books are returned: Notify users according to the reservation order

#### 3.3.3 Data Integrity Constraints

- Foreign key constraints ensure data consistency: Student ID and Book ID in user_book table must exist in corresponding tables
- Transaction processing to ensure data integrity: Use database transactions for borrow, return, and reservation operations
- Concurrency control: Use database locking mechanisms to prevent concurrent conflicts

### 3.4 Data Backup and Recovery

- Regular data backup mechanism: Automatically back up the database daily
- Data recovery functionality: Support data recovery from backup files
- Data import/export functionality: Support data exchange in JSON and CSV formats
- Logging and auditing functionality: Record all key operations and exceptions

## 4. Technical Implementation Requirements

### 4.1 Development Environment

- **Programming Language**: Python 3.8+
- **Database**: MySQL 8.0+
- **Database Connection**: PyMySQL 1.0.2+
- **Data Visualization**: matplotlib 3.5+
- **Development Tools**: VS Code / PyCharm
- **Version Control**: Git

### 4.2 Project Structure

```
library_management_system/
├── main.py                 # Main program entry
├── config/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   └── settings.py         # System configuration
├── models/
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── book.py            # Book model
│   └── borrow.py          # Loan model
├── services/
│   ├── __init__.py
│   ├── user_service.py    # User service
│   ├── book_service.py    # Book service
│   ├── borrow_service.py  # Loan service
│   └── auth_service.py    # Authentication service
├── utils/
│   ├── __init__.py
│   ├── database.py        # Database tools
│   ├── validators.py      # Data validation tools
│   ├── encrypt.py         # Encryption tools
│   ├── logger.py          # Logging tools
│   └── chart_generator.py # Chart generation tools
├── cli/
│   ├── __init__.py
│   ├── main_menu.py       # Main menu
│   ├── admin_menu.py      # Administrator menu
│   ├── user_menu.py       # User menu
│   └── helpers.py         # Interface helper tools
├── data/
│   ├── init_data.sql      # Initialization data
│   ├── sample_data.json   # Sample data
│   ├── charts/            # Chart output directory
│   └── backup/            # Backup directory
├── tests/
│   ├── __init__.py
│   ├── test_user.py
│   ├── test_book.py
│   ├── test_borrow.py
│   └── test_integration.py
├── docs/
│   ├── api.md             # API Documentation
│   └── user_guide.md      # User Guide
├── requirements.txt       # Dependencies
├── README.md              # Project Description
└── .gitignore             # Git Ignore File
```

### 4.3 Core Function Implementation Points

#### 4.3.1 Database Connection Management

- Connection Pool Management: Use a connection pool to improve database access efficiency.
- Transaction Processing: Ensure the atomicity, consistency, isolation, and durability of data operations.
- Exception Handling: Complete exception capture and handling mechanism.
- Connection Closing: Ensure database connections are properly closed to avoid connection leaks.

#### 4.3.2 Business Logic Implementation

- Data Validation: Verification of input data format and business rules.
- Business Rule Checks: Loan restrictions, inventory checks, and other business constraints.
- Status Management: Management of book and loan statuses.
- Concurrency Control: Use of database locks and transactions to ensure data consistency.

#### 4.3.3 User Interface

- Command-line Menu System: Multi-level menus, supporting return to the previous menu.
- Input Validation: Real-time validation of user inputs.
- Error Prompt: Friendly error message prompts.
- Operation Confirmation: Important operations require user confirmation.

#### 4.3.4 Data Security

- Password Encryption Storage: Use MD5 hashing algorithm to encrypt passwords.
- SQL Injection Protection: Use parameterized queries to prevent SQL injection.
- Permission Verification: Verify user permissions before every operation.
- Data Backup: Regularly back up important data.

#### 4.3.5 Chart Generation

- Use matplotlib to generate basic statistical charts.
- Support for bar graphs, pie charts, line charts, and other common chart types.
- Save charts in PNG format to a specified directory.
- Chart data generated based on database query results.

### 4.4 Testing Requirements

- Unit Testing: Cover all core functional modules, with test coverage ≥80%.
- Integration Testing: Verify collaboration and business processes between modules.
- Functional Testing: Ensure all functions work as expected.
- Data Testing: Verify the correctness and integrity of data operations.

## 5. Deployment and Operation

### 5.1 Environment Preparation

1. Install Python 3.8+: Ensure the Python environment is correctly installed.
2. Install MySQL 8.0+: Configure the database server.
3. Create Database and User: Set database connection permissions.
4. Install Dependencies: Use pip to install project dependencies.

### 5.2 Initialization Steps

1. Import Database Structure: Execute init_data.sql to create table structures.
2. Import Initial Data: Import sample or real data.
3. Configure Database Connection: Modify connection parameters in config/database.py.
4. Create Output Directory: Create directories for charts and other outputs.
5. Run System Test: Ensure all functions work properly.

### 5.3 Running Method

```bash
# Install dependencies
pip install -r requirements.txt

# Configure database connection
# Edit config/database.py file

# Initialize the database
python -c "from utils.database import init_database; init_database()"

# Run the system
python main.py
```

### 5.4 Maintenance Requirements

- Regular Data Backup: Automatically back up the database daily.
- System Log Monitoring: Monitor the system's operational status and exceptions.
- Regular Cleanup of Output Files: Clear outdated chart files.
- Security Updates: Timely updates for security patches and dependencies.

## 6. Acceptance Criteria

### 6.1 Functional Acceptance

- All basic functions operate normally: user management, book management, loan management, etc.
- Accurate and error-free data operations: correct results for CRUD operations.
- Correct execution of business rules: loan restrictions, inventory management, etc.
- Graphics generation functions work normally: ability to generate and save basic statistical charts.
- Proper handling of exceptions: comprehensive handling of input errors, network exceptions, etc.

### 6.2 Performance Acceptance

- Reasonable system response time: query operations' response time < 2 seconds.
- Stable concurrent access: supports more than 10 users operating simultaneously.
- Good data query efficiency: complex query response time < 5 seconds.
- Reasonable memory usage: system memory usage < 500MB.

### 6.3 Security Acceptance

- Effective user permission control: different privileged users can only access respective functions.
- Ensured data security: password encryption, SQL injection protection, etc.
- Complete input validation: all user inputs undergo validation.
- No sensitive data leakage in error messages: error prompts do not contain internal system information.

### 6.4 Usability Acceptance

- User-friendly interface: clear menu, explicit prompts.
- Clear error prompts: error messages are easy to understand.
- Complete help information: provide detailed operating instructions.
- Good system stability: long-term operation with no anomalies.

## 7. Project Timeline

### 7.1 Development Phase

- **Phase 1 (1-2 weeks)**: Environment setup, database design, basic framework.
- **Phase 2 (2-3 weeks)**: Development of user management and book management modules.
- **Phase 3 (2-3 weeks)**: Development of loan management and query statistics modules.
- **Phase 4 (1-2 weeks)**: Chart generation, system management, interface optimization, testing and debugging.

### 7.2 Testing Phase

- **Unit Testing (1 week)**: Function testing of each module.
- **Integration Testing (1 week)**: Overall system function testing.
- **Function Testing (3 days)**: Chart generation function testing.
- **User Acceptance Testing (3 days)**: Final acceptance and deployment.

### 7.3 Deliverables

- Complete source code and documentation.
- Database structure and initial data.
- User manual.
- System deployment guide.
- Test report and acceptance documentation.
- Sample chart files.
