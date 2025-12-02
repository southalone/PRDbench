### Chengqingdao Area 1 Multi-Round Lottery Management System PRD

#### 1. Requirement Overview
The "Chengqingdao Area 1 Multi-Round Lottery Management System" is a command-line lottery tool designed for internal corporate activities, supporting participant management, multi-round lottery rule configuration, weighted probability lottery execution, and result recording. The system needs to implement lottery logic based on weighted random sampling algorithms, support customizing the number of winners per round and individual winning probabilities, display results through colored command-line output, and provide querying and persistent storage capabilities for historical lottery records.

#### 2. Basic Functional Requirements

##### 2.1 Participant Management Module
- Supports adding participant information, including name (required), department (optional), and initial weight value (default value 1.0).
- Supports deleting specified participants by name, requiring secondary confirmation and verification of participant existence.
- Supports modifying participant weight values (range 0.1-10.0, step size 0.1), effective immediately after modification.
- Provides participant list viewing functionality, displaying name, department, current weight value, and cumulative win count.
- Supports saving participant lists to local CSV files (Comma-Separated Values format) and loading from files.

##### 2.2 Lottery Rule Configuration Module
- Supports creating multi-round lottery plans, each round requiring a unique round name (such as "Star of the Quarter", "Lucky Prize").
- Each lottery round can independently configure: number of winners (1-N, N≤ current number of participants), participation scope (all participants/specified departments), lottery mode (allow repeated wins/prohibit repeated wins).
- Supports configuring individual weight coefficients for specified participants in single lottery rounds (overriding global weights, weight calculation method: final weight = global weight × round coefficient).
- Supports deleting a specified round, requiring secondary confirmation and checking whether the round exists.
- Provides preview functionality for configured lottery rules, displaying round sequence, round parameters, and participant weight details.
- Supports saving/loading lottery rule configurations to/from JSON files.

##### 2.3 Lottery Execution Engine Module
- Implements weighted random sampling algorithms (requires support for Alias Method algorithm optimization, ensuring O(n) preprocessing time complexity and O(1) single sampling time complexity).
- Real-time validation during lottery execution: number of winners not exceeding number of participants, total weight sum not 0, automatic exclusion of already won participants in no-repeat mode.
- After completion of single lottery round, automatically updates participants' cumulative win count (based on lottery mode configuration).
- Supports interrupting current round lottery and rolling back state (only available when results are not saved).
- Multi-round lotteries execute in configured order, supporting single round execution or continuous execution of all rounds.

##### 2.4 Result Display and Recording Module
- Lottery results displayed through colored command-line output (using ANSI Escape Sequences to control text color: winners' names in red, round titles in blue).
- Result display content includes: round name, draw time, number of winners, winner list (including name, department, winning weight for this round).
- Supports saving single round/all rounds results to CSV files, fields include: round ID, round name, draw time, name, department, winning weight, cumulative win count.
- Provides historical record query functionality, supporting filtering by date range, round name, participant name.
- Query results support command-line pagination display, showing 10 records per page.

##### 2.5 Command-Line Interaction Control Module
- System displays main menu upon startup, containing function options: 【1】Participant Management 【2】Rule Configuration 【3】Execute Lottery 【4】Result Query 【5】Exit System.
- All user input requires validity verification (numeric ranges, string formats, file path legality).
- Displays Chinese prompt messages for operation errors (such as "Weight value must be between 0.1-10.0", "Participant list is empty, cannot execute lottery").
- Supports shortcut key operations (such as number keys for direct menu selection, Enter key for confirmation, Esc key to return to previous level).
- Critical operations (deleting participants, clearing rules) require secondary confirmation to prevent misoperations.

---