"""
Sustainability Scoring System for Fashion Products.

A data-driven sustainability scoring system for fashion products that integrates
material LCA indicators, manufacturing origin impacts, care-phase environmental
costs, and sustainability certifications.
"""

from sustainability_scoring.scoring.calculator import calculate_sustainability_score
from sustainability_scoring.data.loader import load_product_data, load_reference_tables
from sustainability_scoring.data.cleaner import clean_product_data, merge_reference_data

__version__ = "0.1.0"

__all__ = [
    "calculate_sustainability_score",
    "load_product_data",
    "load_reference_tables",
    "clean_product_data",
    "merge_reference_data",
]
