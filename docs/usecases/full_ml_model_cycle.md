# Use Case : Streaming ML Classification with Active Learning Model
- In this use case we are gonna build ground up dataset from scratch from live streaming data. 
- Use programmatic methods to tag dataset, create golden dataset for ML training, 
in an iterative manner till we are satisfied with model performance.
- Build model and evaluate it on golden dataset
- Deploy the model, classify the text
- Extract the web links from tweets and store the urls

## Dataset
We are interested to collect tweets taht talks about Artificial Intelligence / Data SCience in general.

Dataset creation involves:
- Observer the Tweets
- Sample relevant tweets, with possible false positive data (i.r irrelevant tweets)
- Dataset of format `parquet` with text column and label column. (parquet nicely packs special characters without the headache os parsing the CSV files)
- Data splits

Run `bin/dump_raw_data_as_file.sh`, cratess dataset @ [data/dataset/ssp/](data/dataset/ssp/)
- data/dataset/ssp/ssp_tweet_dataset.parquet : Greater than 275000 records
- data/dataset/ssp/ssp_train_dataset.parquet : 2000 records
- data/dataset/ssp/ssp_test_dataset.parquet  : 1000 records
- data/dataset/ssp/ssp_val_dataset.parquet   : 500 records
- data/dataset/ssp/ssp_LF_dataset.parquet    : 1000 records


## Labeling
```
Raw Data -> Run python code to tag programmatically -> Vanilla Version -> Tagger -> Golden Version (small dataset) 

Golden Version (small dataset) -> Snorkel -> Labeling Functions -> Model -> Large Labelled Dataset -> (Optional) Tagger
    Labeling Functions -> Regex Rules
                       -> Clustering Models

Large Labelled Dataset -> ML Model -> Prediction
```
 
- **Tagger**

    - Mannual annotation plays a major role in ML pipeline, where humans needs to infuse domain information in to ML model.
    - Though there are more advanced tools like [https://prodi.gy/](https://prodi.gy/), I wanted to keep things tiddy and simple, 
    so a web tool has been put in place to get a hands on experience in tagging with respect to text classification.
    
    `bin/tagger.sh`
    
    In this tool, you can:
        - Upload multiple CSV/Parquet(preffered) data files with columns [id, text] and corresponding
         CSV lable files with columns [lable, index]
        - Tag each of the data files independently
        - Download the files (as matter of fact the files lives in your home folder ;) )
    
    Main screen...
    ![](../images/text_tagger1.png)
    
    Upload CSV data...
    ![](../images/text_tagger_upload_csv.png)
    
    Upload Labels file...
    ![](../images/text_tagger_labels.png)
    
    Main Tagger Screen...
    ![](../images/text_tagger_screen.png)
    
- **[Snorkel](https://www.snorkel.org/)**
    A semi automated way of preparing the dataset at scale for later use.
