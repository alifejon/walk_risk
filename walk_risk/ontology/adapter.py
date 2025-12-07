"""
Walk Risk Ontology Adapter

Bridge between Walk Risk and the grokipedia-ontology framework.
Provides clean interfaces for ontology operations in the context of
financial risk management and investment education.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add grokipedia-ontology to path for local development
GROKIPEDIA_SRC = Path(__file__).parent.parent.parent / "grokipedia-ontology" / "src"
if GROKIPEDIA_SRC.exists() and str(GROKIPEDIA_SRC) not in sys.path:
    sys.path.insert(0, str(GROKIPEDIA_SRC))

from rdflib import Namespace
from grokipedia_ontology import GrokipediaOntology, Concept, Relation
from grokipedia_ontology.models import ConceptType, RelationType


# Walk Risk specific namespaces
WRISK = Namespace("http://walkrisk.org/ontology#")
WRISK_CLASS = Namespace("http://walkrisk.org/class#")
WRISK_PROP = Namespace("http://walkrisk.org/property#")

# Path to financial ontology
FINANCIAL_ONTOLOGY_PATH = (
    Path(__file__).parent.parent.parent
    / "grokipedia-ontology"
    / "ontology"
    / "walk_risk_financial.ttl"
)


class WalkRiskOntologyAdapter:
    """
    Adapter class that wraps grokipedia-ontology for Walk Risk use cases.

    Provides:
    - Risk taxonomy navigation
    - Mentor knowledge lookup
    - Investment concept relationships
    - SPARQL query interface

    Example:
        adapter = WalkRiskOntologyAdapter()
        subcategories = adapter.get_risk_subcategories("MarketRisk")
        mentor_info = adapter.get_mentor_philosophy("buffett")
    """

    def __init__(self, ontology_path: Path | None = None) -> None:
        """
        Initialize the Walk Risk ontology adapter.

        Args:
            ontology_path: Optional path to custom ontology file.
                          If None, loads the default walk_risk_financial.ttl
        """
        self.ontology = GrokipediaOntology(base_uri="http://walkrisk.org/ontology")
        self._setup_namespaces()

        # Load financial ontology
        path = ontology_path or FINANCIAL_ONTOLOGY_PATH
        if path.exists():
            self.ontology.load(path)
            self._loaded = True
        else:
            self._loaded = False

    def _setup_namespaces(self) -> None:
        """Bind Walk Risk namespaces to the graph."""
        self.ontology.graph.bind("wrisk", WRISK)
        self.ontology.graph.bind("wrisk_class", WRISK_CLASS)
        self.ontology.graph.bind("wrisk_prop", WRISK_PROP)

    @property
    def is_loaded(self) -> bool:
        """Check if the ontology was successfully loaded."""
        return self._loaded

    def query(self, sparql: str) -> list[dict[str, Any]]:
        """
        Execute a SPARQL query on the ontology.

        Args:
            sparql: SPARQL query string

        Returns:
            List of result bindings as dictionaries
        """
        return self.ontology.query(sparql)

    # =========================================================================
    # Risk Operations
    # =========================================================================

    def get_risk_hierarchy(self, risk_type: str) -> dict[str, Any]:
        """
        Get the full hierarchy for a risk type.

        Args:
            risk_type: Risk type name (e.g., "MarketRisk", "CreditRisk")

        Returns:
            Dictionary with risk hierarchy information
        """
        query = f"""
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?subclass ?label ?comment WHERE {{
            ?subclass rdfs:subClassOf* wrisk_class:{risk_type} .
            ?subclass rdfs:label ?label .
            OPTIONAL {{ ?subclass rdfs:comment ?comment }}
            FILTER(LANG(?label) = "ko" || LANG(?label) = "")
        }}
        """
        results = self.query(query)
        return {
            "risk_type": risk_type,
            "hierarchy": results,
        }

    def get_risk_subcategories(self, risk_type: str) -> list[dict[str, str]]:
        """
        Get direct subcategories of a risk type.

        Args:
            risk_type: Risk type name (e.g., "MarketRisk")

        Returns:
            List of subcategory dictionaries with name, label, and comment
        """
        query = f"""
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?subclass ?label ?comment WHERE {{
            ?subclass rdfs:subClassOf wrisk_class:{risk_type} .
            ?subclass rdfs:label ?label .
            OPTIONAL {{ ?subclass rdfs:comment ?comment }}
            FILTER(LANG(?label) = "ko" || LANG(?label) = "")
        }}
        """
        results = self.query(query)
        return [
            {
                "uri": r.get("subclass", ""),
                "label": r.get("label", ""),
                "comment": r.get("comment", ""),
            }
            for r in results
        ]

    def get_risk_mitigations(self, risk_type: str) -> list[dict[str, str]]:
        """
        Get investment philosophies that mitigate a specific risk.

        Args:
            risk_type: Risk type name

        Returns:
            List of mitigation strategies
        """
        query = f"""
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX wrisk_prop: <http://walkrisk.org/property#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?philosophy ?label WHERE {{
            ?philosophy wrisk_prop:mitigates wrisk_class:{risk_type} .
            ?philosophy rdfs:label ?label .
            FILTER(LANG(?label) = "ko" || LANG(?label) = "")
        }}
        """
        results = self.query(query)
        return [
            {"uri": r.get("philosophy", ""), "label": r.get("label", "")}
            for r in results
        ]

    # =========================================================================
    # Mentor Operations
    # =========================================================================

    def get_mentor_philosophy(self, mentor_name: str) -> dict[str, Any]:
        """
        Get investment philosophy and expertise for a mentor.

        Args:
            mentor_name: Mentor name (e.g., "WarrenBuffett", "PeterLynch")

        Returns:
            Dictionary with mentor's philosophy, risk expertise, and concepts
        """
        query = f"""
        PREFIX wrisk: <http://walkrisk.org/ontology#>
        PREFIX wrisk_prop: <http://walkrisk.org/property#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?property ?value ?valueLabel WHERE {{
            wrisk:{mentor_name} ?property ?value .
            OPTIONAL {{ ?value rdfs:label ?valueLabel }}
        }}
        """
        results = self.query(query)

        # Organize results
        philosophy = None
        risk_expertise = []
        concepts = []
        indicators = []

        for r in results:
            prop = r.get("property", "")
            value = r.get("value", "")
            label = r.get("valueLabel", value)

            if "hasPhilosophy" in prop:
                philosophy = {"uri": value, "label": label}
            elif "specializesIn" in prop:
                risk_expertise.append({"uri": value, "label": label})
            elif "usesConcept" in prop:
                concepts.append({"uri": value, "label": label})
            elif "usesIndicator" in prop:
                indicators.append({"uri": value, "label": label})

        return {
            "mentor": mentor_name,
            "philosophy": philosophy,
            "risk_expertise": risk_expertise,
            "concepts": concepts,
            "indicators": indicators,
        }

    def get_mentor_risk_expertise(self, mentor_name: str) -> list[str]:
        """
        Get risk types a mentor specializes in.

        Args:
            mentor_name: Mentor name

        Returns:
            List of risk type URIs
        """
        query = f"""
        PREFIX wrisk: <http://walkrisk.org/ontology#>
        PREFIX wrisk_prop: <http://walkrisk.org/property#>

        SELECT ?risk WHERE {{
            wrisk:{mentor_name} wrisk_prop:specializesIn ?risk .
        }}
        """
        results = self.query(query)
        return [r.get("risk", "") for r in results]

    def get_all_mentors(self) -> list[dict[str, str]]:
        """
        Get all mentor personas defined in the ontology.

        Returns:
            List of mentor dictionaries with uri and labels
        """
        query = """
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?mentor ?label WHERE {
            ?mentor a wrisk_class:MentorPersona .
            ?mentor rdfs:label ?label .
        }
        """
        results = self.query(query)
        return [
            {"uri": r.get("mentor", ""), "label": r.get("label", "")}
            for r in results
        ]

    # =========================================================================
    # Investment Concept Operations
    # =========================================================================

    def get_related_concepts(
        self, concept_name: str, max_depth: int = 2
    ) -> list[dict[str, Any]]:
        """
        Get concepts related to a given concept.

        Args:
            concept_name: Name of the concept to find relations for
            max_depth: Maximum relationship depth to traverse

        Returns:
            List of related concept dictionaries
        """
        # For MVP, use a simple query
        query = f"""
        PREFIX wrisk: <http://walkrisk.org/ontology#>
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX grok_prop: <http://grokipedia.org/property#>

        SELECT ?related ?label ?relation WHERE {{
            {{
                wrisk_class:{concept_name} ?relation ?related .
                ?related rdfs:label ?label .
            }}
            UNION
            {{
                ?related ?relation wrisk_class:{concept_name} .
                ?related rdfs:label ?label .
            }}
        }}
        LIMIT 20
        """
        results = self.query(query)
        return [
            {
                "concept": r.get("related", ""),
                "label": r.get("label", ""),
                "relation": r.get("relation", ""),
            }
            for r in results
        ]

    def get_indicator_for_risk(self, risk_type: str) -> list[dict[str, str]]:
        """
        Get financial indicators that measure a specific risk.

        Args:
            risk_type: Risk type name

        Returns:
            List of indicators
        """
        query = f"""
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX wrisk_prop: <http://walkrisk.org/property#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?indicator ?label WHERE {{
            ?indicator wrisk_prop:measures wrisk_class:{risk_type} .
            ?indicator rdfs:label ?label .
        }}
        """
        results = self.query(query)
        return [
            {"uri": r.get("indicator", ""), "label": r.get("label", "")}
            for r in results
        ]

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_korean_label(self, concept_uri: str) -> str | None:
        """
        Get Korean label for a concept.

        Args:
            concept_uri: Full URI of the concept

        Returns:
            Korean label string or None
        """
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?label WHERE {{
            <{concept_uri}> rdfs:label ?label .
            FILTER(LANG(?label) = "ko")
        }}
        """
        results = self.query(query)
        if results:
            return results[0].get("label")
        return None

    def get_stats(self) -> dict[str, int]:
        """
        Get basic statistics about the ontology.

        Returns:
            Dictionary with counts of various elements
        """
        # Count risks
        risk_query = """
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT (COUNT(?risk) as ?count) WHERE {
            ?risk rdfs:subClassOf* wrisk_class:Risk .
        }
        """

        # Count philosophies
        philosophy_query = """
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT (COUNT(?p) as ?count) WHERE {
            ?p rdfs:subClassOf* wrisk_class:InvestmentPhilosophy .
        }
        """

        # Count mentors
        mentor_query = """
        PREFIX wrisk_class: <http://walkrisk.org/class#>

        SELECT (COUNT(?m) as ?count) WHERE {
            ?m a wrisk_class:MentorPersona .
        }
        """

        risk_results = self.query(risk_query)
        philosophy_results = self.query(philosophy_query)
        mentor_results = self.query(mentor_query)

        return {
            "risk_concepts": int(risk_results[0].get("count", 0)) if risk_results else 0,
            "investment_philosophies": (
                int(philosophy_results[0].get("count", 0)) if philosophy_results else 0
            ),
            "mentor_personas": (
                int(mentor_results[0].get("count", 0)) if mentor_results else 0
            ),
            "total_triples": len(self.ontology.graph),
        }
