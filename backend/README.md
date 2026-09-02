# Backend

Run `python -m venv .venv`, activate it, install `pip install -r requirements.txt`, then start `uvicorn app.main:app --reload --port 8000`.

The included engine is a deterministic visual/demo VQE model. For research use, swap `vqe_result` in `app/main.py` for a Qiskit Nature workflow: `PySCFDriver` → `ElectronicStructureProblem` → `ParityMapper` → `HartreeFock` + `UCCSD` → `VQE` (SPSA/L-BFGS-B), and persist job data to a database/queue rather than memory.
