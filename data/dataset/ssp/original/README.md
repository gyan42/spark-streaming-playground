### Dataset
|File Name|Records|Info|Columns|
|---------|-------|----|------|
|ssp_tweet_dataset.parquet| 30K+|Full Raw Dataset|['created_at', 'text', 'source', 'expanded_url', 'media_url_https']|
|ssp_train_dataset.parquet | 27K+|Train Data|['created_at', 'text', 'source', 'expanded_url', 'media_url_https']|
|ssp_LF_dataset.parquet|1000|Snorkell Dataset|["id", "text", "label"]|
|ssp_test_dataset.parquet | 1000| Test Data|["id", "text", "label"]|
|ssp_val_dataset.parquet | 500|Validation Data|["id", "text", "label"]|