# MiniNetflix

A project that aims to explore non-relational database structures, such as redis, cassandra, Neo4J. 


**Goal:** create a Netflix like database using non-relational database structures. 

**Main project tasks:**
*  Create main project skeleton while employing MongoDB.
*  Implementing chaching for more *expensive* operations and Redis-based locks.
*  Create audit and chat functionalities using Cassandra.

The project was developed using a virtual environment on the Windows operating system.

### Creating virtual enviroment
**Windows**:
```
python -m venv .venv
.\.venv\Scripts\fileName.py
```
**MacOS/Linux**:
```
python3 -m venv ./.venv
source ./.venv/bin/activate
```
---
All functions are tested through Postman. Testing logic is documented after each major implementation. 

  ## V0.1

  **Main task:** create main project skeleton while employing MongoDB.
  **Sub Tasks:**
  * Implement seed data for function testing.
  * Implement basic aggregation functions used for filtering.
  * Create user login with tokens that would allow to restrict some functions. 
