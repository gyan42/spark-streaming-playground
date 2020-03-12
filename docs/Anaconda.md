# Conda
Virtual environment `Conda` is used to setup the Python development
arena!

Follow the steps [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) to install `conda`.

```
#create a virtual env with a specific location, to take load out of root path
conda create --prefix=/opt/envs/ssp/ python=3.7
conda activate /opt/envs/ssp
pip install -r requirements.txt
```

## Juyter Lab
`jupyter-lab # http://localhost:8888/lab`
 