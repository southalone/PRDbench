# Simplified Distributed File System PRD

## 1. Overview of Requirements

This project aims to develop a distributed file system implemented using the Python standard library, featuring a three-tier architecture composed of client-proxy server-storage server. The system simulates a distributed environment using a local file system and inter-process communication, supporting concurrent multi-user access, enabling file permission management, basic caching mechanisms, and data redundancy, offering users a complete experience of distributed file storage services.

## 2. Basic Functional Requirements

### 2.1 User Connection and Session Management Module

Supports up to three client processes running simultaneously, with each client identified by a unique ID. Utilizes file locking mechanisms to achieve inter-process communication and state synchronization, providing user identity authentication based on configuration files. Session information is stored in a shared JSON file, supporting user login authentication and session state management. Upon disconnection, automatically cleans up related resources and temporary files.

### 2.2 Core File Operation Module

Supports complete file lifecycle management, including file creation, reading, writing, deletion, and other core operations. Allows users to specify file names and permission modes upon file creation, supporting four levels of permission settings. Implements basic file content editing functions, supporting complete reading and writing of text content. Provides file search functionality, capable of searching local cache and all storage server locations. Supports file listing functionality, displaying all files of a specified user and their distribution status.

### 2.3 Permission Management and Access Control Module

Implements four file permission modes: full permission allows complete access including deletion, writable permission allows read and write but not deletion, readonly permission supports file reading only, and private permission allows access only by file owner. Permission information is stored in JSON configuration files, with permission verification performed before each file operation. Returns corresponding error messages when permission is insufficient, ensuring safe file access.

### 2.4 Simplified Concurrency Control Module

Uses file locking mechanisms for inter-process synchronization, ensuring only one process is allowed to write to the same file at the same time. Manages operation queue through temporary files, ensuring orderly execution of operations. Sets a 30-second operation timeout to prevent processes from occupying resources for an extended period. Supports concurrent execution of read operations, allowing multiple processes to read a file simultaneously if permissions permit.

### 2.5 Basic Cache Management Module

Each client maintains its own local cache directory to store copies of recently accessed files. Implements a simple FIFO cache replacement strategy, with each client caching up to five files. Prioritizes checking local cache when reading files, returning local copies directly when cache hits occur. Automatically updates the corresponding local cache content upon file write operations. Provides manual cache clearing commands to support cache space management.

### 2.6 Data Redundancy and Fault Simulation Module

Automatically duplicates each file to two different storage server directories to ensure data redundancy. Simulates storage node health status monitoring by checking directory accessibility. Implements basic data recovery functions, automatically recovering data from other available copies when a specific replica is detected as unavailable. Performs regular data integrity checks to verify file existence and content integrity.

### 2.7 System Management Module

Utilizes a fixed configuration of two storage server directory structures, manages system parameters through JSON format configuration files, and provides system configuration viewing functions to display core parameters (storage server count, maximum client count, cache size limit, operation timeout). Implements a simple operation logging function, recording all file operations in a text log file. Provides system status query functionality to view current active clients, storage server status, and file distribution. Supports system initialization and cleanup functions, creating necessary directory structures during initialization and deleting user data while retaining configuration files during cleanup.

## 3. Data Requirements

### 3.1 File Storage Structure Design

Adopts a layered directory structure design, with client cache directories located at `clients/client{id}/cache/`, storage server directories at `servers/server{id}/{user_id}/`, system configuration files stored in the `config/` directory, operation logs recorded in the `logs/` directory, and temporary files and lock files stored in the `temp/` directory. File naming follows the `{owner_id}_{file_name}` format to ensure unique file identifiers.

### 3.2 Data Model Design

Permission information is stored in JSON format, with keys as file identifiers and values as permission level numbers. User information includes username, password, and active status. System configuration includes parameters such as storage server list, maximum client count, cache size limit, and operation timeout. File metadata records the file owner, creation time, size, and replica location information.

### 3.3 Inter-process Communication Protocol

Uses temporary files in JSON format for inter-process message transmission, with request and response files uniquely named using timestamps and client IDs. File locks are identified by resource names to prevent concurrent access conflicts. The communication protocol includes essential information such as operation type, user identity, target file, and operation parameters. The response format includes status code, message, and data content.

## 4. Performance and Reliability Requirements

### 4.1 Performance Indicators

The system supports up to three client processes to run concurrently, with a single file size limited to text files within 500KB. Local file operation response time is expected to be less than one second, aiming for a cache hit rate of over 60%. Each client's cache capacity is limited to five files, with a 30-second operation timeout. The total disk space usage of the system is controlled within 100MB.

### 4.2 Reliability Indicators

Maintains two replicas of each file to ensure no data loss in the event of single point failures. Data recovery time is required to be completed within 10 seconds, with fault detection response time under 5 seconds. The system supports automatic recovery from single storage server failures, ensuring data consistency through synchronous write mechanisms. Operation logs fully document all file operations, supporting issue tracking and system auditing.

## 5. Technical Implementation Requirements

### 5.1 Development Environment Configuration

Programming language used is Python version 3.7 or above, completely implemented using the Python standard library without requiring the installation of any third-party packages. Core standard libraries used include `os` for file system operations, `json` for data serialization, `time` for time management, `threading` for concurrent control, and `fcntl` or `msvcrt` for file lock implementation. Supports cross-platform operation, compatible with Windows, Linux, and macOS operating systems.

### 5.2 Deployment and Testing Requirements

The system uses a single-machine deployment method, with all components operating on the same machine. Disk space requires at least 100MB, and each process requires at least 10MB of memory. Testing coverage includes multi-client concurrent operation testing, file permission control testing, data redundancy and recovery testing, cache mechanism effectiveness testing, etc. Supports automated test scripts to verify system functionality integrity and stability.