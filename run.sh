conda activate explorer
cd /home/mcfrank/celium/explorer

export PATH_CELIUM="/home/mcfrank/celium"
export PATH_INPUT="/home/mcfrank/posts"
export PATH_DB="data/data.db"

mkdir -p data

python src/load.py

python server.py