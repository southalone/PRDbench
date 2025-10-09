### Company Team Building Event Smart Lottery System PRD

#### 1. Requirement Overview
This system is designed for company team building events (including annual meetings, department gatherings, etc.) and supports multi-round and multi-rule lottery processes. The system needs to integrate list management, custom prize configuration, a complex lottery rule engine (including group avoidance, special rules, and fallback mechanisms), and control the lottery process and display results through command line interaction to ensure fairness and adaptability to different scenarios.

#### 2. Basic Functional Requirements

##### 2.1 List Management Module
- Supports two list loading modes: load the built-in default team building list (including names and department group information); upload a custom txt list (format: each line "Name,Department Group" e.g., "Zhang San, Technology Department").
- List verification function: automatically detects and prompts duplicate names and format errors; supports manually removing invalid data or terminating the upload.
- Group information extraction: parses department groups from the list, supports viewing the current valid group list and the number of people in each group.

##### 2.2 Prize Configuration Module
- Prize library management: supports a preset prize library (e.g., "Third Prize - Movie Ticket", "Second Prize - Shopping Card", "First Prize - One Day Off") and adding custom prizes (enter prize name, quantity, associated lottery participants).
- Group avoidance rule configuration: set "avoidance groups" for each prize (e.g., the "Technology Department Exclusive Coupon" prize needs to avoid the "Product Department" group), supporting multiple group selections.
- Prize sorting function: adjust the lottery round order by entering the sequence number via command line, defaulting to the order of addition.

##### 2.3 Lottery Process Control
- Multi-round lottery execution: start the lottery in the configured order, displaying the current prize name, quantity, and rule description for each round.
- Manual control function: supports entering "pause" during the lottery to interrupt the process, entering "resume" to continue; entering "terminate" to end the current round and skip it.
- Real-time progress display: dynamically shows "Drawing the Xth winner" during the lottery, with winning results refreshed in real-time (format: "Congratulations [Name] ([Department]) for winning [Prize Name]").

##### 2.4 Lottery Rule Engine
- Basic filtering logic: automatically exclude previous winners and members of the current prize's "avoidance group" in each round.
- Special lottery participant rule: when the participant is specified as "Li Bin", only exclude previous winners and do not apply "avoidance group" rules.
- Fallback mechanism (Cheng Ru Group Guarantee): if the consecutive lottery results of two participants (Chen Qixian, Jin Duo) do not include "Cheng Ru Group" members, the next participant (Ma Jiaqi) must have their prize pool restricted to "Cheng Ru Group" members (even if the group is an avoidance group for the current prize).
- Anti-duplication check: the system maintains a real-time winning list to ensure the same person cannot win repeatedly (regardless of prize type).

##### 2.5 Result Management and Display
- Real-time result display: after each round of the lottery, display this round's results in the order of winning; after all rounds, summarize the complete winning list by "prize level from high to low" and "winning time order within the same prize" (including name, department, prize name).
- Result export function: supports exporting the complete winning list as a txt file (path: current directory/awards_result_YYYYMMDD.txt), in CSV format (Name, Department, Prize Name, Winning Time).