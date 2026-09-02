"""
hamiltonian.py
Defines candidate molecules and benchmark parameters for VQE quantum simulation.
"""

MOLECULES = {
    "H2": {
        "name": "Hydrogen",
        "formula": "H₂",
        "atoms": [("H", -0.37), ("H", 0.37)],
        "qubits": 4,
        "electrons": 2,
        "reference": -1.1373,
        "binding": -0.1743,
    },
    "LiH": {
        "name": "Lithium hydride",
        "formula": "LiH",
        "atoms": [("Li", -0.78), ("H", 0.78)],
        "qubits": 6,
        "electrons": 4,
        "reference": -7.8823,
        "binding": -0.1201,
    },
    "BeH2": {
        "name": "Beryllium dihydride",
        "formula": "BeH₂",
        "atoms": [("H", -1.31), ("Be", 0.0), ("H", 1.31)],
        "qubits": 8,
        "electrons": 6,
        "reference": -15.5942,
        "binding": -0.1721,
    },
    "N2": {
        "name": "Nitrogen",
        "formula": "N₂",
        "atoms": [("N", -0.55), ("N", 0.55)],
        "qubits": 10,
        "electrons": 14,
        "reference": -108.5721,
        "binding": -0.3551,
    },
    "CO2": {
        "name": "Carbon dioxide",
        "formula": "CO₂",
        "atoms": [("O", -1.16), ("C", 0.0), ("O", 1.16)],
        "qubits": 12,
        "electrons": 22,
        "reference": -186.7214,
        "binding": -0.5842,
    },
    "H2O": {
        "name": "Water",
        "formula": "H₂O",
        "atoms": [("H", -0.76), ("O", 0.0), ("H", 0.76)],
        "qubits": 8,
        "electrons": 10,
        "reference": -75.0232,
        "binding": -0.3421,
    },
}
