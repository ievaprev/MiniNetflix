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

# V0.1

 **User registration and login**:
    * Users are registered with unique IDs, and their data is stored in MongoDB.  
    * Login functions use JWT tokens for authentication and session management.
    
**Movie management**:  
   * Includes listing movies, filtering by genre or release year, and sorting by release year.  
   * Users can access and filter movies.
    
**Reviews and ratings**:  
   * Users can leave reviews and ratings for movies, which requires an active user session (token).
    
**Subscription management**:  
   * Users can change their subscription plan and view their active subscription.  
   * Subscription validity is automatically set based on the selected plan duration.
    
**Analytics**:  
   * "Top Movies": identifies the highest-rated movies (average rating, review count). 
   * "Top Reviewers": identifies the most active users by review count.  
   * Both functions use MongoDB aggregation queries.

# V0.2

**Redis caching layer**:
   * Frequently accessed endpoints (movie list, filters, sorting) were cached in Redis to reduce MongoDB load.
   * Cached responses have TTL to ensure freshness.

**Analytics optimization**:
   * “Top Movies” and “Top Reviewers” results are cached in Redis, avoiding repeated heavy MongoDB aggregations.

**Review updates**:
   * When a user posts a review, Redis clears affected cache keys (movie-specific data + analytics) to keep results consistent.

# V0.3

**Chat system (Cassandra)**:
  * Users can send and retrieve chat messages stored in Cassandra.
  * Messages are partitioned by chat ID and ordered by timestamp for efficient high-write performance.
  * ChatBot using Hugging Face API was implemented.

**Audit logging (Cassandra)**:
  * All key system actions (logins, subscription changes, reviews) are stored in Cassandra audit tables.

**Two audit models implemented**:
  * By user ID (query user history)
  * By event date (query system events by day)

