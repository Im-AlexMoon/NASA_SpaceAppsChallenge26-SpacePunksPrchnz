# Requires GNU make (Git Bash / WSL / choco install make). Every target maps 1:1
# to a `flamesafe` CLI command, so you can run those directly on Windows too.
.PHONY: setup lint test catalog bronze silver gold pipeline eda train rag-index app clean

setup:        ## Install package with all extras in editable mode
	pip install -e ".[all]"

lint:         ## Ruff lint + format check
	ruff check src tests app && ruff format --check src tests app

test:         ## Unit tests (no network)
	pytest -m "not integration"

catalog:      ## F1: fetch PSI combustion catalog -> data/bronze/catalog
	flamesafe catalog

bronze:       ## F2: download selected files (manifest-driven) -> data/bronze
	flamesafe bronze

silver:       ## F2: parse/clean/standardize -> data/silver
	flamesafe silver

gold:         ## F2: analysis-ready tables -> data/gold
	flamesafe gold

pipeline: catalog bronze silver gold  ## Full medallion run

train:        ## F4: train + evaluate models -> artifacts/models
	flamesafe train

rag-index:    ## F5: build RAG index -> artifacts/rag
	flamesafe rag-index

app:          ## F6: run dashboard locally
	streamlit run app/Home.py

clean:
	rm -rf data/silver/* data/gold/* artifacts/* && git checkout -- data artifacts 2>/dev/null || true
