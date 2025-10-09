# Intelligent Business Travel Planning System PRD

## 1. Requirement Overview
This project aims to develop an intelligent business travel planning system based on command-line interaction, integrating transportation data and itinerary management functions. The system should support users in inputting multi-city business trip requirements, generate time-optimal/cost-optimal/balanced transportation plans using an improved weighted directed graph algorithm, and provide prioritized sorting suggestions based on decision fatigue theory. It should also have conflict detection and multi-format export capabilities, offering end-to-end decision support for business travelers.

## 2. Basic Functional Requirements

### 2.1 Itinerary Information Management Module
- Supports user input for departure city, multiple destination cities, and duration of stay (accurate to the hour)
- Supports adding time window constraints (e.g., "Must arrive in Shanghai before 14:00 for a meeting")
- Provides itinerary template saving, allowing storage of commonly used business travel routes (e.g., "Beijing-Tianjin-Hebei three-day exhibition tour")

### 2.2 Multi-Objective Transportation Plan Generation Module
- Integrates simulated high-speed rail/flight data (including train/flight number, departure and arrival time, stopover stations, ticket price, and 12 other parameters)
- Implements an improved Dijkstra algorithm to calculate optimal paths between cities, with weighted factors including:
  - Basic weight: travel time (unit: minutes)
  - Penalty terms: number of transfers × 60 minutes + departures earlier than 6:00 × 120 minutes
  - Adjustment factors: user preference coefficients (time sensitivity/cost sensitivity)
- Provides three types of optimized schemes:
  - Time optimal: minimize total travel time (including transfer waiting)
  - Cost optimal: minimize total transportation expenditure (applying price elasticity coefficient)
  - Balanced scheme: computes time-cost integrated score via TOPSIS method
- Supports setting maximum number of transfers (1-3) and transportation mode preference (High-speed rail preferred/Flight preferred/No preference)

### 2.3 Intelligent Itinerary Conflict Detection Module
- Implements a time conflict detection algorithm based on Allen’s interval algebra, identifying the following conflict types:
  - Hard conflicts: insufficient connection time between transport modes (e.g., ≥90 minutes required for high-speed rail to flight)
  - Soft conflicts: rest time between consecutive journeys <4 hours (based on fatigued driving safety standards)
- Provides visual conflict prompts (timeline overlap markers)
- Automatically generates conflict resolution solutions:
  - Time adjustment recommendations (e.g., "Move Beijing-Shanghai high-speed rail to G107")
  - Itinerary splitting recommendations (e.g., "Add one night stay in Nanjing")

### 2.4 Decision Support Recommendation Module
- Builds a decision evaluation model based on Prospect Theory, calculating for each plan:
  - Value function: v(x) = x^α (gain) or -λ(-x)^β (loss)
  - Weight function: π(p) = p^γ / [p^γ + (1-p)^γ]^(1/γ)
- Implements multi-attribute decision matrix with quantifiable evaluation metrics including:
  - Time efficiency (30% weight)
  - Economic cost (25% weight)
  - Comfort index (20% weight, based on seat space/on-time rate)
  - Reliability score (15% weight, based on historical delay data)
  - Transfer convenience (10% weight, based on transfer distance within stations)

### 2.5 Itinerary Export and Sharing Module
- Supports generating various itinerary report formats:
  - Markdown format (including itinerary timeline and transportation details)
- Implements itinerary summary generation, automatically extracting key information:
  - Total travel distance (calculated by Haversine formula based on geographic coordinates)
  - Total time/total cost statistics
  - Key node reminders (e.g., "Tomorrow 08:30 Beijing South Station G109")

### 2.6 Command Line Interaction System
- Implements multi-level command menu system, supports shortcut operations (e.g., "Ctrl+S" to save itinerary)
- Provides real-time input validation, including:
  - City name standard check (based on GB/T 2260 administrative division codes)
  - Date format validation (supports relative dates, e.g., "Tomorrow"/"Next Monday")
  - Time logic validation (e.g., "Arrival time cannot be earlier than departure time")