# Adjust EXEC_MEM, NUM_CORES, CORES_MAX as per your machine capacity
printf "Make sure you are running \"start_kafka_producer.sh\" \n\n Eg: bin/start_kafka_producer.sh \n\n"
#read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
make build
export EXEC_MEM=3g
export NUM_CORES=3
export CORES_MAX=6
spark-submit \
--conf "spark.executor.memory=${EXEC_MEM}" \
--conf "spark.executor.cores=${NUM_CORES}" \
--conf "spark.cores.max=${CORES_MAX}" \
--conf "spark.jars=libs/postgresql-42.2.10.jar" \
--packages org.postgresql:postgresql:9.4.1211 \
--packages postgresql:postgresql:9.1-901-1.jdbc4 \
--driver-class-path ~/.ivy2/jars/org.postgresql_postgresql-9.4.1211.jar \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4,org.apache.kafka:kafka-clients:2.4.0,io.delta:delta-core_2.11:0.4.0 \
--py-files dist/streaming_pipeline.zip src/ssp/spark/streaming/consumer/twiteer_stream_consumer_main.py --mode=visualize