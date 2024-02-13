cd /home/mcfrank/celium/explorer

export PATH_CELIUM="/home/mcfrank/celium"
export PATH_INPUT="/home/mcfrank/celium/ghlisten/data/issues.db"
export PATH_DB="data/graph.db"

mkdir -p data

python src/load_issues.py

python server.py
