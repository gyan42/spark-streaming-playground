## Architecture of Spark



- Spark Driver (Master Process)
  - Converts the Spark code into tasks and schedules them using **Task Scheduler **for Executors
- Spark Cluster Manager
  - Launches executors and driver(s) in `cluster` deploy mode
- Spark Executors (Slave Process)
  - Where the Tasks are run

