# Python - Conda Environment

Virtual environment `Conda` is used to setup the Python development
arena!

Follow the steps [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) to install `conda`.

```
#create a virtual env with a specific location, to take load out of root path
conda create --prefix=/opt/envs/ssp/ python=3.7
conda activate /opt/envs/ssp # or source activate ssp
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pip install notebook
pip install jupyterlab
```


## Juyter Lab

`jupyter-lab # http://localhost:8888/lab`
 
 
### Issues
 - https://github.com/explosion/spaCy/issues/2883
 ```
pip uninstall thinc
pip uninstall cymem
pip install spacy
```