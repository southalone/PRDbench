# MinNE Layered Network Simulation and Protocol Stack Implementation Platform PRD

## 1. Requirement Overview

This platform is designed to build a comprehensive layered network simulation system. It implements virtual modeling of various network devices (hosts, switches, routers) using Python and supports end-to-end data transmission across complex network topologies. The system is based on socket communication, implementing a full network protocol stack from the physical layer to the application layer. It covers key network technologies like frame synchronization and positioning, CRC-16 error detection and control, Dijkstra dynamic routing algorithm, port address learning, and flow control. The platform supports reliable transmission of Chinese, English text, and image files, providing a comprehensive technical solution for network protocol research, teaching experiments, and simulation testing.

## 2. Basic Functional Requirements

### 2.1 Network Device Simulation Module

#### 2.1.1 Host Device Simulation
- **Device Identification & Port Assignment**: Each host is assigned a unique device number (e.g., "1", "2", "4", "7"); the application layer port format is `1{device_id}300`, and the network layer port format is `1{device_id}200`
- **Application Layer Implementation**: Based on the AbstractLayer abstract class, implements bidirectional message sending and receiving between the console and network layer; supports data reception with buffer size `IN_NE_BUFSIZE`
- **Message Handling Capability**: The application layer must distinguish source (console/network layer), implement blocking reception and non-blocking sending, ensuring ordered message transmission

#### 2.1.2 Switch Device Simulation
- **Port Address Table Management**: Implements a SwitchTable class to maintain the mapping between local physical layer ports and remote application layer ports (format: `dict[local_port, dict[remote_port, lifetime]]`)
- **Address Learning Mechanism**: Upon receiving a data frame, automatically extracts the source address and updates the port address table; sets the lifetime to `REMOTE_MAX_LIFE`, decrements the lifetime of all entries by 1 on each frame processing, and removes expired entries automatically
- **Forwarding Decision Logic**:
  - Unicast: Look up the destination address in the port address table, find the corresponding local port for forwarding
  - Broadcast: Forward data to all physical layer ports except the receiving port
  - Flooding: If the destination address is unknown, forward to all ports except the receiving port

#### 2.1.3 Router Device Simulation
- **Routing Table Structure**: Implements a RouterTable class, contains two-level mapping: WAN environment (router_id -> Path structure) and LAN environment (host_id -> exit_port)
- **Dijkstra Algorithm Implementation**: Dynamic routing computation, maintains the shortest path to each destination, including fields: next (next hop), exit (exit port), cost, optimized (optimization status)
- **Routing Information Exchange**: Supports routing packet format `device:dst-cost|dst-cost|...:$` for packaging and unpacking, enabling distributed synchronous routing table updates
- **Address Mapping & Lookup**: Supports 5-digit port number format for address resolution; implements reverse mapping lookup from application layer to physical layer ports

### 2.2 Network Protocol Stack Implementation Module

#### 2.2.1 Frame Structure and Encoding/Decoding
- **Frame Format Definition**: Uses a fixed frame structure that includes:
  - Frame locator: 8-bit fixed pattern `01111110`
  - Source port: 16-bit binary encoding
  - Session status: 2 bits (NORMAL="00", FIN="01", REQ_TXT="10", REQ_IMG="11")
  - Acknowledgement flag: 1 bit (ACK="1", NAK="0")
  - Sequence number: 1 bit alternating sequence number
  - Data segment: 32-bit variable length data
  - Destination port: 16-bit binary encoding
  - CRC check: 16-bit cyclic redundancy check code
- **Transparent Transmission Handling**: Implements bit stuffing algorithm, inserts '0' after detecting 5 consecutive '1's, ensuring uniqueness of the frame locator
- **Frame Construction & Parsing**: Provides FrameBuilder and FrameParser classes for complete processes of frame construction, validation, and parsing

#### 2.2.2 Error Detection & Control
- **CRC-16 Check Implementation**: Uses the generator polynomial 0xA001 for cyclic redundancy checking on frame content to detect bit errors during transmission
- **Check Code Calculation**: Based on the standard CRC-16 algorithm, initial value 0xFFFF, supports check code generation for binary data of any length
- **Error Control Protocol**:
  - Stop-and-Wait ARQ: Sender waits for ACK confirmation after sending a frame; retransmits on timeout
  - Sequence Number Mechanism: Uses alternating 0/1 sequence numbers to prevent reception of duplicate frames
  - NAK Feedback: Receiving side sends NAK upon error detection, triggering immediate retransmission

#### 2.2.3 Flow Control Mechanism
- **Sending Rate Constraint**: Sets maximum transmission interval to prevent sender overload of receiver buffer
- **Buffer Management**: Sets communication buffer for inter-network-element (`INTER_NE_BUFSIZE`) and intra-network-element (`IN_NE_BUFSIZE`)
- **Congestion Control Strategy**: Dynamically adjusts send window size based on packet loss rate and latency feedback, implementing adaptive flow control

### 2.3 Data Transmission and File Processing Module

#### 2.3.1 Multimedia Data Support
- **Text Data Processing**: Supports transmission of UTF-8 encoded Chinese and English characters, punctuation, two-way conversion between string and binary
- **Image File Transmission**: Supports binary transmission of PNG format images; implements framing and reassembly for large files
- **Data Fragmentation Mechanism**: When data length exceeds single frame capacity (32 bits), automatically fragments into multiple frames for transmission; supports reassembly and out-of-order handling

#### 2.3.2 Session Management & File Storage
- **Session Status Management**: Implements full session lifecycle including connection establishment, data transmission, and connection termination
- **Automatic File Saving**: Received image files are automatically saved to the resource directory; file naming format is `received-{timestamp}.png`
- **Transmission Progress Tracking**: Provides file transmission progress feedback; supports transmission status inquiry and exception handling

### 2.4 Network Topology Configuration and Management Module

#### 2.4.1 Topology Configuration System
- **JSON Configuration Format**: Uses a structured JSON configuration file (devicemap.json) to define device types, connection relationships, and routing information
- **Phased Configuration Management**: Supports independent configurations for four experimental stages, including device mapping table, physical layer configuration, and batch script version management
- **Configuration Validation Mechanism**: Automatically validates configuration file integrity and consistency at startup, including port conflict detection and connectivity verification

#### 2.4.2 Device Discovery & Mapping
- **Device Type Recognition**: Automatically detects host, switch, and router device types and assigns appropriate functional modules
- **Port Mapping Management**: Maintains mapping from device number to port number, supports dynamic port allocation and conflict detection
- **Topology Relationship Maintenance**: Real-time maintenance of physical connections between devices; supports dynamic topology change awareness

### 2.5 Command Line Interface and Control Module

#### 2.5.1 Startup Control System
- **Phased Startup**: Specify simulation stage (2-4) via command line parameters; automatically loads corresponding configuration and starts relevant modules
- **Batch Processing Integration**: Supports automatic execution of Windows batch files for one-click startup and shutdown
- **Error Handling Mechanism**: Automatic detection and alerting of exceptions such as port occupancy and configuration errors during startup

#### 2.5.2 Interactive Console
- **Real-time Command Interaction**: Provides command line interface; supports device status inquiry, parameter adjustment, manual data sending
- **Status Display Functionality**: Real-time display of key information such as routing tables, port address tables, device connection status
- **Debug Mode Support**: Offers detailed debug info output; supports single-step execution and breakpoint debugging