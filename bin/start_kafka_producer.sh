make build
printf "Make sure you are running Kafka server. \n\n Eg: kafka-server-start.sh /etc/kafka.properties \n\n"
read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python3 src/ssp/dataset/twiteer_stream_ingestion_main.py --mode=start_tweet_stream