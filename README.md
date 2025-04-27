# bh-reggie-llamaindex

Example
```
import requests

CLOUD_RUN_URL = "https://your-cloud-run-url/ingest"
payload = {
    "gcs_path": "global/library/file.pdf",
    "vector_table": "kb_customer_123"
}

res = requests.post(CLOUD_RUN_URL, json=payload)
print(res.json())
```

Full rebuild
```
requests.post("https://your-cloud-run-url/ingest-all", json={
    "gcs_path": "global/library/",
    "vector_table": "kb_customer_123"
})
```

https://docs.llamaindex.ai/en/stable/community/integrations/vector_stores/

## Running and Testing
```
uvicorn main:app --reload --port 8080
```
```
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "gcs_path": "test/file.pdf",
    "knowledgebase_id": "your-kb-id"
  }'
```
or from python
```
import requests

res = requests.post("http://localhost:8080/ingest", json={
    "gcs_path": "test/file.pdf",
    "knowledgebase_id": "your-kb-id"
})
print(res.json())
```

https://github.com/googleapis/llama-index-cloud-sql-pg-python/blob/main/samples/llama_index_vector_store.ipynb

## Setup instructions
```
python3.12 -m venv llama_env
source llama_env/bin/activate
pip install -r dev-requirements.txt
```