Usecases
********

Assuming that there is some idea of each components, lets cook up some use cases matching the real world project scenarios.
These examples may seem simple or already been explained somewhere else on the web, however care has been taken such that the
use cases exploit the `scalable` nature on each framework.

Our setup is configured to run on single machine, however with little bit of effort same example applications
can scale to hundreads of nodes and GigaBytes of data by tuning the configurations of respective frameworks involved.

Most of these examples involve multiple services running in the background on different terminal tabs for the pipeline to work.
It is highly recommened to use application like [Guake](http://guake-project.org/).
Guake is a background running terminal application in short, preventing you from closing the terminals.


.. toctree::
   :maxdepth: 1

   1_dump_tweets.md
   2_trending_tweets.md
   3_scalable_rest_api.md
   4_spark_ml.md
   5_static_table_stackoverflow.md
   6_full_ml_model_cycle.md
   7_spark_on_k8s.md
   8_online_lda_pyspark.md
