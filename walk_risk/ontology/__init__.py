"""
Walk Risk Ontology Module

This module provides integration between Walk Risk and the grokipedia-ontology
framework for semantic knowledge representation of financial concepts.

Example usage:
    from walk_risk.ontology import WalkRiskOntologyAdapter, RiskOntologyManager

    # Initialize the adapter
    adapter = WalkRiskOntologyAdapter()

    # Use risk ontology
    risk_manager = RiskOntologyManager(adapter)
    subcategories = risk_manager.get_risk_subcategories("MARKET")
"""

from walk_risk.ontology.adapter import WalkRiskOntologyAdapter
from walk_risk.ontology.risk_ontology import RiskOntologyManager, RISK_TYPE_MAPPING

__all__ = [
    "WalkRiskOntologyAdapter",
    "RiskOntologyManager",
    "RISK_TYPE_MAPPING",
]
