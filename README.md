# RAG

RAG contains a standalone Ollama chat example on `main`. An earlier project snapshot contains a FastAPI service for extracting web-page text and retrieving Hugging Face model metadata, plus a Streamlit dashboard for model likes and downloads.

## Repository structure

| Checkout | Path | Purpose |
| --- | --- | --- |
| `main` | `Documents/ontology llm project/onto_llm_realtime_plus/run_llm_example.py` | Calls `LLM(model="llama2").chat(...)` and prints the response. |
| September snapshot | `scraper/api.py`, `scraper/scraper.py` | FastAPI routes, HTML extraction, and Hugging Face model discovery and enrichment. |
| September snapshot | `start_api.py`, `scraper/requirements.txt` | Development server launcher and backend dependencies. |
| September snapshot | `streamlit_app/app.py`, `scraped_models.txt` | Model dashboard and local list of model IDs. |
| September snapshot | `recovery_app/` | Separate Streamlit app with its own requirements and dataset builder. |
| September snapshot | `LICENSE` | MIT license added by [PR #3](https://github.com/BigPap20/RAG/pull/3). |

The commands below use commit [`bec5092`](https://github.com/BigPap20/RAG/tree/bec50927d828918889af38a42b92b7805f381070) for the backend and dashboard and commit [`55a16e1`](https://github.com/BigPap20/RAG/commit/55a16e144623c56f9757dcb69f35d5fbb00981e1) for the Ollama example.

## Set up the FastAPI backend

Run these commands from a shell with Git and Python. The September snapshot's `.python-version` specifies Python 3.10.13. Use a fresh virtual environment for the component dependencies.

```bash
git clone https://github.com/BigPap20/RAG.git
cd RAG
git fetch origin bec50927d828918889af38a42b92b7805f381070
git worktree add --detach ../RAG-september bec50927d828918889af38a42b92b7805f381070
cd ../RAG-september
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scraper/requirements.txt
python -m uvicorn scraper.api:app --host 127.0.0.1 --port 8000
```

The snapshot also includes `python start_api.py`, which starts Uvicorn with auto-reload on port 8000 and binds to all interfaces. For local development, use the loopback command above. The scraper accepts a caller-supplied URL and the API has no authentication.

## FastAPI endpoints

Open [Swagger UI](http://127.0.0.1:8000/docs) or [ReDoc](http://127.0.0.1:8000/redoc) while the server is running. The OpenAPI schema is at `/openapi.json`.

| Method and path | Query parameters | Response |
| --- | --- | --- |
| `GET /` | None | Service name, version, and route summary. |
| `GET /health` | None | Service status. This route performs no upstream connectivity check. |
| `GET /scrape` | Required `url`. Optional `format`, default `json`. | JSON object with `url`, `title`, `text`, `status`, and `error`. With `format=text`, FastAPI serializes the extracted text as a JSON string. |
| `GET /models` | `limit` defaults to 20 and accepts 1–100. `enrich` defaults to `true`. | `models` with metadata or `model_ids` with `enrich=false`, plus `count`. |
| `GET /context` | Optional `topic`. `limit` defaults to 20 and accepts 1–100. | Enriched models, aggregate likes and downloads, pipeline tags, and the top models by likes. The topic filter matches model IDs, tags, and pipeline tags after retrieval and enrichment. |

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsSG http://127.0.0.1:8000/scrape --data-urlencode 'url=https://example.com/'
curl -fsS 'http://127.0.0.1:8000/models?limit=5&enrich=false'
curl -fsS 'http://127.0.0.1:8000/context?topic=text-generation&limit=10'
```

## Run the Streamlit dashboard

In a second terminal, start in the September worktree root and activate its virtual environment.

```bash
source .venv/bin/activate
python -m pip install 'streamlit==1.48.1' 'pandas==2.3.1' requests
cd streamlit_app
python -m streamlit run app.py --server.address 127.0.0.1
```

Open [the dashboard](http://127.0.0.1:8501). The app reads `../scraped_models.txt` relative to its working directory, then queries Hugging Face directly and displays a table and charts for likes and downloads. With no local file it uses three built-in model IDs. The dashboard refreshes every 60 seconds and runs independently of FastAPI.

## Ollama example

From the original `RAG` checkout, inspect the script in `Documents/ontology llm project/onto_llm_realtime_plus/`. The example hardcodes `llama2` and the placeholder prompt `Your question here`. It imports `LLM` from `app.llm`, which is absent from `main`. The wrapper's client dependencies, connection settings, and behavior need to be confirmed with its source.

With Ollama running locally, you can check the example's model separately.

```bash
ollama pull llama2
ollama run llama2 "What is retrieval-augmented generation?"
```

Once the intended `app.llm` implementation is available on the Python import path and its dependencies are installed, try the repository example from the original checkout.

```bash
cd "Documents/ontology llm project/onto_llm_realtime_plus"
python run_llm_example.py
```

The September backend and dashboard contain no call to the Ollama example.

## Configuration and limitations

| Setting | Where to configure it |
| --- | --- |
| Backend host and port | Set Uvicorn's `--host` and `--port` options. The included launcher sets `0.0.0.0:8000` directly. |
| Scraper network behavior | `scraper/scraper.py` sets Hugging Face URLs and a user agent in code. The scraper classes default to a 20-second request timeout and three attempts for listing or page scraping. |
| Dashboard input and refresh | Edit `DATA_FILE`, `DEFAULT_IDS`, or `SCRAPE_INTERVAL` in `streamlit_app/app.py`. |
| Ollama model and prompt | Edit the model and prompt literals in `run_llm_example.py`. The script defines no environment-variable configuration. |

- Live data depends on outbound access and Hugging Face availability. The backend falls back to the Hub API when HTML model discovery yields no IDs. Enrichment skips failed lookups and can return fewer results than requested.
- Page scraping extracts text from returned HTML. Pages that render content in JavaScript may yield incomplete results. Scrape failures currently surface as HTTP 500 because the route's broad exception handler catches its own HTTP 400.
- Backend requests perform synchronous network work, model enrichment runs sequentially, and the declared model cache is unused. The dashboard polls the upstream API and has no explicit request timeout.
- The root requirements file in the snapshot includes Conda packages. The setup uses the backend requirements and the dashboard's direct dependencies.

## Verify before publishing

- Confirm which branch or commit should be the supported application checkout and whether the backend, dashboard, and license should be restored to `main`.
- Test installation from clean environments on the intended Python versions and platforms. Smoke-test the API routes, upstream retrieval, and the dashboard refresh with real data.
- Identify the intended `app.llm.LLM` source and verify the Ollama client dependencies, host, model tag, and script output before presenting the Python example as runnable.

## License

[PR #3](https://github.com/BigPap20/RAG/pull/3) merged on September 3, 2025 and added the [MIT license](https://github.com/BigPap20/RAG/blob/bec50927d828918889af38a42b92b7805f381070/LICENSE), copyright 2025 BigPap20. The current `main` tree has no root `LICENSE` file.
