printf "Make sure you are running Kafka server & topic name in settings.py"
#read -p "Press any key to continue... " -n1 -s
cd src/ssp/news_scrape
scrapy crawl $1