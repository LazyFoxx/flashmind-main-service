from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.application.interfaces.ai_service import (
    AIInsight,
    AIProblemArea,
    AIRecommendation,
    AIGoals,
)


@dataclass(frozen=True, slots=True)
class AIAnalyzeStudyStatInput:
    user_id: UUID
    deck_id: Optional[UUID] = None


@dataclass(frozen=True, slots=True)
class AIAnalyzeStudyStatOutput:
    analysis_date: datetime
    analysis_next_date: datetime
    analysis_success: bool
    
        # Structured fields (из AIStudyAnalysisResult)
    insights: list[AIInsight] = field(default_factory=list)
    problem_areas: list[AIProblemArea] = field(default_factory=list)
    recommendations: list[AIRecommendation] = field(default_factory=list)
    goals: list[AIGoals] = field(default_factory=list)
