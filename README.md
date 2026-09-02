# Aurora Quantum Screening

This project is a visually engaging VQE screening dashboard for an early-stage pharma R&D workflow. It screens H2, LiH, BeH2, N2, CO2, and H2O as benchmark molecular systems, tracks energy convergence, displays an illustrative UCCSD circuit, highlights the molecule currently being processed, and ranks candidates by binding energy.

## Start it

Open two terminals:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Then open the URL Vite prints (normally `http://localhost:5173`).

## How to turn this into real VQE research

1. Install Qiskit Nature and PySCF in the backend environment.
2. Replace the deterministic function `vqe_result` with the `PySCFDriver → ElectronicStructureProblem → ParityMapper → HartreeFock + UCCSD → VQE` pipeline described in `backend/README.md`.
3. Save calculation metadata (basis set, geometry, optimizer seeds, shots, backend, package versions) alongside each run; do not treat a single variational energy as a synthesis decision.
4. Use a durable task queue (Celery/RQ) and database for real jobs. VQE workloads should not run inside a web server process.
5. Validate against FCI/CASCI for small benchmarks and use classical DFT/CC methods plus ADMET and synthetic-accessibility screening for actual drug-like molecules.

The three included molecules are educational VQE benchmarks, not drug candidates. Ground-state energy is only one early filter and cannot establish pharmacological safety or efficacy.
