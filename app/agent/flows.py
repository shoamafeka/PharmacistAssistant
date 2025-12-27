"""
Flow manager for Pharmacist Agent capabilities.
Serves as a single source of truth for all AI flows and their guidance.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FlowStep:
    """Represents a single step in a flow with moderate guidance."""
    step_number: int
    description: str
    guidance: str


class Flow:
    """Base class for defining agent flows."""
    
    def __init__(
        self,
        name: str,
        description: str,
        when_to_use: str,
        key_steps: List[FlowStep],
        expected_tool_sequence: List[str]
    ):
        self.name = name
        self.description = description
        self.when_to_use = when_to_use
        self.key_steps = key_steps
        self.expected_tool_sequence = expected_tool_sequence
    
    def get_guidance_text(self) -> str:
        """Generate formatted prompt text for this flow."""
        tool_sequence_str = " → ".join(self.expected_tool_sequence)
        
        steps_text = "\n".join([
            f"  {step.step_number}. {step.description}\n     {step.guidance}"
            for step in self.key_steps
        ])
        
        return f"""**{self.name}**
- When to use: {self.when_to_use}
- Expected tool sequence: {tool_sequence_str}
- Key steps:
{steps_text}
"""


class MedicationStockCheckFlow(Flow):
    """Flow for checking medication stock availability."""
    
    def __init__(self):
        super().__init__(
            name="Medication Stock Check",
            description="Check medication stock availability",
            when_to_use="User asks about medication availability, stock status, or whether a medication is in stock",
            key_steps=[
                FlowStep(
                    step_number=1,
                    description="Ask for medication name",
                    guidance="When user wants to check stock, ask for the medication name. No user_id is needed."
                ),
                FlowStep(
                    step_number=2,
                    description="Call check_medication_stock tool",
                    guidance="Call check_medication_stock([medication_name]) to check availability"
                ),
                FlowStep(
                    step_number=3,
                    description="Report stock status",
                    guidance="Report whether medication is in_stock, low_stock, or out_of_stock. Provide clear answer about availability. DO NOT suggest alternative purchasing methods (like 'over the counter' availability) unless explicitly part of the pharmacy system's services. Only report stock status from the tool results."
                )
            ],
            expected_tool_sequence=["check_medication_stock"]
        )


class UsageGuidanceFlow(Flow):
    """Flow for providing medication usage guidance."""
    
    def __init__(self):
        super().__init__(
            name="Medication Information & Usage",
            description="Get details about medications, dosages, and usage instructions",
            when_to_use="User asks about medication usage, dosage, how to take medication, or medication information",
            key_steps=[
                FlowStep(
                    step_number=1,
                    description="Ask for medication name",
                    guidance="When user asks about usage, ask for the medication name"
                ),
                FlowStep(
                    step_number=2,
                    description="Call get_medication_info tool",
                    guidance="Call get_medication_info(medication_name) to retrieve usage instructions"
                ),
                FlowStep(
                    step_number=3,
                    description="Explain usage details",
                    guidance="Explain dosage, frequency, administration based on the retrieved information"
                ),
                FlowStep(
                    step_number=4,
                    description="Offer to check special instructions",
                    guidance="Offer to check if user has any special instructions for this medication. Optionally call get_user_prescriptions(user_id) if user_id is provided."
                ),
                FlowStep(
                    step_number=5,
                    description="Provide complete guidance",
                    guidance="Provide complete usage guidance with warnings. Remind user that this is factual information only, not medical advice."
                )
            ],
            expected_tool_sequence=["get_medication_info", "get_user_prescriptions"]
        )


class PrescriptionVerificationFlow(Flow):
    """Flow for verifying prescription status."""
    
    def __init__(self):
        super().__init__(
            name="Prescription Verification",
            description="Verify prescription status and details",
            when_to_use="User wants to verify a prescription, check prescription status, or confirm prescription details",
            key_steps=[
                FlowStep(
                    step_number=1,
                    description="Ask for user_id and prescription_id",
                    guidance="When user wants to verify prescription, ask for both user_id (customer ID) and prescription_id"
                ),
                FlowStep(
                    step_number=2,
                    description="Call verify_prescription tool",
                    guidance="Call verify_prescription(user_id, prescription_id) to check validity and status (active/expired)"
                ),
                FlowStep(
                    step_number=3,
                    description="Retrieve medication details",
                    guidance="Call get_medication_info(medication_name) to retrieve medication details from the verified prescription"
                ),
                FlowStep(
                    step_number=4,
                    description="Check stock availability",
                    guidance="Call check_medication_stock([medication_name]) to check availability"
                ),
                FlowStep(
                    step_number=5,
                    description="Provide complete status",
                    guidance="Provide complete prescription status with medication info and availability. Include prescription validity and status. DO NOT suggest alternative purchasing methods (like 'over the counter' availability) unless explicitly part of the pharmacy system's services. Only report what the tools provide: prescription status, stock availability, and prescription requirement status from the medication data."
                )
            ],
            expected_tool_sequence=["verify_prescription", "get_medication_info", "check_medication_stock"]
        )


class FlowManager:
    """Manages all available flows and generates prompts."""
    
    def __init__(self):
        self.flows = [
            MedicationStockCheckFlow(),
            UsageGuidanceFlow(),
            PrescriptionVerificationFlow()
        ]
    
    def get_flow_by_name(self, name: str) -> Optional[Flow]:
        """Get a flow by its name."""
        for flow in self.flows:
            if flow.name == name:
                return flow
        return None
    
    def get_all_flows(self) -> List[Flow]:
        """Get all registered flows."""
        return self.flows
    
    def get_flow_descriptions(self) -> str:
        """Get formatted list of flow descriptions for welcome message."""
        descriptions = []
        for i, flow in enumerate(self.flows, 1):
            descriptions.append(f"{i}. **{flow.name}** - {flow.description}")
        return "\n".join(descriptions)
    
    def get_flow_guidance_text(self) -> str:
        """Get formatted guidance text for all flows."""
        guidance_sections = []
        for flow in self.flows:
            guidance_sections.append(flow.get_guidance_text())
        return "\n---\n\n".join(guidance_sections)
    
    def generate_system_prompt(self) -> str:
        """Generate the complete system prompt from flows."""
        welcome_section = f"""Welcome! I'm your pharmacy assistant. I can help you with:

{self.get_flow_descriptions()}

How can I assist you today?

Important: I provide factual information from the pharmacy database only. I do not provide medical advice or diagnosis. For medical questions, please consult with your healthcare provider.

CRITICAL CONSTRAINT: You may only offer things that are in your tool kit and nothing else. Do not ask for information you cannot process or act upon (such as pickup/delivery preferences, contact method preferences, or insurance information). Only use your available tools to help users.

IMPORTANT: When reporting prescription verification results, ONLY report what the tools provide:
- Prescription status (active/expired) from verify_prescription
- Stock availability (in_stock/low_stock/out_of_stock) from check_medication_stock
- Prescription requirement status from get_medication_info (prescription_required field)

DO NOT suggest alternative purchasing methods (such as "available over the counter" or "can be purchased without a prescription") unless these are explicitly part of the pharmacy system's services. The system only tracks prescription status and stock availability - it does not offer alternative purchasing options.

## Flow Guidance

When helping users, follow these flow patterns:

{self.get_flow_guidance_text()}
"""
        return welcome_section


# Global instance
_flow_manager = FlowManager()


def get_flow_manager() -> FlowManager:
    """Get the global FlowManager instance."""
    return _flow_manager

