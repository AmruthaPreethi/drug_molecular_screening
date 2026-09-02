"""
validate.py
Validates VQE calculated energy against classical reference calculations.
"""

from hamiltonian import MOLECULES

def validate(molecule_name: str, total_energy_hartree: float) -> dict:
    if molecule_name not in MOLECULES:
        raise ValueError(f"Unknown molecule: {molecule_name}")

    ref = MOLECULES[molecule_name]["reference"]
    diff_mHa = abs(total_energy_hartree - ref) * 1000
    passed = diff_mHa < 50.0  # Threshold of 50 mHa

    return {
        "molecule": molecule_name,
        "diff_mHa": round(diff_mHa, 4),
        "passed": passed,
    }
