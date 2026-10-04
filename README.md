# BusinessOps

BusinessOps is a Streamlit web application for tracking small-business customers, products, orders, invoices, and payments. It includes manual entry forms, CSV/Excel/JSON imports, summary dashboards, reports, backups, and separate local workspaces for multiple businesses.

## Run locally

Requirements: Python 3.10 or newer.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run ui/dashboard.py
```

Open the local URL printed by Streamlit. On Windows PowerShell, use the `.\` prefix when running an executable from the current folder.

## Run tests

```powershell
python -m pytest -q
```

## AI Copilot configuration

The AI Copilot is optional. To enable it locally, set `GROQ_API_KEY` in an ignored `.env` file or in the process environment before starting Streamlit. Never commit `.env` or Streamlit `secrets.toml` files. Without a key, the rest of the application remains available and the Copilot displays a configuration message.

## GitHub and hosted deployment

The app entry point for Streamlit Community Cloud is `ui/dashboard.py`; install dependencies from `requirements.txt`. To deploy, push this project to a GitHub repository, then select that repository and entry point in Streamlit Community Cloud. Add `GROQ_API_KEY` through the hosting provider's secrets settings only if the Copilot is needed.

**Deployment limitation:** this project is currently a local-storage MVP, not a secure multi-user hosted product. Business workspaces are stored as SQLite files on the app's filesystem, hosted filesystems may be temporary, and the app does not provide user authentication or access control. Do not put real client or confidential business data into a public deployment. Before offering it to multiple clients online, add authentication and authorization, per-client data isolation, and persistent hosted database/storage.

Local workspace databases, uploaded files, generated reports, environment files, and backups are excluded from Git.
