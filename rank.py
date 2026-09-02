"""
rank.py
Ranks candidates by ground state / binding energy.
"""

def rank_molecules(results: list[dict]) -> list[dict]:
    return sorted(results, key=lambda r: r["binding_energy_hartree"])
