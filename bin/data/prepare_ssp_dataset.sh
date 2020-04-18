make build
#read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python3 src/ssp/ml/dataset/prepare_dataset_main.py --config_file=config/default_ssp_config.gin --version=0 --mode=split
