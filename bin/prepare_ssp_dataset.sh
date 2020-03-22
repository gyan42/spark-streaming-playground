make build
read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python3 src/ssp/dataset/twiteer_stream_ingestion_main.py --mode=ssp_dataset