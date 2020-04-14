# Adjust EXEC_MEM, NUM_CORES, CORES_MAX as per your machine capacity
printf "Make sure you have Apache Spark server is running and appropriate Spark master url is used in the config! \n\n"
printf "You Spark Home is : ${SPARK_HOME}"
printf "\t\tEg: ${SPARK_HOME}sbin/start-all.sh\n\n"
#read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
make build
export EXEC_MEM=3g
export NUM_CORES=5
export CORES_MAX=10

FILE=data/dataset/sentiment/sentiment140/training.1600000.processed.noemoticon.csv
if test -f "$FILE"; then
    echo "$FILE exist"
else
    unzip data/dataset/sentiment/sentiment140.zip -d data/dataset/sentiment/sentiment140/
fi

spark-submit \
--conf "spark.executor.memory=${EXEC_MEM}" \
--conf "spark.executor.cores=${NUM_CORES}" \
--conf "spark.cores.max=${CORES_MAX}" \
--py-files=dist/streaming_pipeline.zip \
--packages io.delta:delta-core_2.11:0.4.0 src/ssp/spark/streaming/ml/sentiment_analysis_model_main.py