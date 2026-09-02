"""
app.py
Streamlit frontend for the VQE drug-molecule screening pipeline.
Run with: streamlit run app.py

This is a thin UI layer -- it calls the exact same hamiltonian.py /
vqe_runner.py / validate.py / rank.py modules used in the CLI pipeline.
No science logic lives here, only display logic.
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from hamiltonian import MOLECULES
from vqe_runner import run_vqe
from validate import validate
from rank import rank_molecules

st.set_page_config(page_title="VQE Drug Molecule Screening", layout="wide")

st.title("VQE-Based Molecular Stability Screening")
st.caption(
    "Estimates ground-state energies of candidate small molecules using "
    "VQE with a UCCSD ansatz, validates against a classical reference "
    "(CASCI/FCI), and ranks molecules by binding energy."
)

selected = st.multiselect(
    "Molecules to screen",
    options=list(MOLECULES.keys()),
    default=list(MOLECULES.keys()),
)

run_button = st.button("Run VQE Screening", type="primary")

if run_button:
    if not selected:
        st.warning("Select at least one molecule.")
        st.stop()

    all_results = []
    validations = []
    progress = st.progress(0.0, text="Starting...")

    for i, mol in enumerate(selected):
        progress.progress((i) / len(selected), text=f"Running VQE for {mol}...")
        res = run_vqe(mol)
        check = validate(mol, res["total_energy_hartree"])
        all_results.append(res)
        validations.append(check)
    progress.progress(1.0, text="Done")

    ranked = rank_molecules(all_results)
    val_by_mol = {v["molecule"]: v for v in validations}

    # --- Ranking table ---
    st.subheader("Ranking (most stable first, by binding energy)")
    table_rows = []
    for i, r in enumerate(ranked, 1):
        v = val_by_mol[r["molecule"]]
        table_rows.append({
            "Rank": i,
            "Molecule": r["molecule"],
            "Qubits": r["num_qubits"],
            "Total Energy (Ha)": round(r["total_energy_hartree"], 6),
            "Binding Energy (Ha)": round(r["binding_energy_hartree"], 6),
            "Validated": "✅" if v["passed"] else "❌",
            "Diff vs classical (mHa)": round(v["diff_mHa"], 4),
        })
    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download ranking as CSV",
        df.to_csv(index=False).encode("utf-8"),
        "ranking_report.csv",
        "text/csv",
    )

    # --- Convergence plots ---
    st.subheader("VQE Convergence")
    cols = st.columns(len(all_results))
    for col, res in zip(cols, all_results):
        with col:
            fig, ax = plt.subplots(figsize=(4, 3))
            conv = res["convergence"]
            ax.plot(conv["iters"], conv["energies"], marker="o", markersize=2)
            ax.set_title(res["molecule"])
            ax.set_xlabel("Evaluation count")
            ax.set_ylabel("Energy (Ha)")
            ax.grid(alpha=0.3)
            st.pyplot(fig)

    st.caption(
        "Convergence plots show the raw electronic energy from the optimizer "
        "callback (before nuclear repulsion is added), so values won't match "
        "the total energy column directly -- the flat tail is what confirms "
        "convergence."
    )
else:
    st.info("Select molecules and click **Run VQE Screening** to start.")
