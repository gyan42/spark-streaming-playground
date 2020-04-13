# Linux Machine Setup

Essential pacakages:
 
```
sudo apt-get update
sudo apt-get install libsnappy-dev
sudo apt-get install -y wget axel vim rsync net-tools
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y ssh supervisor openssh-server
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:openjdk-r/ppa
sudo apt-get install -y openjdk-8-jdk
sudo apt-get install -y zookeeperd
sudo apt-get install -y build-essential
sudo apt-get install -y python3-pip zip
sudo apt-get install -y libpq-dev
sudo apt-get install -y iputils-ping
sudo apt-get install -y iproute2
sudo apt-get install -y curl
sudo apt-get install -y libsnappy-dev
sudo apt-get install -y unzip
sudo apt-get install -y p7zip-full
```

Run the following 3 lines, and you should be able to see the tqdm progress bars in Jupyer notebooks:

```
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

Download [Draw.io](https://github.com/jgraph/drawio-desktop/releases) desktop version for diagrams!
