### Chengqingdao Area 1 Multi-Round Lottery Management System PRD

#### 1. Requirement Overview 
The "Chengqingdao Area 1 Multi-Round Lottery Management System" is a command-line lottery tool designed for internal corporate events. It supports participant management, configuration of multi-round lottery rules, execution of weighted probability lotteries, and result recording. The system should implement lottery logic based on a weighted random sampling algorithm, allow customization of the number of winners and individual winning probabilities per round, display results using colored command-line output, and offer functionalities to query and persistently store historical lottery records.

#### 2. Basic Functional Requirements

##### 2.1 Participant Management Module
- Supports adding participant information including name (required), department (optional), and initial weight value (default 1.0).
- Supports deleting specified participants by name with double confirmation and verification of participant existence.
- Supports modifying participant weight values (range: 0.1–10.0, step: 0.1), effective immediately after modification.
- Provides participant list viewing, displaying name, department, current weight value, and cumulative win count.
- Supports saving participant lists to local CSV files (Comma-Separated Values format) and loading from files.

##### 2.2 Lottery Rule Configuration Module
- Supports creating multi-round lottery plans, with each round requiring a unique round name (e.g., "Star of the Quarter," "Lucky Prize").
- Each round can independently set: number of winners (1–N, N≤ current number of participants), participant range (all participants/specified departments), lottery mode (allow repeated winners/prohibit repeated winners).
- Supports configuring individual weight coefficients for specified participants in single rounds (overrides global weight; weight calculation: final weight = global weight × round coefficient).
- Provides a preview of configured lottery rules, showing round order, round parameters, and participant weight details.
- Supports saving/loading lottery rule configurations to/from JSON files.

##### 2.3 Lottery Execution Engine Module
- Implements a weighted random sampling algorithm (supports Alias Method optimization, ensuring O(n) preprocessing and O(1) per-sample time complexity).
- During lottery execution, real-time validation of: number of winners not exceeding number of participants, total weight not being zero, and winners in non-repetition mode being automatically excluded.
- Upon the completion of each round, automatically updates participants’ cumulative win count (based on lottery mode configuration).
- Supports interrupting the current round and rolling back state (only available when results are not yet saved).
- Multi-round lottery executes in configured order, capable of executing a single round or all rounds consecutively.

##### 2.4 Result Display and Recording Module
- Lottery results are displayed through colored command-line output (using ANSI Escape Sequences: winner's name in red, round title in blue).
- Displayed content includes: round name, draw time, number of winners, winner list (including name, department, winning weight for this round).
- Supports saving results of a single/all rounds to CSV files, fields include: round ID, round name, draw time, name, department, winning weight, cumulative win count.
- Provides a historical record query function, supporting filters by date range, round name, participant name.
- Query results support command-line pagination, displaying 10 records per page.

##### 2.5 Command-Line Interaction Control Module
- On system startup, displays the main menu with options: 【1】Participant Management 【2】Rule Configuration 【3】Execute Lottery 【4】Query Results 【5】Exit System.
- All user input must be validated (numeric range, string format, file path validity).
- Error messages are displayed in Chinese (e.g., "Weight value must be between 0.1 and 10.0", "Participant list is empty, cannot execute lottery").
- Supports shortcut key operations (e.g., number keys to select menu, Enter to confirm, Esc to return to the previous level).
- Critical operations (delete participant, clear rules) require double confirmation to prevent incorrect operations.

---