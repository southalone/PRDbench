### BUPT-Air Intelligent Air Conditioning Management System PRD

#### 1. Overview of Requirements
This system aims to provide centralized intelligent management capabilities for multi-room air conditioning environments, allowing users to log in to the corresponding room's air conditioner using ID card recognition. It implements unified scheduling of air conditioning equipment, intelligent temperature regulation, real-time cost calculation, and operation log management based on a master-slave architecture. The system implements core functions via a Web API interface and is designed as a monolithic application with a built-in database and web server, allowing for local deployment and operation without complex external dependencies.

#### 2. Basic Functional Requirements

##### 2.1 Host Scheduling Management
- Provides host start/stop control interface, supports cooling/heating mode switching, automatically resetting all slave units' temperature settings when switching modes (reset to 22℃ if slave unit temperature exceeds 25℃ in cooling mode, or reset to 28℃ if it is less than or equal to 25℃ in heating mode).
- Supports three scheduling algorithm configurations: Random Scheduling (process requests randomly), First-Come-First-Served (process requests in order of time), and Wind Speed Priority (prioritize high wind speed requests).
- Provides host status query functionality, returning information on current operating mode, processing capacity, scheduling algorithm, standby status, etc.
- Supports configuration of processing capacity parameters (maximum requests processed per second, default is 3), automatically discarding excess requests when processing capacity is exceeded.
- Implements request queue management, prioritizing on/off requests to prevent queue overflow causing system malfunction.

##### 2.2 Slave Unit Temperature Control
- Registers and recognizes slave units based on ID numbers, supporting queries for corresponding slave unit status information via ID numbers.
- Provides a temperature adjustment interface, supporting temperature increase/decrease operations.
- Supports wind speed level adjustment (levels 0-3), with level 0 indicating off status, and levels 1-3 corresponding to low, medium, and high-speed winds, respectively.
- Implements slave unit on/off control, automatically setting wind speed to 0 when off, and maintaining current target temperature setting when on.
- Supports slave unit information management, including adding, deleting, and querying slave unit status.
- Supports batch deletion of slave units, clearing all slave unit status data for system reset or testing convenience.

##### 2.3 Intelligent Scheduling Algorithm
- Implements a request collection mechanism, retrieving all pending requests from the database every second and sorting them based on the configured scheduling algorithm.
- Supports priority handling logic, with on/off requests (wind speed changing from 0 to non-0 or from non-0 to 0) prioritized over ordinary adjustment requests.
- Provides intelligent decision-making functionality, automatically adjusting wind speed based on the current and target temperature difference, and reducing the wind speed to 0 when the target temperature is reached.
- Implements mode adaptation mechanism, setting wind speed to 0 when the current temperature is lower than the target in cooling mode, and higher in heating mode.
- Supports request queue limitations to prevent system overload due to exceeding host processing capacity.

##### 2.4 Temperature Monitoring and Calculation
- Implements a temperature change calculation model based on thermodynamic principles, considering external temperature effects on indoor temperature.
- Provides temperature initialization function, supporting the setting of external temperature as the initial temperature value.
- Implements a smart adjustment mechanism, automatically sending adjustment requests when the temperature deviates from the target by more than 1℃ and surpasses one second since the last request.
- Supports temperature calculation switch control, enabling/disabling automatic adjustment functionality.
- Provides temperature monitoring destruction functionality, stopping the temperature calculation thread and releasing resources.

##### 2.5 Real-Time Cost Calculation
- Implements energy consumption calculation based on wind speed levels, with low-speed wind calculated at 0.8 standard power/min, medium-speed wind at 1.0 standard power/min, and high-speed wind at 1.3 standard power/min.
- Provides real-time cost calculation functionality, charging 5 units per standard power, updating energy consumption and cost data every second.
- Supports cost calculation switch control, allowing the cost calculation thread to start/stop.
- Implements cumulative statistics functionality, recording the total energy consumption and total cost for each slave unit.
- Manages data persistence via ORM (Object-Relational Mapping) to ensure data consistency during cost calculations.

##### 2.6 Operation Log Management
- Records all control requests and response results, including request time, response time, and operation parameters.
- Supports time range query functionality, allowing users to specify start and end dates to query historical records.
- Provides slave unit statistics functionality, calculating on/off counts, total costs, and detailed adjustment records per slave unit ID.
- Implements cost statistics functionality, calculating total costs within a specified time range based on actual usage duration and wind speed levels.
- Supports report generation functionality, outputting a complete report containing query time range, slave unit statistics, cost statistics, and detailed records.

#### 3. Data Management Requirements

##### 3.1 Slave Unit Status Management
- Maintains a basic information table for slave units, including fields such as slave unit ID, ID number, target temperature, current temperature, current wind speed, cumulative energy consumption, and cumulative cost.
- Supports real-time updates of slave unit status, synchronizing temperature changes, wind speed adjustments, and cost accumulation operations to the database timely.
- Provides a slave unit status query interface, supporting queries of a single slave unit status by ID or all slave units' status.

##### 3.2 Request Queue Management
- Maintains a request information table, recording request ID, slave unit ID, requested temperature, requested wind speed, request time, etc.
- Implements request lifecycle management, tracking the complete process from request creation to completion.
- Supports request cleanup mechanism, automatically deleting completed requests from the queue.

##### 3.3 Operation Log Recording
- Maintains an operation log table, recording log ID, ID number, slave unit ID, wind speed, current temperature, target temperature, request time, response time, etc.
- Supports log query functionality, filtering log records by time range, slave unit ID, etc.
- Implements log statistics functionality, providing summary information on on/off counts, usage duration, and cost statistics.

#### 4. System Integration Requirements

##### 4.1 Web API Interface
- Provides RESTful API interface, supporting cross-domain access for easy front-end application integration.
- Implements API version management, ensuring backward compatibility of APIs.
- Provides interface status monitoring, including connection testing and error handling functionalities.

##### 4.2 Concurrency Handling
- Adopts a multi-threaded architecture with independent operation of modules such as host scheduling, cost calculation, and temperature monitoring.
- Implements thread pool management to control the number of concurrent threads, preventing system resource overload.
- Supports thread-safe data access, ensuring data consistency in a multi-threaded environment.

##### 4.3 Exception Handling
- Provides a comprehensive exception handling mechanism, including data access exceptions, request processing exceptions, calculation exceptions, etc.
- Implements error log recording, facilitating problem diagnosis and system maintenance.
- Supports graceful degradation to guarantee normal operation of core functions when some functionalities are malfunctioning.