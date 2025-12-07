"""
Risk Ontology Manager

Maps Walk Risk's RiskType enum to ontology concepts and provides
risk-related semantic operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from walk_risk.models.risk.base import RiskType, RiskLevel

if TYPE_CHECKING:
    from walk_risk.ontology.adapter import WalkRiskOntologyAdapter


# Mapping from RiskType enum to ontology class names
RISK_TYPE_MAPPING: dict[RiskType, str] = {
    RiskType.MARKET: "MarketRisk",
    RiskType.CREDIT: "CreditRisk",
    RiskType.OPERATIONAL: "OperationalRisk",
    RiskType.STRATEGIC: "StrategicRisk",
}

# Reverse mapping
ONTOLOGY_TO_RISK_TYPE: dict[str, RiskType] = {v: k for k, v in RISK_TYPE_MAPPING.items()}

# Risk level to difficulty mapping
RISK_LEVEL_DEPTH: dict[RiskLevel, int] = {
    RiskLevel.BEGINNER: 1,
    RiskLevel.INTERMEDIATE: 2,
    RiskLevel.ADVANCED: 3,
    RiskLevel.EXPERT: 4,
}

# Subcategory mapping for detailed risk classification
RISK_SUBCATEGORIES: dict[RiskType, dict[str, list[str]]] = {
    RiskType.MARKET: {
        "systemic": ["SystemicRisk"],
        "volatility": ["VolatilityRisk"],
        "liquidity": ["LiquidityRisk"],
        "currency": ["CurrencyRisk"],
        "interest_rate": ["InterestRateRisk"],
    },
    RiskType.CREDIT: {
        "default": ["DefaultRisk"],
        "counterparty": ["CounterpartyRisk"],
        "downgrade": ["DowngradeRisk"],
    },
    RiskType.OPERATIONAL: {
        "process": ["ProcessRisk"],
        "system": ["SystemFailureRisk"],
        "compliance": ["ComplianceRisk"],
    },
    RiskType.STRATEGIC: {
        "business_model": ["BusinessModelRisk"],
        "competitive": ["CompetitiveRisk"],
        "regulatory": ["RegulatoryRisk"],
    },
}


class RiskOntologyManager:
    """
    Manages risk classification using ontology.

    Provides mapping between Walk Risk's RiskType enum and the
    ontology's risk hierarchy, enabling semantic queries and
    detailed risk classification.

    Example:
        adapter = WalkRiskOntologyAdapter()
        risk_manager = RiskOntologyManager(adapter)

        # Get subcategories
        subcats = risk_manager.get_subcategories(RiskType.MARKET)

        # Classify event
        risks = risk_manager.classify_market_event({
            "change_percent": -5.0,
            "volume_ratio": 3.0,
        })
    """

    def __init__(self, adapter: WalkRiskOntologyAdapter) -> None:
        """
        Initialize the risk ontology manager.

        Args:
            adapter: WalkRiskOntologyAdapter instance
        """
        self.adapter = adapter

    def get_ontology_class(self, risk_type: RiskType) -> str:
        """
        Get the ontology class name for a RiskType.

        Args:
            risk_type: RiskType enum value

        Returns:
            Ontology class name (e.g., "MarketRisk")
        """
        return RISK_TYPE_MAPPING.get(risk_type, "Risk")

    def get_risk_type(self, ontology_class: str) -> RiskType | None:
        """
        Get the RiskType enum for an ontology class name.

        Args:
            ontology_class: Ontology class name

        Returns:
            RiskType enum or None if not found
        """
        return ONTOLOGY_TO_RISK_TYPE.get(ontology_class)

    def get_subcategories(self, risk_type: RiskType) -> list[dict[str, str]]:
        """
        Get subcategories of a risk type from the ontology.

        Args:
            risk_type: RiskType enum value

        Returns:
            List of subcategory dictionaries with uri, label, and comment
        """
        ontology_class = self.get_ontology_class(risk_type)
        return self.adapter.get_risk_subcategories(ontology_class)

    def get_hierarchy(self, risk_type: RiskType) -> dict[str, Any]:
        """
        Get the full hierarchy for a risk type.

        Args:
            risk_type: RiskType enum value

        Returns:
            Dictionary with risk hierarchy information
        """
        ontology_class = self.get_ontology_class(risk_type)
        return self.adapter.get_risk_hierarchy(ontology_class)

    def get_mitigations(self, risk_type: RiskType) -> list[dict[str, str]]:
        """
        Get investment philosophies that mitigate a specific risk type.

        Args:
            risk_type: RiskType enum value

        Returns:
            List of mitigation strategy dictionaries
        """
        ontology_class = self.get_ontology_class(risk_type)
        return self.adapter.get_risk_mitigations(ontology_class)

    def get_indicators(self, risk_type: RiskType) -> list[dict[str, str]]:
        """
        Get financial indicators that measure a specific risk type.

        Args:
            risk_type: RiskType enum value

        Returns:
            List of indicator dictionaries
        """
        ontology_class = self.get_ontology_class(risk_type)
        return self.adapter.get_indicator_for_risk(ontology_class)

    def classify_market_event(
        self,
        event_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Classify a market event into risk categories.

        Uses heuristic rules combined with ontology relationships
        to determine which risk categories apply to a market event.

        Args:
            event_data: Dictionary containing event information:
                - change_percent: Price change percentage
                - volume_ratio: Volume compared to average
                - event_type: Type of event (optional)
                - sector: Market sector (optional)

        Returns:
            List of applicable risk classifications with confidence
        """
        classifications = []
        change = event_data.get("change_percent", 0)
        volume = event_data.get("volume_ratio", 1.0)
        event_type = event_data.get("event_type", "")

        # Market Risk classification rules
        if abs(change) > 5.0:
            classifications.append({
                "risk_type": RiskType.MARKET,
                "subcategory": "VolatilityRisk",
                "confidence": min(abs(change) / 10.0, 1.0),
                "reason": f"High price volatility ({change:+.1f}%)",
            })

        if abs(change) > 10.0:
            classifications.append({
                "risk_type": RiskType.MARKET,
                "subcategory": "SystemicRisk",
                "confidence": min(abs(change) / 20.0, 1.0),
                "reason": f"Extreme price movement ({change:+.1f}%)",
            })

        if volume > 3.0:
            classifications.append({
                "risk_type": RiskType.MARKET,
                "subcategory": "LiquidityRisk",
                "confidence": min(volume / 5.0, 1.0),
                "reason": f"Unusual volume ({volume:.1f}x average)",
            })

        # Event type based classification
        if "earnings" in event_type.lower():
            classifications.append({
                "risk_type": RiskType.OPERATIONAL,
                "subcategory": None,
                "confidence": 0.7,
                "reason": "Earnings announcement event",
            })

        if "regulatory" in event_type.lower():
            classifications.append({
                "risk_type": RiskType.STRATEGIC,
                "subcategory": "RegulatoryRisk",
                "confidence": 0.8,
                "reason": "Regulatory event",
            })

        # Default to market risk if nothing specific found
        if not classifications:
            classifications.append({
                "risk_type": RiskType.MARKET,
                "subcategory": None,
                "confidence": 0.5,
                "reason": "General market event",
            })

        return classifications

    def get_risk_description(
        self,
        risk_type: RiskType,
        language: str = "ko",
    ) -> str | None:
        """
        Get the description of a risk type in the specified language.

        Args:
            risk_type: RiskType enum value
            language: Language code ("ko" for Korean, "en" for English)

        Returns:
            Description string or None
        """
        ontology_class = self.get_ontology_class(risk_type)
        query = f"""
        PREFIX wrisk_class: <http://walkrisk.org/class#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?comment WHERE {{
            wrisk_class:{ontology_class} rdfs:comment ?comment .
            FILTER(LANG(?comment) = "{language}" || LANG(?comment) = "")
        }}
        LIMIT 1
        """
        results = self.adapter.query(query)
        if results:
            return results[0].get("comment")
        return None

    def get_all_risks_for_level(
        self,
        risk_level: RiskLevel,
    ) -> list[dict[str, Any]]:
        """
        Get all risk concepts appropriate for a given difficulty level.

        Args:
            risk_level: RiskLevel enum value

        Returns:
            List of risk concepts with their details
        """
        depth = RISK_LEVEL_DEPTH.get(risk_level, 1)
        risks = []

        for risk_type in RiskType:
            ontology_class = self.get_ontology_class(risk_type)

            # For beginner, only top-level risks
            if depth == 1:
                risks.append({
                    "risk_type": risk_type,
                    "ontology_class": ontology_class,
                    "level": RiskLevel.BEGINNER,
                })
            else:
                # Include subcategories for higher levels
                subcategories = self.get_subcategories(risk_type)
                for subcat in subcategories[:depth - 1]:
                    risks.append({
                        "risk_type": risk_type,
                        "ontology_class": subcat.get("uri", "").split("#")[-1],
                        "label": subcat.get("label", ""),
                        "level": risk_level,
                    })

        return risks
