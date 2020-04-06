# Spark Basics

**RDD (Resilient Distributed Datasets) –** A RDD is a distributed  collection of immutable datasets on distributed nodes of the cluster. An RDD is partitioned into one or many partitions. RDD is the core of  spark as their distribution among various nodes of the cluster that  leverages data locality. To achieve parallelism inside the application,  Partitions are the units for it. Repartition or coalesce transformations can help to maintain the number of partitions. Data access is optimized utilizing RDD shuffling. 



Spark distributed collection RDD API has two set of operations:

- Transformation
- Actions



![](images/schedule-process.png)



Consider following simple line count for given word example:

```scala
/* SimpleApp.scala */
val logFile = "YOUR_SPARK_HOME/README.md"
val spark = SparkSession.builder().master("local").appName("WordCount").getOrCreate()
val sc = spark.sparkContext
// Read and cache the data
val logData = sc.textFile(logFile, 2).cache()
// filter -> Transformation; count -> Action
val numAs = logData.filter(line => line.contains("and")).count()
println("Lines with a: %s".format(numAs))
```



```bash
Spark Application ---> DataFrames / Datasets 
                  ---> RDDs 
                  ---> Operator Graph 
                  ---> DAGScheduler 
                  ---> Actions (Jobs) 
                  ---> Stages (shuffle boundaries) 
                  ---> Tasks (equal to number of partitions) 
```



![](images/spark_execution_model.png)

- Build `Stages` of `Task` objects (code + preferred location)
- Submit them to `TaskScheduler` as ready
- Resubmit failed `Stages` if outputs are lost The `TaskScheduler` is responsible for launching tasks at `Executors` in our cluster, re-launch failed tasks several times, return the result to `DAGScheduler`. We can now quickly summarize:
- We submit a jar application which contains jobs
- The job gets submitted to `DAGScheduler` via `SparkContext` will be split into `Stages`. The `DAGScheduler` schedules the running order of these stages.
- A `Stage` contains a set of `Tasks` to run on `Executors`. The `TaskScheduler` schedules the run of tasks.

 

![](images/dependencies.png)



- **Narrow dependency**:  each partition of the parent `RDD` is used by at most one partition of the child `RDD`. This means the task can be executed locally and we don’t have to shuffle. (Eg: `map`, `flatMap`, `filter`, `sample`)
- **Wide dependency**: multiple child partitions may depend on one partition of the parent `RDD`. This means we have to shuffle data unless the parents are hash-partitioned (Eg: `sortByKey`, `reduceByKey`, `groupByKey`, `cogroupByKey`, `join`, `cartesian`) Thanks to the lazy evaluation technique, the `Scheduler` will be able to optimize the stages before submitting the job:  pipelines narrow operations within a stage, picks join algorithms based  on partitioning (try to minimize shuffles), reuses previously cached  data.

Reference Video : https://www.youtube.com/watch?v=49Hr5xZyTEA

## Spark Internals

https://github.com/JerryLead/SparkInternals



## API Examples

RDD: http://homepage.cs.latrobe.edu.au/zhe/ZhenHeSparkRDDAPIExamples.html

Dataset : https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/8963851468310921/1413687243597086/5846184720595634/latest.html



