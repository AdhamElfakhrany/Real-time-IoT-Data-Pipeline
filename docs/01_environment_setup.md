# Step 1 – Environment Setup

This document captures the exact actions required to bootstrap the development environment for the Real-time IoT Data Pipeline project.

## 1. Repository Bootstrapping
- Ensure the project folder contains the directory structure referenced in `README.md`.
- Initialize git: `git init && git add . && git commit -m "chore: bootstrap repo"` (optional but recommended).

## 2. Python Toolchain
1. Install Python 3.10+.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Upgrade pip and install base dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 3. Environment Variables
1. Copy the template: `cp .env.example .env`.
2. Update the `.env` values to match your local Kafka broker, storage paths, and alert endpoints.
3. Load env vars automatically by sourcing them in your shell or letting each service load them via `python-dotenv`.

## 4. Local Infrastructure (Optional for Step 1)
- Install Docker Desktop (or Colima/Rancher Desktop on Linux/macOS).
- Verify that ports `9092` (Kafka), `2181` (Zookeeper), and `3000`/`8501` (dashboards) are free.
- Upcoming steps will introduce a docker-compose stack in `infra/compose.yml`.

## 5. Tooling Checklist
- [ ] Git configured with user name/email.
- [ ] Python virtualenv created and activated.
- [ ] Dependencies installed.
- [ ] `.env` populated.
- [ ] Docker Desktop running (if you intend to use containers).

Once these items are complete, proceed to **Milestone 1 – Data Simulation & Ingestion**.
