make build
#read -p "Press any key to continue... " -n1 -s
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python3 src/ssp/ml/prepare_dataset.py --config_file=config/default_ssp_config.gin