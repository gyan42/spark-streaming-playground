.. spark-streaming-playground documentation master file, created by
   sphinx-quickstart on Mon Apr 13 12:10:20 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to spark-streaming-playground's documentation!
======================================================

The aim of the this project is to create a zoo of Big Data frameworks on a single machine,
where pipelines can be build and tested based on Twitter stream. Which involves but not limited to fetch,
store the data in data lake, play around with the Spark Structured SQLs for processing, create dataset from live
stream for Machine Learning and do interactive visualization from the data lake.

What is `Spark Streaming? <https://techvidvan.com/tutorials/spark-streaming/>`_
#########################

First of all, what is streaming? A data stream is an unbounded sequence of data arriving continuously.
Streaming divides continuously flowing input data into discrete units for processing. Stream processing is low latency
processing and analyzing of streaming data. Spark Streaming is an extension of the core Spark API that enables scalable,
high-throughput, fault-tolerant stream processing of live data. Spark Streaming is for use cases which require a
significant amount of data to be quickly processed as soon as it arrives. Example real-time use cases are:

- Website monitoring, network monitoring
- Fraud detection
- Web clicks
- Advertising
- Internet of Things sensors

Spark Streaming supports data sources such as HDFS directories, TCP sockets, Kafka, Flume, Twitter, etc.
Data Streams can be processed with Spark’s core APIS, DataFrames SQL, or machine learning APIs, and can be persisted
to a filesystem, HDFS, databases, or any data source offering a Hadoop OutputFormat.


Code base can be found @ `https://github.com/gyan42/spark-streaming-playground <https://github.com/gyan42/spark-streaming-playground/>`_.

Some common useful `Cheat Sheets <https://github.com/gyan42/spark-streaming-playground/blob/master/docs/cheat_sheets/cheat_sheets.md>`_

.. image:: drawio/big_data_zoo.png
    :align: center
    :alt: alternate text

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   setup/setup.rst
   tutorials.md
   host_urls_n_ports.md
   how_to_run.md
   usecases/usecases.rst

.. toctree::
   :maxdepth: 1
   :caption: API:

   ssp/ssp.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
