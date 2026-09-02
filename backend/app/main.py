import asyncio
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI(
    title="Molecule Screening API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# MOLECULE DATABASE
# =========================================================

MOLECULES = {
    "H2": {
        "name": "Hydrogen",
        "formula": "H₂",
        "atoms": [
            ("H", -0.37),
            ("H", 0.37)
        ],
        "qubits": 4,
        "electrons": 2,
        "reference": -1.1373,
        "binding": -0.1743
    },

    "LiH": {
        "name": "Lithium hydride",
        "formula": "LiH",
        "atoms": [
            ("Li", -0.78),
            ("H", 0.78)
        ],
        "qubits": 6,
        "electrons": 4,
        "reference": -7.8823,
        "binding": -0.1201
    },

    "BeH2": {
        "name": "Beryllium dihydride",
        "formula": "BeH₂",
        "atoms": [
            ("H", -1.31),
            ("Be", 0.0),
            ("H", 1.31)
        ],
        "qubits": 8,
        "electrons": 6,
        "reference": -15.5942,
        "binding": -0.1721
    },

    "N2": {
        "name": "Nitrogen",
        "formula": "N₂",
        "atoms": [
            ("N", -0.55),
            ("N", 0.55)
        ],
        "qubits": 10,
        "electrons": 14,
        "reference": -108.5721,
        "binding": -0.3551
    },

    "CO2": {
        "name": "Carbon dioxide",
        "formula": "CO₂",
        "atoms": [
            ("O", -1.16),
            ("C", 0.0),
            ("O", 1.16)
        ],
        "qubits": 12,
        "electrons": 22,
        "reference": -186.7214,
        "binding": -0.5842
    },

    "H2O": {
        "name": "Water",
        "formula": "H₂O",
        "atoms": [
            ("H", -0.76),
            ("O", 0.0),
            ("H", 0.76)
        ],
        "qubits": 8,
        "electrons": 10,
        "reference": -75.0232,
        "binding": -0.3421
    }
}


# =========================================================
# REQUEST MODEL
# =========================================================

class ScreeningRequest(BaseModel):
    molecules: list[str] = Field(min_length=1)
    max_iterations: int = Field(
        default=72,
        ge=20,
        le=160
    )


# =========================================================
# JOB STATE
# =========================================================

class JobState(BaseModel):
    id: str
    status: Literal["queued", "running", "complete", "failed"]
    progress: int = Field(ge=0, le=100)

    active_molecule: str | None = None
    active_stage: str | None = None

    results: list[dict] = Field(
        default_factory=list
    )


# Resolve all Pydantic annotations before the API starts handling requests.
JobState.model_rebuild()


# =========================================================
# JOB STORAGE
# =========================================================

JOBS: dict[str, JobState] = {}
BACKGROUND_TASKS: set[asyncio.Task] = set()


# =========================================================
# QUANTUM CIRCUIT
# =========================================================

def circuit(qubits: int) -> list[dict]:

    gates = []

    # Hadamard layer
    for q in range(qubits):
        gates.append({
            "gate": "H",
            "q": q,
            "layer": 0
        })

    # Entanglement layer
    for q in range(qubits - 1):
        gates.append({
            "gate": "CX",
            "q": q,
            "target": q + 1,
            "layer": 1
        })

    # Parameterized rotation layer
    for q in range(0, qubits, 2):
        gates.append({
            "gate": "Rᵧ(θ)",
            "q": q,
            "layer": 2
        })

    # Second entanglement layer
    for q in range(qubits - 1):
        gates.append({
            "gate": "CX",
            "q": q,
            "target": q + 1,
            "layer": 3
        })

    return gates


# =========================================================
# DEMO VQE CALCULATION
# =========================================================

def vqe_result(
    key: str,
    iterations: int
) -> dict:

    item = MOLECULES[key]

    rng = random.Random(
        f"{key}-{iterations}"
    )

    initial = (
        item["reference"]
        + 0.7
        + rng.uniform(0.05, 0.2)
    )

    convergence = []

    for i in range(iterations):

        decay = (
            (initial - item["reference"])
            * math.exp(
                -i / (iterations / 5)
            )
        )

        noise = (
            rng.uniform(-0.006, 0.006)
            * math.exp(-i / 18)
        )

        energy = (
            item["reference"]
            + decay
            + noise
        )

        convergence.append({
            "iteration": i + 1,
            "energy": round(
                energy,
                6
            )
        })

    estimated = convergence[-1]["energy"]

    return {
        "molecule": key,
        "name": item["name"],
        "formula": item["formula"],

        "total_energy_hartree": estimated,

        "reference_energy_hartree":
            item["reference"],

        "binding_energy_hartree":
            item["binding"],

        "error_millihartree": round(
            abs(
                estimated
                - item["reference"]
            ) * 1000,
            3
        ),

        "qubits": item["qubits"],
        "electrons": item["electrons"],

        "ansatz": "UCCSD",
        "optimizer": "SPSA",

        "convergence": convergence,

        "circuit": circuit(
            item["qubits"]
        ),

        "atoms": [
            {
                "element": atom,
                "x": position
            }
            for atom, position
            in item["atoms"]
        ]
    }


# =========================================================
# SCREENING JOB
# =========================================================

async def run_job(
    job_id: str,
    request: ScreeningRequest
):

    job = JOBS[job_id]

    try:

        job.status = "running"

        stages = [
            "Building Hamiltonian",
            "Mapping fermions to qubits",
            "Optimizing UCCSD ansatz",
            "Validating energy"
        ]

        total_steps = (
            len(request.molecules)
            * len(stages)
        )

        current_step = 0

        for key in request.molecules:

            # Safety check
            if key not in MOLECULES:
                raise ValueError(
                    f"Unknown molecule: {key}"
                )

            job.active_molecule = key

            for stage in stages:

                job.active_stage = stage

                job.progress = int(
                    (
                        current_step
                        / total_steps
                    ) * 100
                )

                await asyncio.sleep(
                    0.45
                )

                current_step += 1

            result = vqe_result(
                key,
                request.max_iterations
            )

            job.results.append(
                result
            )

            job.progress = int(
                (
                    current_step
                    / total_steps
                ) * 100
            )

        # Rank by binding energy
        job.results.sort(
            key=lambda r:
            r["binding_energy_hartree"]
        )

        for rank, result in enumerate(
            job.results,
            1
        ):
            result["rank"] = rank

        job.progress = 100
        job.status = "complete"
        job.active_stage = "Screening complete"

    except Exception as exc:

        print(
            f"SCREENING ERROR: {exc}"
        )

        job.status = "failed"
        job.active_stage = (
            f"Simulation error: {exc}"
        )


# =========================================================
# MOLECULES API
# =========================================================

@app.get("/api/molecules")
def molecules():

    return [
        {
            "id": key,
            "name": value["name"],
            "formula": value["formula"],
            "qubits": value["qubits"],
            "atoms": [
                {
                    "element": atom,
                    "x": position
                }
                for atom, position
                in value["atoms"]
            ]
        }
        for key, value
        in MOLECULES.items()
    ]


# =========================================================
# CREATE SCREENING
# =========================================================

@app.post(
    "/api/screenings",
    response_model=JobState
)
async def create_screening(
    request: ScreeningRequest
):

    # Validate molecules manually
    invalid = [
        molecule
        for molecule in request.molecules
        if molecule not in MOLECULES
    ]

    if invalid:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown molecule(s): "
                f"{', '.join(invalid)}"
            )
        )

    # Create unique job ID
    job_id = datetime.now(
        timezone.utc
    ).strftime(
        "job-%Y%m%d%H%M%S%f"
    )

    job = JobState(
        id=job_id,
        status="queued",
        progress=0
    )

    JOBS[job_id] = job

    print(
        f"SCREENING STARTED: {job_id}"
    )

    print(
        f"MOLECULES: {request.molecules}"
    )

    # Keep a strong reference so Python 3.13 does not
    # garbage-collect the screening task before it runs.
    task = asyncio.create_task(
        run_job(
            job_id,
            request
        )
    )
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)

    return job


# =========================================================
# SCREENING STATUS
# =========================================================

@app.get(
    "/api/screenings/{job_id}",
    response_model=JobState
)
def screening_status(
    job_id: str
):

    if job_id not in JOBS:

        raise HTTPException(
            status_code=404,
            detail="Screening job not found"
        )

    return JOBS[job_id]


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# FRONTEND BUILD
# =========================================================

DIST_DIR = (
    Path(__file__).resolve()
    .parent.parent.parent
    / "frontend"
    / "dist"
)

if DIST_DIR.exists():

    app.mount(
        "/",
        StaticFiles(
            directory=str(DIST_DIR),
            html=True
        ),
        name="frontend"
    )