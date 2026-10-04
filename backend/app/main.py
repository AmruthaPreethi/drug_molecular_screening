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
    },

    "Benzene": {
        "name": "Benzene",
        "formula": "C₆H₆",
        "atoms": [
            ("C", -1.45), ("C", -0.70), ("C", 0.70),
            ("C", 1.45), ("C", 0.70), ("C", -0.70),
            ("H", -2.50), ("H", -1.30), ("H", 1.30),
            ("H", 2.50), ("H", 1.30), ("H", -1.30)
        ],
        "qubits": 12,
        "electrons": 42,
        "reference": -230.3995,
        "binding": -2.4070
    },

    "Aspirin": {
        "name": "Acetylsalicylic acid",
        "formula": "C₉H₈O₄",
        "atoms": [
            ("C", -2.8), ("C", -1.4), ("C", 2.8), ("C", 1.4),
            ("O", -3.6), ("O", 1.4), ("O", 3.6), ("O", -0.2),
            ("C", -0.2), ("C", 1.8), ("C", 0.4), ("C", -1.6),
            ("H", -3.2), ("H", 3.2), ("H", 0.6), ("H", -2.4),
            ("H", 1.6), ("H", -1.2), ("H", 0.2)
        ],
        "qubits": 12,
        "electrons": 84,
        "reference": -683.2457,
        "binding": -3.9840
    },

    "Paracetamol": {
        "name": "Acetaminophen",
        "formula": "C₈H₉NO₂",
        "atoms": [
            ("C", -2.2), ("C", -1.0), ("C", 1.0), ("C", 2.2),
            ("N", 0.0), ("O", 3.2), ("O", -3.2), ("C", 0.0),
            ("H", -1.6), ("H", 1.6), ("H", -3.0), ("H", 3.0),
            ("H", -2.8), ("H", 0.8), ("H", -0.8), ("C", 1.4),
            ("H", 2.0)
        ],
        "qubits": 12,
        "electrons": 76,
        "reference": -592.1437,
        "binding": -3.4120
    },

    "Caffeine": {
        "name": "Caffeine",
        "formula": "C₈H₁₀N₄O₂",
        "atoms": [
            ("C", -2.4), ("C", -1.0), ("C", 1.0), ("C", 2.4),
            ("N", -1.8), ("N", 0.0), ("N", 1.8), ("N", 0.8),
            ("O", -3.6), ("O", 3.6), ("C", 0.0), ("C", 2.0),
            ("C", -0.8), ("C", 1.2), ("H", 0.4), ("H", -2.6),
            ("H", 1.6), ("H", -1.2), ("H", 2.8), ("H", -0.2),
            ("H", 1.8), ("H", -3.2)
        ],
        "qubits": 12,
        "electrons": 102,
        "reference": -711.2366,
        "binding": -4.2280
    },

    "Ibuprofen": {
        "name": "Ibuprofen",
        "formula": "C₁₃H₁₈O₂",
        "atoms": [
            ("C", -3.0), ("C", -1.8), ("C", -0.6), ("C", 0.6),
            ("C", 1.8), ("C", 3.0), ("C", 4.2), ("C", -2.4),
            ("C", -4.2), ("O", 3.6), ("O", 4.8), ("C", 2.4),
            ("C", 1.2), ("H", -1.2), ("H", -3.6), ("H", -4.8),
            ("H", 2.4), ("H", 3.4), ("H", 4.6), ("H", 5.2),
            ("H", 0.6), ("H", 2.0), ("H", 0.2), ("H", -2.0),
            ("H", -1.4), ("H", -3.0), ("H", 1.0), ("H", 3.0)
        ],
        "qubits": 12,
        "electrons": 132,
        "reference": -573.0245,
        "binding": -3.8870
    },

    "Amoxicillin": {
        "name": "Amoxicillin",
        "formula": "C₁₆H₁₉N₃O₅S",
        "atoms": [
            ("C", -3.4), ("C", -2.0), ("C", 2.0), ("C", 3.4),
            ("N", 0.0), ("N", 1.0), ("N", -1.4), ("O", 3.8),
            ("O", -3.8), ("S", 2.6), ("O", 0.4), ("O", -0.8),
            ("C", 1.8), ("C", 0.6), ("C", -1.8), ("C", -0.4),
            ("C", 2.4), ("C", 4.0), ("H", 1.2), ("H", -2.6),
            ("H", 3.2), ("H", -1.2), ("H", 4.6), ("H", 2.0),
            ("H", 0.0), ("H", -0.2), ("H", 1.6)
        ],
        "qubits": 12,
        "electrons": 158,
        "reference": -1246.8452,
        "binding": -5.4760
    },

    "Metformin": {
        "name": "Metformin",
        "formula": "C₄H₁₁N₅",
        "atoms": [
            ("C", -2.0), ("C", 0.0), ("C", 2.0), ("C", 1.0),
            ("N", -1.0), ("N", 0.0), ("N", 2.0), ("N", 3.0),
            ("N", -2.4), ("H", -3.0), ("H", 1.2), ("H", 0.4),
            ("H", -1.6), ("H", 2.4), ("H", 2.0), ("H", -0.6),
            ("H", 1.8), ("H", 3.6), ("H", -1.0)
        ],
        "qubits": 12,
        "electrons": 68,
        "reference": -415.1234,
        "binding": -3.1180
    },

    "Amiodarone": {
        "name": "Amiodarone",
        "formula": "C₂₅H₂₉I₂NO₃",
        "atoms": [
            ("C", -4.0), ("C", -2.8), ("C", -1.6), ("C", 1.6),
            ("C", 2.8), ("C", 4.0), ("N", 3.4), ("O", 0.0),
            ("I", 4.4), ("I", -4.4), ("O", -0.8), ("O", 1.2),
            ("C", 0.4), ("C", 2.2), ("C", 3.0), ("C", -3.0),
            ("C", -1.0), ("C", 2.0), ("C", 3.8), ("C", -2.2),
            ("C", -3.6), ("C", 1.0), ("C", -4.4), ("H", 1.6),
            ("H", -1.2), ("H", 2.6), ("H", -2.8), ("H", 4.0),
            ("H", 0.6), ("H", -3.8)
        ],
        "qubits": 12,
        "electrons": 214,
        "reference": -1714.5634,
        "binding": -6.8420
    },

    "Atorvastatin": {
        "name": "Atorvastatin",
        "formula": "C₃₃H₃₅FN₂O₅",
        "atoms": [
            ("C", -4.4), ("C", -3.2), ("C", -2.0), ("C", 2.0),
            ("C", 3.2), ("C", 4.4), ("F", 5.0), ("N", 2.6),
            ("N", -2.6), ("O", 0.0), ("O", 1.4), ("O", -1.4),
            ("O", 3.8), ("O", -3.8), ("C", 0.8), ("C", 1.6),
            ("C", -0.8), ("C", -1.6), ("C", 4.0), ("C", 2.2),
            ("C", -4.0), ("C", -2.2), ("C", 3.0), ("C", 1.2),
            ("C", -3.0), ("C", -1.2), ("C", 4.6), ("H", 2.4),
            ("H", -2.4), ("H", 4.2), ("H", -4.2), ("H", 3.4),
            ("H", -3.4), ("H", 1.8), ("H", -1.8)
        ],
        "qubits": 12,
        "electrons": 278,
        "reference": -2240.3356,
        "binding": -7.5120
    },

    "Salbutamol": {
        "name": "Albuterol",
        "formula": "C₁₃H₂₁NO₃",
        "atoms": [
            ("C", -3.0), ("C", -1.8), ("C", -0.6), ("C", 0.8),
            ("C", 2.0), ("C", 3.2), ("N", -1.2), ("O", 3.8),
            ("O", 0.0), ("O", -3.6), ("C", 1.4), ("C", 0.4),
            ("C", -2.4), ("C", 2.4), ("H", 1.0), ("H", -2.2),
            ("H", 3.4), ("H", -3.4), ("H", -1.0), ("H", 2.0),
            ("H", 1.6), ("H", 0.2), ("H", -1.8), ("H", 2.8)
        ],
        "qubits": 12,
        "electrons": 102,
        "reference": -610.8761,
        "binding": -3.7540
    },

    "Omeprazole": {
        "name": "Omeprazole",
        "formula": "C₁₇H₁₉N₃O₃S",
        "atoms": [
            ("C", -3.4), ("C", -2.2), ("C", 2.2), ("C", 3.4),
            ("N", 1.0), ("N", 0.0), ("N", -1.2), ("S", 2.0),
            ("O", -3.8), ("O", 3.8), ("O", 0.4), ("C", 0.8),
            ("C", -0.8), ("C", 2.0), ("C", -2.0), ("C", 3.0),
            ("C", 1.4), ("C", -1.4), ("C", 2.6), ("C", -2.6),
            ("C", 3.8), ("C", -3.4), ("H", 1.0), ("H", -1.0),
            ("H", 3.4), ("H", -3.6), ("H", 2.2), ("H", -2.2)
        ],
        "qubits": 12,
        "electrons": 158,
        "reference": -1256.3458,
        "binding": -5.5430
    },

    "Metoprolol": {
        "name": "Metoprolol",
        "formula": "C₁₅H₂₅NO₃",
        "atoms": [
            ("C", -3.2), ("C", -2.0), ("C", 2.0), ("C", 3.2),
            ("N", -1.2), ("O", 3.6), ("O", 0.2), ("O", -3.0),
            ("C", 0.6), ("C", -0.6), ("C", 1.4), ("C", 2.2),
            ("C", -2.4), ("C", 3.0), ("C", -3.4), ("C", 1.0),
            ("C", 4.0), ("H", 1.8), ("H", -2.8), ("H", 3.6),
            ("H", -3.8), ("H", 0.4), ("H", -1.0), ("H", 4.4),
            ("H", 1.2), ("H", -1.4), ("H", 3.2)
        ],
        "qubits": 12,
        "electrons": 128,
        "reference": -690.4567,
        "binding": -4.0230
    },

    "Lisinopril": {
        "name": "Lisinopril",
        "formula": "C₂₁H₃₁N₃O₅",
        "atoms": [
            ("C", -4.2), ("C", -3.0), ("C", -1.8), ("C", 1.8),
            ("C", 3.0), ("C", 4.2), ("N", 0.0), ("N", 1.0),
            ("N", -1.0), ("O", 3.6), ("O", 4.8), ("O", -3.6),
            ("O", -4.8), ("O", 0.6), ("C", 0.8), ("C", -0.8),
            ("C", 2.4), ("C", 1.4), ("C", -2.4), ("C", -1.4),
            ("C", 3.4), ("C", 2.0), ("C", -3.4), ("C", -2.0),
            ("C", 4.4), ("H", 1.6), ("H", -1.6), ("H", 3.0),
            ("H", -3.0), ("H", 2.2), ("H", -2.2), ("H", 4.0)
        ],
        "qubits": 12,
        "electrons": 194,
        "reference": -1412.6671,
        "binding": -6.1150
    },

    "Furosemide": {
        "name": "Furosemide",
        "formula": "C₁₂H₁₁ClN₂O₅S",
        "atoms": [
            ("C", -3.0), ("C", -1.8), ("C", 1.8), ("C", 3.0),
            ("Cl", 3.8), ("N", 0.0), ("N", -1.0), ("O", -3.4),
            ("O", 3.4), ("O", 0.4), ("O", -0.6), ("S", 2.4),
            ("C", 0.6), ("C", -0.6), ("C", 1.4), ("C", -1.4),
            ("C", 2.0), ("C", -2.2), ("C", 3.2), ("H", 1.0),
            ("H", -2.6), ("H", 3.6), ("H", -1.0), ("H", 1.8),
            ("H", 0.2), ("H", 2.6), ("H", -3.8)
        ],
        "qubits": 12,
        "electrons": 128,
        "reference": -1138.9023,
        "binding": -5.2120
    },

    "Warfarin": {
        "name": "Warfarin",
        "formula": "C₁₉H₁₆O₄",
        "atoms": [
            ("C", -3.6), ("C", -2.4), ("C", 2.4), ("C", 3.6),
            ("O", 0.0), ("O", 1.2), ("O", -1.2), ("O", 3.4),
            ("C", 0.6), ("C", -0.6), ("C", 1.8), ("C", -1.8),
            ("C", 3.0), ("C", 2.0), ("C", -3.0), ("C", -2.0),
            ("C", 0.4), ("C", 2.8), ("C", -2.8), ("C", -0.4),
            ("C", 3.8), ("C", -3.8), ("H", 1.6), ("H", -1.6),
            ("H", 3.2), ("H", -3.2), ("H", 2.4), ("H", -2.4),
            ("H", 4.0), ("H", -4.0)
        ],
        "qubits": 12,
        "electrons": 128,
        "reference": -1025.3451,
        "binding": -5.0120
    },

    "Levothyroxine": {
        "name": "Levothyroxine",
        "formula": "C₁₅H₁₁I₄NO₄",
        "atoms": [
            ("C", -3.4), ("C", -2.2), ("C", 2.2), ("C", 3.4),
            ("N", 0.0), ("O", 3.8), ("O", -3.8), ("O", 0.4),
            ("I", 4.2), ("I", -4.2), ("I", 2.8), ("I", -2.8),
            ("O", 1.2), ("C", 0.8), ("C", 1.6), ("C", -1.6),
            ("C", 3.0), ("C", -3.0), ("C", 2.4), ("C", -2.4),
            ("C", 4.0), ("H", 1.0), ("H", 1.8), ("H", 3.2),
            ("H", -3.2), ("H", 4.4)
        ],
        "qubits": 12,
        "electrons": 132,
        "reference": -1522.3345,
        "binding": -6.4230
    },

    "Hydrochlorothiazide": {
        "name": "Hydrochlorothiazide",
        "formula": "C₇H₈ClN₃O₄S₂",
        "atoms": [
            ("C", -2.4), ("C", -1.2), ("C", 1.2), ("C", 2.4),
            ("Cl", 3.4), ("N", 0.0), ("N", 1.4), ("N", -1.4),
            ("O", -3.0), ("O", 3.0), ("S", 1.0), ("S", -1.0),
            ("O", 0.6), ("O", -0.6), ("C", 0.4), ("C", 2.0),
            ("C", -2.0), ("H", 1.8), ("H", -1.8), ("H", 2.6),
            ("H", -2.6), ("H", 0.8), ("H", -0.8)
        ],
        "qubits": 12,
        "electrons": 118,
        "reference": -1334.2211,
        "binding": -5.6340
    },

    "Isoniazid": {
        "name": "Isoniazid",
        "formula": "C₆H₇N₃O",
        "atoms": [
            ("C", -2.0), ("C", -1.0), ("C", 1.0), ("C", 2.0),
            ("N", 0.0), ("N", 2.6), ("O", -3.0), ("C", 0.0),
            ("H", -2.6), ("H", -1.4), ("H", 1.4), ("H", 2.6),
            ("H", 0.4), ("H", 3.2), ("H", -0.6), ("H", 1.8)
        ],
        "qubits": 12,
        "electrons": 54,
        "reference": -411.5672,
        "binding": -3.0450
    },

    "Ampicillin": {
        "name": "Ampicillin",
        "formula": "C₁₆H₁₉N₃O₄S",
        "atoms": [
            ("C", -3.4), ("C", -2.0), ("C", 2.0), ("C", 3.4),
            ("N", 0.0), ("N", 1.0), ("N", -1.4), ("O", 3.4),
            ("O", -3.4), ("S", 2.6), ("O", 0.4), ("O", -0.6),
            ("C", 1.8), ("C", 0.6), ("C", -1.8), ("C", -0.4),
            ("C", 2.4), ("C", 4.0), ("C", -4.0), ("H", 1.2),
            ("H", -2.6), ("H", 3.2), ("H", -1.2), ("H", 4.4),
            ("H", 2.0), ("H", 0.0), ("H", -1.6)
        ],
        "qubits": 12,
        "electrons": 158,
        "reference": -1123.4456,
        "binding": -5.3450
    },

    "Gentamicin": {
        "name": "Gentamicin",
        "formula": "C₂₁H₄₃N₅O₇",
        "atoms": [
            ("C", -4.0), ("C", -3.0), ("C", -2.0), ("C", -1.0),
            ("C", 1.0), ("C", 2.0), ("C", 3.0), ("C", 4.0),
            ("N", -1.4), ("N", 1.4), ("N", 3.4), ("N", -3.4),
            ("N", 0.0), ("O", 0.8), ("O", -0.8), ("O", 2.2),
            ("O", -2.2), ("O", 1.6), ("O", 4.2), ("C", 0.4),
            ("C", 2.6), ("C", -2.6), ("C", 1.2), ("C", -1.2),
            ("C", 3.6), ("C", -3.6), ("H", 1.8), ("H", -1.8),
            ("H", 3.0), ("H", -3.0), ("H", 2.0), ("H", -2.0),
            ("H", 4.6), ("H", 2.8), ("H", -4.4)
        ],
        "qubits": 12,
        "electrons": 194,
        "reference": -1856.2234,
        "binding": -6.9840
    },

    "Propanolol": {
        "name": "Propranolol",
        "formula": "C₁₆H₂₁NO₂",
        "atoms": [
            ("C", -3.6), ("C", -2.4), ("C", 2.4), ("C", 3.6),
            ("N", 0.0), ("O", 0.8), ("O", 2.8), ("C", 1.4),
            ("C", -1.4), ("C", 3.0), ("C", 2.0), ("C", -3.0),
            ("C", -2.0), ("C", 0.6), ("C", 1.0), ("C", -0.8),
            ("C", 2.6), ("C", -2.6), ("C", 3.8), ("C", -3.8),
            ("C", 4.4), ("H", 1.8), ("H", -1.8), ("H", 3.4),
            ("H", -3.4), ("H", 2.2), ("H", -2.2), ("H", 4.0)
        ],
        "qubits": 12,
        "electrons": 124,
        "reference": -699.8876,
        "binding": -4.1870
    },

    "Dextromethorphan": {
        "name": "Dextromethorphan",
        "formula": "C₁₈H₂₅NO",
        "atoms": [
            ("C", -3.6), ("C", -2.4), ("C", 2.4), ("C", 3.6),
            ("N", 0.0), ("O", 3.2), ("C", 1.4), ("C", -1.4),
            ("C", 3.0), ("C", 2.2), ("C", -3.0), ("C", -2.2),
            ("C", 0.6), ("C", 1.0), ("C", -0.8), ("C", 2.6),
            ("C", -2.6), ("C", 3.8), ("C", -3.8), ("C", 4.0),
            ("C", -4.0), ("C", 1.8), ("C", -1.8), ("H", 1.6),
            ("H", 3.4), ("H", 2.4), ("H", -3.4), ("H", 4.4),
            ("H", -4.4), ("H", 2.0)
        ],
        "qubits": 12,
        "electrons": 140,
        "reference": -712.4536,
        "binding": -4.3210
    },

    "PenicillinG": {
        "name": "Benzylpenicillin",
        "formula": "C₁₆H₁₈N₂O₄S",
        "atoms": [
            ("C", -3.2), ("C", -2.0), ("C", 2.0), ("C", 3.2),
            ("N", 0.0), ("N", 1.4), ("O", 3.6), ("O", -3.6),
            ("S", 2.8), ("O", 0.4), ("O", -0.6), ("C", 1.8),
            ("C", 0.6), ("C", -1.8), ("C", -0.4), ("C", 2.4),
            ("C", 3.8), ("C", -2.4), ("C", 4.0), ("H", 1.2),
            ("H", -2.6), ("H", 3.2), ("H", -1.2), ("H", 4.4),
            ("H", 2.0), ("H", 0.0), ("H", -1.6)
        ],
        "qubits": 12,
        "electrons": 152,
        "reference": -1098.3321,
        "binding": -5.2780
    },

    "Sildenafil": {
        "name": "Sildenafil",
        "formula": "C₂₂H₃₀N₆O₄S",
        "atoms": [
            ("C", -4.0), ("C", -3.0), ("C", -2.0), ("C", 2.0),
            ("C", 3.0), ("C", 4.0), ("N", -1.2), ("N", 1.2),
            ("N", 2.8), ("N", 0.0), ("N", -2.8), ("N", 3.4),
            ("O", 1.4), ("O", -1.4), ("O", 4.2), ("S", 2.2),
            ("O", 0.6), ("C", 0.8), ("C", 2.0), ("C", -2.0),
            ("C", 3.6), ("C", -3.6), ("C", 1.6), ("C", -1.6),
            ("C", 4.4), ("C", -4.4), ("C", 2.4), ("C", 3.0),
            ("H", 2.2), ("H", -2.2), ("H", 3.8), ("H", -3.8),
            ("H", 1.2), ("H", 4.0), ("H", 1.0)
        ],
        "qubits": 12,
        "electrons": 214,
        "reference": -1620.5567,
        "binding": -6.4780
    },

    "Diazepam": {
        "name": "Diazepam",
        "formula": "C₁₆H₁₃ClN₂O",
        "atoms": [
            ("C", -3.4), ("C", -2.2), ("C", 2.2), ("C", 3.4),
            ("Cl", 4.2), ("N", 0.0), ("N", 1.0), ("O", -3.8),
            ("C", 0.8), ("C", -0.8), ("C", 1.8), ("C", -1.8),
            ("C", 3.0), ("C", -3.0), ("C", 2.4), ("C", -2.4),
            ("C", 1.2), ("C", -1.2), ("C", 3.8), ("H", 1.4),
            ("H", -1.4), ("H", 3.2), ("H", -3.2), ("H", 2.8),
            ("H", -2.8), ("H", 4.0), ("H", -4.0)
        ],
        "qubits": 12,
        "electrons": 124,
        "reference": -1098.8876,
        "binding": -5.1760
    },

    "VitaminC": {
        "name": "Ascorbic acid",
        "formula": "C₆H₈O₆",
        "atoms": [
            ("C", -2.6), ("C", -1.4), ("C", 1.4), ("C", 2.6),
            ("O", -3.4), ("O", 3.4), ("O", 0.2), ("O", -0.8),
            ("O", 2.0), ("O", -2.0), ("C", 0.2), ("C", -0.2),
            ("H", -3.0), ("H", -1.0), ("H", 1.0), ("H", 3.0),
            ("H", 2.4), ("H", -2.4), ("H", 0.4)
        ],
        "qubits": 12,
        "electrons": 84,
        "reference": -683.5567,
        "binding": -3.9870
    },

    "Doxycycline": {
        "name": "Doxycycline",
        "formula": "C₂₂H₂₄N₂O₈",
        "atoms": [
            ("C", -4.0), ("C", -3.0), ("C", -2.0), ("C", 2.0),
            ("C", 3.0), ("C", 4.0), ("N", 0.0), ("N", 1.0),
            ("O", 1.4), ("O", -1.4), ("O", 3.4), ("O", -3.4),
            ("O", 4.2), ("O", -4.2), ("O", 0.6), ("O", -0.6),
            ("C", 0.8), ("C", 1.8), ("C", -1.8), ("C", 2.4),
            ("C", -2.4), ("C", 3.4), ("C", -3.4), ("C", 1.2),
            ("C", -1.2), ("C", 4.4), ("C", -4.4), ("C", 2.0),
            ("H", 2.2), ("H", -2.2), ("H", 3.0), ("H", -3.0),
            ("H", 4.0), ("H", 1.6), ("H", -1.6), ("H", 4.6)
        ],
        "qubits": 12,
        "electrons": 206,
        "reference": -1567.3346,
        "binding": -6.5120
    },

    "Morphine": {
        "name": "Morphine",
        "formula": "C₁₇H₁₉NO₃",
        "atoms": [
            ("C", -3.4), ("C", -2.2), ("C", 2.2), ("C", 3.4),
            ("N", 0.0), ("O", 3.6), ("O", -3.6), ("O", 0.4),
            ("C", 1.4), ("C", -1.4), ("C", 3.0), ("C", -3.0),
            ("C", 0.6), ("C", -0.6), ("C", 2.0), ("C", -2.0),
            ("C", 2.6), ("C", -2.6), ("C", 4.0), ("H", 1.8),
            ("H", -1.8), ("H", 3.4), ("H", -3.4), ("H", 2.2),
            ("H", -2.2), ("H", 4.4)
        ],
        "qubits": 12,
        "electrons": 132,
        "reference": -853.5567,
        "binding": -4.8870
    },

    "Tetracaine": {
        "name": "Tetracaine",
        "formula": "C₁₅H₂₄N₂O₂",
        "atoms": [
            ("C", -3.2), ("C", -2.0), ("C", 2.0), ("C", 3.2),
            ("N", 0.0), ("N", 1.2), ("O", 3.6), ("O", -3.4),
            ("C", 0.6), ("C", 1.8), ("C", -1.8), ("C", 2.6),
            ("C", -2.6), ("C", 1.4), ("C", -1.4), ("C", 3.0),
            ("C", -3.0), ("C", 2.2), ("C", -2.2), ("C", 4.0),
            ("C", -4.0), ("H", 1.0), ("H", -1.0), ("H", 3.4),
            ("H", -3.4), ("H", 2.4), ("H", -2.4), ("H", 4.4)
        ],
        "qubits": 12,
        "electrons": 132,
        "reference": -778.3345,
        "binding": -4.5560
    },

    "Captopril": {
        "name": "Captopril",
        "formula": "C₉H₁₅NO₃S",
        "atoms": [
            ("C", -2.6), ("C", -1.4), ("C", 1.4), ("C", 2.6),
            ("N", 0.0), ("O", 3.0), ("O", -3.0), ("S", 2.0),
            ("O", 0.6), ("C", 0.4), ("C", 1.2), ("C", -0.6),
            ("C", 1.8), ("C", -1.8), ("C", 2.4), ("C", -2.4),
            ("C", 3.2), ("H", 0.8), ("H", -0.2), ("H", 1.6),
            ("H", -2.2), ("H", 2.0), ("H", 3.4), ("H", 2.8)
        ],
        "qubits": 12,
        "electrons": 118,
        "reference": -835.2211,
        "binding": -4.8650
    },

    "Ribavirin": {
        "name": "Ribavirin",
        "formula": "C₈H₁₂N₄O₅",
        "atoms": [
            ("C", -2.6), ("C", -1.4), ("C", 1.4), ("C", 2.6),
            ("N", -1.0), ("N", 1.0), ("N", 2.0), ("N", -2.0),
            ("O", 0.2), ("O", -0.2), ("O", 3.2), ("O", -3.2),
            ("O", 1.6), ("C", 0.4), ("C", -0.4), ("C", 1.8),
            ("C", -1.8), ("C", 2.4), ("C", -2.4), ("H", 0.8),
            ("H", -0.8), ("H", 2.0), ("H", -2.0), ("H", 3.4),
            ("H", -3.4), ("H", 1.2), ("H", -1.2)
        ],
        "qubits": 12,
        "electrons": 124,
        "reference": -882.4456,
        "binding": -4.9980
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