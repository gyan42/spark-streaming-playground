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

Code base can be found @ `https://github.com/gyan42/spark-streaming-playground <https://github.com/gyan42/spark-streaming-playground/>`_.

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

   ssp/modules.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
