#export USER=mageswarand
#export EMR_SPARK_MASTER=ec2-18-212-195-31.compute-1.amazonaws.com
#if [ -z "$EMR_SPARK_MASTER" ]
#then
#      echo "Export user name and Spark master machine IP: \n export USER=mageswarand \n export EMR_SPARK_MASTER=ec2-54-196-93-28.compute-1.amazonaws.com"
#else
#      make build
#      rsync -rvz -e "ssh -p 3022" pytarget $USER@$EMR_SPARK_MASTER:/home/$USER/
#      ssh -p 3022 $USER@$EMR_SPARK_MASTER "cd pytarget/; cp config/text_processing/* .; spark-submit --jars udf.jar  --packages io.delta:delta-core_2.11:0.4.0 --py-files=cdr.zip --conf spark.databricks.delta.retentionDurationCheck.enabled=false --conf spark.executor.memory=25g  --conf spark.executor.cores=3 --conf spark.executor.instances=50 --conf spark.dynamicAllocation.enabled=false text_processing_aws_rxnorm_main.py --spark_master=yarn --db_config_env=serverless_aurora_development --config_dir_path=./config/ --run_environment=development --s3_bucket=dp-dev-iris --config_file=vh.iris2.ini --log_level=ERROR --run_manually=$IS_MANNUAL --is_ingestion=False --step_name=extract_text |& tee log.txt"
#fi