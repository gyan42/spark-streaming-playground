'''
Created on 05-May-2020

@author: srinivasan
'''
#!/usr/bin/env python

import argparse
import gin

from ssp.spark.streaming.lda.model import LdaModelOperation

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/scrapy_config.gin",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="lad_model_train, online_lad_model_predict]")

    parsed_args = optparse.parse_args()
    
    gin.parse_config_file(parsed_args.config_file)
    
    ldamode_ope = LdaModelOperation()
    
    if parsed_args.mode == "lad_model_train":
        ldamode_ope.trainLDA(10, 100)
    elif parsed_args.mode == "online_lad_model_predict":
        ldamode_ope.predicateData('', '')
    else:
        raise RuntimeError("Invalid choice")
