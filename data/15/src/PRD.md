### Career Development Assessment and Interview Preparation System PRD

#### 1. Overview of Requirements
This system is an integrated career development support tool designed to help users with career competency diagnosis, interview preparation, and career planning through scientific assessment methods. Based on the Competency Model and Behavioral Interview theory, the system provides question generation, mock interviews, competency evaluation, and visual analysis features to help users comprehensively improve their career competitiveness.

#### 2. Basic Functional Requirements

##### 2.1 Career Competency Question Bank Generation Module
- Supports the generation of four types of questions: single-choice (knowledge understanding), multiple-choice (competency judgment), true/false (concept evaluation), and situational analysis (behavioral description)
- Users can customize the number of questions for each type (1-50) and difficulty level (Beginner/Intermediate/Advanced)
- Questions must cover six major career competency dimensions: professional knowledge, problem-solving, teamwork, communication & expression, learning ability, and professional conduct
- Each question must include a standard answer, competency dimension tag, and detailed analysis (using the STAR method)
- Supports exporting the generated question bank as an Excel file, including fields such as questions, options, answers, analysis, and competency dimensions

##### 2.2 Mock Interview and Evaluation System
- Provides two interview modes: structured interview (preset question bank) and random interview (dynamically generated questions)
- Supports timing functionality that records the user's thinking time for each question and total duration
- Users can input answers, and the system will automatically score them based on preset scoring criteria (1-5 points)
- Scoring dimensions must include: completeness of answer (20%), clarity of logic (25%), professional depth (30%), and fluency of expression (25%)
- After the interview, generates a comprehensive evaluation report containing a radar chart of scores across competency dimensions and recommendations for improvement

##### 2.3 Career Development Planning Generator
- Based on Career Anchor Theory, assesses the user's career anchor type (technical/managerial/creative/autonomous, etc.—8 types) via a 12-question scale
- Combines competency evaluation results to generate personalized development path suggestions, including:
  - Three core competencies to prioritize for improvement
  - Recommended learning resources and sources
  - Staged goal setting (short-term/mid-term/long-term)
- Supports exporting the development plan in Markdown format, including an action plan timetable and competency improvement milestones