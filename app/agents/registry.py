from __future__ import annotations

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.destination_agent import DestinationResearchAgent
from app.agents.etiquette_agent import LocalEtiquetteAgent
from app.agents.final_agent import FinalAdvisoryAgent
from app.agents.health_agent import HealthAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.packing_agent import PackingAgent
from app.agents.profile_agent import ProfileAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.transport_agent import TransportAgent
from app.agents.visa_agent import VisaEntryAgent
from app.agents.weather_agent import WeatherAgent

AGENT_CLASSES = [
    ProfileAgent,
    DestinationResearchAgent,
    WeatherAgent,
    SafetyAgent,
    VisaEntryAgent,
    HealthAgent,
    LocalEtiquetteAgent,
    TransportAgent,
    AccommodationAgent,
    BudgetAgent,
    ItineraryAgent,
    PackingAgent,
    FinalAdvisoryAgent,
]

AGENT_CATALOG = [
    {"name": cls.name, "purpose": cls.purpose}
    for cls in AGENT_CLASSES
]
