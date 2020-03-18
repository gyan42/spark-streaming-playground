### Use Case : Streaming ML Classification with Active Learning Model
- In this use case we are gonna build ground up dataset from scratch from live streaming data. 
- Use programmatic methods to tag dataset, create golden dataset for ML training, 
in an iterative manner till we are satisfied with model performance.
- Build model and evaluate it on golden dataset
- Deploy the model, classify the text
- Extract the web links from tweets and store the urls

**[Snorkel](https://www.snorkel.org/)**
A semi automated way of preparing the dataset at scale for later use.

**Tagger**

- Mannual annotation plays a major role in ML pipeline, where humans needs to infuse domain information in ot ML model.
- There are more advanced tools like [https://prodi.gy/](https://prodi.gy/).
- But to keep things tiddy and simple, a simple web tool has been put in place to get a hands on experience with respect to text classification.

`bin/tagger.sh`

Main screen...
![](images/text_tagger1.png)

Upload CSV data...
![](images/text_tagger_upload_csv.png)

Upload Labels file...
![](images/text_tagger_labels.png)

Main Tagger Screen...
![](images/text_tagger_screen.png)