printf "Make sure you are running \"dump_raw_data.sh\" \n\n\t\tEg: bin/dump_raw_data.sh \n\n"
printf "Make sure you have Apache Spark server is running and appropriate Spark master url is used in the config! \n\n"
printf "You Spark Home is : ${SPARK_HOME}"
printf "\t\tEg: ${SPARK_HOME}sbin/start-all.sh\n\n"
read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
make build
export EXEC_MEM=3g
export NUM_CORES=3
export CORES_MAX=6
spark-submit \
--conf "spark.executor.memory=${EXEC_MEM}" \
--conf "spark.executor.cores=${NUM_CORES}" \
--conf "spark.cores.max=${CORES_MAX}" \
--py-files=dist/streaming_pipeline.zip \
--packages io.delta:delta-core_2.11:0.4.0 \
--packages postgresql:postgresql:9.1-901-1.jdbc4 src/ssp/analytics/trending_hashtags_main.py \