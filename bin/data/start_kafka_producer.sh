make build
printf "Make sure you are running Kafka server. \n\n Eg: kafka-server-start.sh /etc/kafka.properties \n\n"
#read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python3 src/ssp/kafka/producer/twitter_producer_main.py