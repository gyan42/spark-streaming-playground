'''
Created on 04-May-2020

@author: srinivasan
'''
import gin
from pyspark import StorageLevel
from pyspark.ml import Pipeline
from pyspark.ml.clustering import LDA, LocalLDAModel
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import monotonically_increasing_id, col
from sparknlp.annotator import (Tokenizer, Normalizer,
                                LemmatizerModel, StopWordsCleaner,
    NGramGenerator, SentenceDetector)
from sparknlp.base import Finisher, DocumentAssembler

from nltk.corpus import stopwords
from ssp.spark.streaming.consumer.scrapy_stream_consumer import ScrapyStreamBase


class Preprocessor:
    
    def __init__(self, src_col_nm, stopwords=[]):
        self._src_col_nm = src_col_nm
        self._stopwords = stopwords
        self._vocabArray = None
    
    def trasnform(self, df:DataFrame) -> DataFrame:
        data = df.filter((df[self._src_col_nm].isNull() == False))
        pipelinemodel = self.__getPipeLine().fit(data)
        self._vocabArray = pipelinemodel.stages[-1].vocabulary
        trans_data = pipelinemodel.transform(data)
        return trans_data.withColumn("index",
                                          monotonically_increasing_id())
    
    def __getPipeLine(self):
        eng_stopwords = stopwords.words('english')
        eng_stopwords.extend(self._stopwords)
        documentAssembler = DocumentAssembler() \
            .setInputCol(self._src_col_nm) \
            .setOutputCol('document')
        
        sentenceDetector = SentenceDetector()\
          .setInputCols(["document"])\
          .setOutputCol("sentence")
        
        tokenizer = Tokenizer() \
            .setInputCols(['sentence']) \
            .setOutputCol('token')
            
        normalizer = Normalizer() \
            .setInputCols(['token']) \
            .setOutputCol('normalized') \
            .setLowercase(True)
        lemmatizer = LemmatizerModel.pretrained() \
            .setInputCols(['normalized']) \
            .setOutputCol('lemma') \
        
        stopwords_cleaner = StopWordsCleaner() \
            .setInputCols(['lemma']) \
            .setOutputCol('clean_lemma') \
            .setCaseSensitive(False) \
            .setStopWords(eng_stopwords)
        
        ngrams_cum = NGramGenerator() \
                    .setInputCols(["clean_lemma"]) \
                    .setOutputCol("ngrams") \
                    .setN(2) \
                    .setEnableCumulative(True)
                    
        finisher = Finisher() \
            .setInputCols(['ngrams']) \
            .setCleanAnnotations(False)
            
        cv = CountVectorizer(inputCol='finished_ngrams',
                         outputCol='features')
        
        return Pipeline() \
            .setStages([
                documentAssembler,
                sentenceDetector,
                tokenizer,
                normalizer,
                lemmatizer,
                stopwords_cleaner,
                ngrams_cum,
                finisher,
                cv
            ])


@gin.configurable
class LdaModelOperation(ScrapyStreamBase):
    
    def __init__(self,
                 model_path,
                 data_path,
                 spark_master,
                 checkpoint_dir,
                 warehouse_location,
                 kafka_bootstrap_servers,
                 kafka_topic,
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming",
                 processing_time='60 seconds'):
        
        super().__init__(spark_master, checkpoint_dir, warehouse_location,
                 kafka_bootstrap_servers, kafka_topic, processing_time)
        self._model_path = model_path
        self._data_path = data_path
        self._model_id = None
        self._postgresql_database = postgresql_database
        self._jdbc_url = f'jdbc:postgresql://{postgresql_host}:{postgresql_port}/{postgresql_database}'
        self._db_properties = {'user':postgresql_user,
                               'password':postgresql_password,
                               'driver':'org.postgresql.Driver'}
        self._pre_pocess = Preprocessor('headline')
    
    def __getSourceData(self):
        
        return self.sparkSession.read. \
            format("parquet"). \
            option("ignoreChanges", "true"). \
            option("failOnDataLoss", "false"). \
            load(self._data_path)
    
    @gin.configurable
    def trainLDA(self, num_topics, max_iterations):
        sdf = self.__getSourceData()
        sdf.persist(StorageLevel.MEMORY_AND_DISK)
        if len(sdf.head(1)) > 0:
            from pyspark.sql.functions import udf
            df = self._pre_pocess.trasnform(sdf).\
                select('index', 'features')
            vocabArray = self._pre_pocess._vocabArray
            df.persist(StorageLevel.MEMORY_AND_DISK)
            lda = LDA(k=num_topics, seed=1, maxIter=max_iterations)
            ldaModel = lda.fit(df)
            """
            Save model into hdfs
            """
            ldaModel.write().overwrite().save(self._model_path)
            topics = ldaModel.describeTopics()
            list_of_index_words = udf(lambda wl: list([vocabArray[w] 
                                                       for w in wl]))
            topic_df = topics.select('topic',
                                     list_of_index_words(topics.termIndices).alias('words'))
            
            topic_df.write.jdbc(url=self._jdbc_url,
                          table='topics',
                           mode='overwrite', properties=self._db_properties)
            """
            Write Runtime information into postgres server
            """
            self.__writeRuntimeInfo()
            
    def __writeRuntimeInfo(self) -> DataFrame:
        import time 
        import json
        runtime_json = json.dumps({"model_runId":str(int(round(time.time() * 1000))),
                        "model_path":self._model_path}) 
        run_df = self.sparkSession.read.json(self.sparkSession\
                    .sparkContext.parallelize([runtime_json]))
        run_df.write.jdbc(url=self._jdbc_url,
                          table='model_info',
                           mode='overwrite', properties=self._db_properties)
    
    @gin.configurable
    def predicateData(self, processing_time, tar_path):
        if processing_time:
            self._processing_time = processing_time
        sdf = self._get_source_stream(self._kafka_topic)

        def foreach_batch_function(run_df, epoch_id):
            run_df.printSchema()
            if len(run_df.head(1)) > 0:
                tdf = self.__predicate(run_df)
                tdf.write.jdbc(url=self._jdbc_url,
                          table='model_result',
                           mode='append',
                           properties=self._db_properties)

        sdf.writeStream.outputMode("append").trigger(processingTime=self._processing_time)\
            .foreachBatch(foreach_batch_function)\
            .start().awaitTermination()
        """
        store predicted data into postgres
        """
        """tdf.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", tar_path). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime=self._processing_time). \
            start().awaitTermination(None)"""

    """
    add the predicated values
    """

    def __predicate(self, df:DataFrame) -> DataFrame:
        """
        prepare columns
        """
        _cols = df.columns
        _cols.extend(['topic_predict'])
        sdf = self._pre_pocess.trasnform(df)
        ldaModel = LocalLDAModel.load(self._model_path)
        transformed = ldaModel.transform(sdf)
        from pyspark.sql.functions import udf

        def predict_topic_(v):
            a = v.toArray().tolist()
            return a.index(max(a))        

        predict_topic = udf(lambda x:predict_topic_(x))
        return transformed.withColumn("topic_predict",
                        predict_topic(col("topicDistribution"))).\
                        select(_cols)
        
