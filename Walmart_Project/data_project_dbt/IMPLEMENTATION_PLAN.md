# Walmart Data Engineering Project — Implementation Plan

## Architecture

```
Sources (files / systems)
    -> Databricks ingestion pipelines
    -> bronze / silver / gold tables
    -> dbt transformations, snapshots, and tests
    -> Airflow orchestration
```

Current workflow:

```
Airflow manual trigger
  -> Databricks ingest_walmart Job
  -> wait for Databricks success
  -> clean dbt files
  -> dbt source freshness
  -> silver models and tests
  -> gold models, snapshots, and facts
```

## Build order

### 1. Create the project foundation

Use this structure:

```
data_project_dbt/
├── airflow/
│   ├── dags/
│   ├── walmart_project/
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── requirements.txt
│   └── .env
├── walmart_project/
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

Create the environment:

```powershell
uv venv
.venv\Scripts\activate
uv init
```

Commit `pyproject.toml` and `uv.lock`.

### 2. Prepare source data

For local source data, use a separate setup area such as:

```
data_project_setup/
└── walmart_dataset/
    ├── data/
    └── ddl/
```

For cloud sources, document the S3 bucket, prefix, schema, file format, arrival frequency, and duplicate/late-data behavior. Do not commit private or production data.

### 3. Build Databricks ingestion

In Databricks:

1. Create or identify the catalog and schemas.
2. Create the S3 external location and verify access.
3. Create the ingestion pipeline.
4. Verify the target bronze/silver/gold table.
5. Run the pipeline manually once.
6. Check schema, row counts, checkpoints, and data quality.
7. Add the pipeline to `ingest_walmart_job`, or record its pipeline ID if it will be triggered separately.

Databricks ingestion must work independently before Airflow is added.

### 4. Build dbt

Use this layout:

```
walmart_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── source/
│   ├── silver_t/
│   ├── silver_b/
│   └── gold/
├── snapshots/
├── tests/
├── macros/
└── analyses/
```

Write dbt code in this order:

1. `models/source/sources.yml`.
2. Silver technical models.
3. Silver properties and tests.
4. Silver business models.
5. Gold ephemeral and fact models.
6. Dimension snapshots.
7. Additional tests and analyses.

Validate with:

```powershell
dbt debug
dbt source freshness
dbt run --select silver_t
dbt test --select silver_t
dbt run --select silver_b
dbt test --select silver_b
dbt run --select gold/ephemeral
dbt snapshot
dbt run --select gold/fact
```

Never hardcode a Databricks token in `profiles.yml`:

```yaml
token: "{{ env_var('DATABRICKS_TOKEN') }}"
```

### 5. Build the Airflow DAG

Put the DAG in `airflow/dags/orchestrate.py`.

Write it in this order:

1. Import lightweight Airflow modules at module load time.
2. Import the Databricks SDK inside the task that needs it.
3. Validate `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `DATABRICKS_JOB_ID`.
4. Start the Databricks Job with `jobs.run_now`.
5. Poll the Databricks run until success or failure.
6. Define cleanup and dbt tasks.
7. Define dependencies explicitly.

Main dependency chain:

```
ingest_cdc -> clean_target -> source_freshness -> silver -> gold
```

If the reviews pipeline is separate, add a second Airflow task that starts and monitors it. Run both ingestion tasks in parallel and make dbt wait for both:

```
ingest_cdc ───────────────┐
                          ├── clean_target -> dbt
run_reviews_pipeline ────┘
```

Do not run `orchestrate.py` directly. Airflow imports it and executes its tasks.

### 6. Configure Docker and Airflow

The Airflow image must install every package imported by the DAG:

```text
apache-airflow
databricks-sdk
dbt-core
dbt-databricks
```

Keep the Airflow version in the Dockerfile aligned with the project configuration.

Create `airflow/.env` locally:

```env
DATABRICKS_HOST=your-workspace-host
DATABRICKS_TOKEN=your-token
DATABRICKS_JOB_ID=your-job-id
DATABRICKS_REVIEWS_PIPELINE_ID=your-pipeline-id
```

Never commit this file.

Start Airflow from the `airflow` directory:

```powershell
docker compose up -d --build
```

Use `--build` after changing the Dockerfile or requirements. On later starts:

```powershell
docker compose up -d
docker compose ps
```

The initialization container exiting successfully is normal. The other services should be running or healthy.

## Manual operating procedure

1. Start Docker Desktop.
2. Run `docker compose up -d` from `airflow`.
3. Open `http://localhost:8080`.
4. Confirm the `orchestrate` DAG is enabled.
5. Click **Trigger** once.
6. Monitor `ingest_cdc`.
7. Confirm the Databricks Job succeeds.
8. Confirm all dbt tasks succeed.

Do not manually start Databricks first. Airflow starts the Job and waits for it. Before another run, confirm the previous Airflow and Databricks runs are finished.

## Validation checklist

Run:

```powershell
python -m py_compile airflow\dags\orchestrate.py
docker compose config --quiet
```

Then verify:

- The DAG appears without import errors or timeouts.
- `ingest_cdc` starts the expected Databricks Job.
- Databricks success is required before dbt starts.
- Silver models and tests pass.
- Gold models and snapshots pass.
- The reviews pipeline writes to the intended table.
- No secret appears in code, logs, or Git history.

## GitHub and secrets checklist

The root `.gitignore` should include:

```gitignore
.env
*.env
logs/
**/logs/
target/
**/target/
__pycache__/
*.pyc
.venv/
```

Before committing:

```powershell
git status --short
git grep -n -i "dapi\|token\|password\|secret\|api_key"
```

If a real token was ever committed or shared, revoke it and create a replacement. Removing it from the current file does not remove it from Git history.

## Recommended commit sequence

Commit small logical changes:

```text
chore: initialize uv project and repository structure
feat: add source preparation and schema definitions
feat: add dbt source, silver, and gold models
feat: orchestrate Databricks ingestion and dbt transformations
feat: orchestrate reviews pipeline alongside ingestion
docs: document setup and orchestration workflow
```

The reviews commit is optional. Never commit `.env`, tokens, logs, `target/`, virtual environments, or private source data.

## Reusable template for future projects

1. Define sources and target tables.
2. Create storage and access permissions.
3. Build and test Databricks ingestion.
4. Create dbt sources, silver models, gold models, snapshots, and tests.
5. Validate dbt independently.
6. Create the Databricks Job.
7. Write Airflow to trigger and wait for the Job.
8. Containerize Airflow.
9. Add local environment variables without committing them.
10. Run one complete end-to-end test.
11. Review secrets and generated files.
12. Commit in logical stages and push to GitHub.

Design rule: Databricks owns ingestion execution, dbt owns transformations and tests, and Airflow owns workflow order and dependencies.

