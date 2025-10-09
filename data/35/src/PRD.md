## Enterprise Fixed Asset Management System PRD (Product Requirements Document)

---

### 1. Requirement Overview

This project aims to design and develop an enterprise fixed asset management system to achieve digitalized management of the full lifecycle of internal fixed assets. It will comprehensively improve the efficiency, accuracy, and traceability of asset management, effectively addressing issues in traditional asset management such as information silos, non-standard processes, and inaccurate data.

---

### 2. Functional Requirements

#### 2.1 User and Permission Management

- **User Authentication and Login Management**
  - Input of unique user identifier (username), password, role type, affiliated department, and account status (active/locked);
  - User login, logout, and authentication;
  - Passwords stored in encrypted form, default password "123456", Token valid for 1 day;
- **User Information Management**
  - CRUD operations for users, support for role assignment (SYSTEM/IT/ASSET/STAFF);
  - Users must be associated with a department; cannot delete the admin user or the currently logged-in user;
  - Password change function, with verification of original password and encrypted storage of new password;
- **Hierarchical Permission Control**
  - System Administrator (SYSTEM): Possesses the highest system permissions and can manage all users and departments;
  - IT Administrator (IT): Responsible for system technical maintenance and user management;
  - Asset Administrator (ASSET): Responsible for asset management, allocation, and review;
  - Regular Employee (STAFF): Can apply to use assets and view asset information relevant to themselves.

#### 2.2 Department Organizational Structure Management

- **Multi-level Department Tree Structure**
  - Supports unlimited levels of department hierarchy, with each department having a parent department;
  - Department name management and provision of root department query functionality;
  - Utilizes MPTT tree structure for efficient hierarchical querying and management;
- **Department Asset Administrator Configuration**
  - Each department can assign users with ASSET privileges as asset administrators;
  - Supports searching for asset administrators in parent departments, realizing permission inheritance;
  - If there is no asset administrator in the current department, automatically search in the parent department.

#### 2.3 Asset Classification and Attribute Management

- **Asset Classification Tree Management**
  - Supports asset classification tree with unlimited levels and unique classification name validation;
  - CRUD operations for classifications, checking for associated assets before deletion;
  - Provides classification tree query interfaces, supporting hierarchical display and management;
- **Custom Attribute Extension**
  - Supports adding custom attributes to all assets, with unique attribute name validation;
  - Bulk update functionality for attribute values, enabling flexible business expansion;
  - Management of associations between custom attributes and asset classifications.

#### 2.4 Asset Full Lifecycle Management

- **Asset Basic Information Management**
  - Asset name (required), asset description, asset value (required), service life (default 5 years);
  - Asset classification (required), asset status (IDLE/IN_USE/IN_MAINTAIN/RETIRED/DELETED);
  - Account holder (user), entry time, custom attributes;
- **Asset Tree Structure Management**
  - Supports management of parent-child relationships among assets, allowing assets to form a tree structure;
  - Child assets inherit status and account holder from the parent asset, supports batch operations for the whole asset tree;
  - Prevents circular references to ensure data integrity;
- **Asset Value Calculation and Depreciation**
  - Automatically calculates current asset value: current value = original value × (remaining service life / total service life);
  - Calculates depreciation annually, retired assets have a value of 0, supports real-time calculation;
- **Asset Operation Processes**
  - Asset CRUD, asset query (supports multi-criteria combined queries), asset allocation, asset retirement;
  - Available asset queries, asset history record queries;
  - Query results filtered by department permissions to ensure data security.

#### 2.5 Application & Processing Workflow

- **Definition of Issue Types**
  - Usage Application (REQUIRE): Apply to use a certain type of asset;
  - Maintenance Issue (MAINTAIN): Apply for asset maintenance;
  - Transfer Issue (TRANSFER): Apply to transfer an asset to another user;
  - Return Issue (RETURN): Apply to return an asset to inventory;
- **Issue Workflow Management**
  - Initiation: User submits an issue application, system checks for conflicts;
  - Processing: Asset administrator reviews and processes, supports batch processing;
  - Completion: Issue status updated to success or failure, records processing result;
- **Issue Conflict Handling**
  - Prevents a user from initiating multiple pending issues for the same asset;
  - Provides conflict prompts to ensure the process is standardized;
- **Issue Query and Management**
  - Query pending issues, and issues submitted;
  - Issue deletion function, supports full lifecycle management of issues.

#### 2.6 History Recording and Operation Tracking

- **Asset Change History Record**
  - Records all change operations of an asset: change time, user, type, and details;
  - Supports history queries, providing complete change traceability;
- **System Operation Log**
  - Records user login, logout, and major operations (create, delete, update);
  - Supports log queries and export, providing system audit capabilities;
  - Operation logs are associated with user permissions to ensure data security.

#### 2.7 Data Permissions and Security Control

- **Role-Based Access Control**
  - Data access permissions control: users can only access data of their own department;
  - Asset lists filtered by department, issue processing based on department permissions;
- **Data Integrity Assurance**
  - Model field validation, business logic validation, permission validation;
  - Data integrity checks to prevent inconsistencies;
  - Supports data backup and recovery to ensure data security.

---

### 3. Technical Requirements

- **Programming Language**: Python 3.7+
- **Authentication and Security**:
  - Hierarchical permission control, data access permission filtering
  - Operation log recording, system audit functionality
- **Tree Structure Management**:
  - Supports unlimited levels for departments and asset classifications
  - Prevents circular references to ensure data integrity
- **History and Traceability**:
  - Operation log recording, supports querying and export
  - Complete change traceability functionality

---

### 4. Data Model Design

#### 4.1 Core Data Tables

- **User Table (User)**: Basic user information, role, department association
- **Department Table (Department)**: Multi-level department tree structure
- **Asset Category Table (AssetCategory)**: Multi-level asset category tree structure
- **Asset Table (Asset)**: Asset basic information, status, value, category association
- **Custom Attribute Table**: Supports asset attribute extension
- **Issue Table (Issue)**: Issue application and processing records

#### 4.2 Data Initialization

- Create admin superuser, root department, and root asset category
- Create basic custom attributes, test data, and users

---