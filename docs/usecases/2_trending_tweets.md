
# Use Case : Trending Twitter Hash Tags

## Requirements
- Read raw twitter data from Bronze lake
- Extract all hash tags in a new column
- Store the hash tags in Postgresql DB table
- Design a simple naive dash board with Bar charts for trending tweets 

## Implementation

- Read the Bronze lake parquet raw data into Spark Structured input stream
- Create a new column with `UDF` to extract the hash tags and use `explode` on array of hash tags to create new row for each hashtag 
- With `foreachParition` API, dump the data into Postgresql DB table
- In Flask backend read the data from  Postgresql DB table
- Use plotly to create Bar chart and display it on the HTML page

Below is the data flow path:

`Bronze Lake -> Spark Structured Streaming Parquet Source -> Extract Hash Tags with UDF -> Spark Structured Streaming Postgresql Sink`

`Postgresql -> Flask REST API -> Web Application`

## How to run?

There are two ways of running, that is on docker or on your local machine. In either case, opening the terminal
is the difference, once the terminal is launched, the steps are common. 

To get a new terminal for our docker instance run : `docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash`
Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

This example needs two terminals:

- Hashtag [bin/trending_tweet_hashtags.sh](../../bin/trending_tweet_hashtags.sh)
    - `Bronze Lake -> Spark Structured Streaming Parquet Source -> Extract Hash Tags with UDF -> Spark Structured Streaming Postgresql Sink`
    - [src/ssp/analytics/trending_hashtags_main.py](../../src/ssp/analytics/trending_hashtags_main.py)    
- Dashboard [bin/dashboard.sh](../../bin/dashboard.sh)
    - `Postgresql -> Flask REST API -> Web Application`
    - [src/ssp/dashboard/app.py](../../src/ssp/dashboard/app.py)
    

```
cd /path/to/ # Local machine
cd /host  # Docker
#[hashtag] Guake terminal name! 
    bin/trending_tweet_hashtags.sh

#[dashboard] Guake terminal name! 
    bin/dashboard.sh
```
 
Head to http://0.0.0.0:5001/ for live count on the trending #hashtags
 ![](../images/trending_tags.png)