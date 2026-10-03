from typing import List, Optional
from pydantic import BaseModel, Field

class Medication(BaseModel):
    name: str = Field(description="Generic or brand name of the medication")
    dosage: str = Field(description="Strength and form, e.g., 500mg capsule")
    frequency: str = Field(description="How often to take it, e.g., twice daily")
    timing: str = Field(description="Meal or time instruction, e.g., after food")
    purpose: str = Field(description="Simple explanation of what the medicine treats")
    critical_warning: Optional[str] = Field(default=None, description="Key caution or side-effect warning")

class DrugInteraction(BaseModel):
    medications_involved: List[str] = Field(description="List of medicines involved in the interaction")
    severity: str = Field(description="Severity level: 'High', 'Moderate', or 'Low'")
    effect: str = Field(description="Plain-English explanation of what happens if taken together")
    clinical_recommendation: str = Field(description="Recommended precaution or spacing advice")

class PrescriptionAnalysis(BaseModel):
    doctor_notes_summary: str = Field(description="Brief summary of diagnosis or treatment plan")
    medications: List[Medication] = Field(description="List of all detected medications")
    drug_interactions: List[DrugInteraction] = Field(
        default_factory=list,
        description="Any potential adverse interactions detected between the listed drugs"
    )
    confidence_warning: Optional[str] = Field(default=None, description="Warning if handwriting was unclear")
    follow_up_advice: Optional[str] = Field(default=None, description="Doctor follow-up guidance")