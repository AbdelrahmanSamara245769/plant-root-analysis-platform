# Plant Root Analysis Platform (cv4)

This is a production MLOps system for NPEC, the Netherlands Plant Eco-phenotyping Centre. It takes a grayscale petri dish scan holding five seedlings and finds each plant's main root tip, in pixels and millimetres, with a confidence score.

The system ships as:

- a tested Python package with command-line tools
- an authenticated REST API with a web dashboard
- automated training and retraining in Azure ML
- deployments on premises and in the cloud, with monitoring for drift

It was a group project for a team of five at Breda University of Applied Sciences (Applied Data Science & AI, Year 2), from April to June 2026, for NPEC.

## The problem

Earlier in the year, each team member built a root segmentation pipeline in a notebook. NPEC needed something that researchers can actually use. That means a maintained service with logins, a feedback loop for wrong predictions, versioned data and models, and retraining when performance drifts. Getting there meant turning the best notebook pipeline into production software and running it locally, on a university server and in Azure.

## How it works

```
plate image
  -> crop and pad the petri dish
  -> U-Net on 256 px patches (overlapping, averaged with flipped copies)
  -> clean the mask -> split into 5 lanes -> trace each root along its skeleton to the tip
  -> tip position (px, mm) + confidence score per plant
```

- **Package and CLI (`src/cv4`).** These are the notebook steps refactored into modules: preprocessing, inference, postprocessing, segmentation, localization and the pipeline that chains them. Two command-line tools, `cv4-predict` and `cv4-train`, wrap them.
- **Model.** A Residual Attention U-Net trained with a hybrid of binary cross-entropy and focal Tversky loss.
- **Backend.**
  - **API:** FastAPI with JWT cookie authentication, a `/predict` endpoint, a `/feedback` endpoint for user corrections, and dashboard analytics.
  - **Database:** predictions and feedback are stored in PostgreSQL through SQLAlchemy, with Alembic migrations.
  - **Inference modes:** the U-Net runs inside the API (*local*) or on an Azure ML managed endpoint (*remote*).
- **Frontend.** A Next.js app for uploading images, viewing results and giving feedback, plus a dashboard.
- **Training in Azure ML.** A four-step pipeline: preprocess, train, evaluate, then register the model only if it beats the current one.
  - **Tracking:** experiments are tracked with MLflow.
  - **Data:** image data is registered as versioned data assets.
  - **Automation:** a hyperparameter sweep, a weekly scheduled retraining job, and an Airflow DAG.
- **Deployment.** Docker Compose runs locally. Images are published to GitHub Container Registry and deployed to two places:
  - an on-premise Portainer server
  - Azure Container Apps, with the model behind an Azure ML endpoint that supports blue/green and canary rollouts
- **Monitoring.** OpenTelemetry sends data to Azure Monitor. A daily job runs a Kolmogorov–Smirnov test on each lane's confidence scores against a baseline to detect drift.
- **CI/CD.** GitHub Actions runs lint and tests on every pull request. It also builds the docs, publishes Docker images, deploys, and runs the drift check.

Architecture diagrams:

- [Training pipeline](docs/model_training_pipeline.drawio.png)
- [Deployment pipeline](docs/deployment_pipeline.drawio.png)
- [Data pipeline](docs/data_pipeline.drawio.png)
- [Combined architecture](docs/cv4_combined_architecture.drawio.pdf)

## Results

| What | Result |
|---|---|
| Reference model (selected from the five members' pipelines) | Validation F1 **0.88**; Kaggle rank 5th |
| Registered models (same evaluation set) | Version 2 F1 0.849, then version 3 (sweep winner) **0.855** |
| Endpoint latency, one plate | 5.65 s average (7.39 s first request) |
| Endpoint throughput | **10.6 requests/min** per instance, about 30 at full scale |
| Cloud cost for the block | **€1.45** actual, against a €75 reconstructed estimate |

Training ran on a shared university cluster that isn't billed to the team, which explains most of the cost difference. [docs/cost_analysis.md](docs/cost_analysis.md) breaks it down per service, and [docs/endpoint_performance.md](docs/endpoint_performance.md) covers the endpoint measurements and the rollout strategies.

## My role

In a team of five, my parts were:

- **Scrum master.** I managed the git-flow branching strategy and merged over 30 pull requests.
- **Base pipeline.** My Block B pipeline was selected as the team's base: it had the highest F1 and the best Kaggle rank ([docs/pipeline_selection.md](docs/pipeline_selection.md)). I turned it into a tested Python package, with unit and integration tests.
- **Training code** (`src/cv4/training/`): the model, loss functions, metrics, data loading, training, evaluation, conditional registration and MLflow tracking.
- **Azure ML pipeline.** I built all four components, their environments and the submission scripts. I validated each component on its own before running the pipeline end to end.
- **Hyperparameter sweeps** over learning rate, batch size and augmentation, with automatic evaluation and registration of the best model.
- **Data pipeline.** A standalone pipeline that registers prepared image data as a versioned data asset.
- **CI/CD:**
  - lint and test checks on every pull request, with coverage reporting
  - deployment to Azure Container Apps and to the on-premise Portainer server
  - a canary rollout script
- **Fixes:**
  - a mask normalisation bug that had the model training on blank labels
  - a data streaming bottleneck in the cloud pipeline

My teammates mainly built the API, the frontend and dashboard, the Docker setup, the monitoring and drift jobs, and the Airflow DAG.

## Tech stack

- **ML and image processing:** Python 3.12, uv, TensorFlow/Keras, OpenCV, scikit-image, NetworkX, SciPy
- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend:** Next.js, React, Tailwind
- **Cloud:** Azure ML (pipelines, sweeps, MLflow, managed endpoints), Azure Container Apps, Application Insights, OpenTelemetry
- **Deployment:** Docker Compose, GitHub Container Registry, Portainer, Airflow
- **Tooling:** GitHub Actions, Ruff, pytest, Sphinx

## Repository layout

```
src/cv4/            # package: pipeline modules, API, training, monitoring, deployment scoring script
tests/              # pytest unit and integration tests
scripts/            # Azure ML submission, sweep, registration, endpoint and rollout scripts
components/         # Azure ML component definitions (preprocess, train, evaluate, register)
configs/            # Azure ML environment definitions
dags/               # Airflow DAG for scheduled retraining
alembic/            # database migrations
docker/             # Dockerfiles and Compose files (local and Portainer)
frontend/           # Next.js web app and user guide
docs/               # architecture diagrams, cost analysis, endpoint performance, package plan, dev setup
.github/workflows/  # CI, Docker publish, deploy, docs, drift check
```

## Data and models

The NPEC plate images and masks are not included, and neither is anything made from them: the trained weights (`weights/unet_256px.h5`), the lane boundaries (`lane_edges.npy`), MLflow runs, predictions, and the integration-test plate image. The integration tests are skipped when these files are missing. To regenerate the lane boundaries from your own predictions, run `scripts/generate_lane_edges.py`.

## How to run

```bash
uv sync                                  # Python 3.12
cp .env.example .env                     # database, JWT secret, inference mode, Azure settings
# put the trained model in weights/unet_256px.h5 and lane_edges.npy next to it

uv run cv4-predict --image plate.png --visualize   # run the pipeline on one image
uv run uvicorn cv4.api.app:app --reload  # REST API on http://localhost:8000
uv run pytest                            # tests
```

- **Full stack (API, frontend and database):** run Docker Compose from `docker/`, as described in [docker/docker-compose.yml](docker/docker-compose.yml).
- **Azure ML:** the scripts in `scripts/` need the Azure settings from `.env.example` and access to a workspace.
- **Development setup:** [docs/development.md](docs/development.md).
