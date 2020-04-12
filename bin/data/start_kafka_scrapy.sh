make build
printf "Make sure you are running Kafka server. \n\n Eg: kafka-server-start.sh /etc/kafka.properties \n\n"
#read -p "Press any key to continue... " -n1 -s
cd src/ssp/news_scrape
scrapy crawl $1
