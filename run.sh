conda activate explorer

export CELIUM_PATH="/home/mcfrank/celium"
export PATH_DB="data/data.db"

mkdir -p data

python src/load.py

python server.py