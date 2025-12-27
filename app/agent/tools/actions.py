"""
Tool action functions for the Pharmacist Agent.
Each function implements a specific capability for prescription management,
medication information retrieval, and inventory control.
"""

from datetime import datetime
from typing import Dict, List, Any
from app.database.db_manager import DatabaseManager
from app.agent.tools.decorator import tool


# Initialize database manager
_db_manager = DatabaseManager()


# Computed fields logic
def _compute_prescription_status(prescribed_date: str, expiry_date: str, is_one_time: bool) -> str:
    """
    Compute prescription status based on dates.
    Returns: 'active', 'expired', or 'completed'
    """
    today = datetime.now().date()
    prescribed = datetime.strptime(prescribed_date, "%Y-%m-%d").date()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    
    if today > expiry:
        return "expired"
    elif today >= prescribed:
        return "active"
    else:
        return "active"  # Future prescriptions are considered active


def _compute_stock_status(stock_quantity: int, threshold: int = 10) -> str:
    """
    Compute stock status based on quantity.
    Returns: 'in_stock', 'low_stock', or 'out_of_stock'
    """
    if stock_quantity == 0:
        return "out_of_stock"
    elif stock_quantity < threshold:
        return "low_stock"
    else:
        return "in_stock"


# Tool Functions

@tool
def get_user_prescriptions(user_id: str) -> Dict[str, Any]:
    """
    Retrieve all prescriptions for a user by customer ID. Supports prescription management workflows.
    
    Args:
        user_id: Customer ID to look up
    """
    try:
        if not user_id or not isinstance(user_id, str):
            return {
                "success": False,
                "error": "Invalid user ID format"
            }
        
        user = _db_manager.get_user_by_id(user_id.upper())
        
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Compute status for each prescription
        prescriptions_with_status = []
        for rx in user.get("prescriptions", []):
            rx_copy = rx.copy()
            rx_copy["status"] = _compute_prescription_status(
                rx["prescribed_date"],
                rx["expiry_date"],
                rx["is_one_time"]
            )
            prescriptions_with_status.append(rx_copy)
        
        return {
            "success": True,
            "user": {
                "customer_id": user["customer_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "prescriptions": prescriptions_with_status
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving prescriptions: {str(e)}"
        }


@tool
def get_medication_info(medication_name: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive medication information including active ingredients, usage instructions, and prescription requirements. Supports customer service and usage guidance workflows. Supports partial/fuzzy matching by case-insensitive search.
    
    Args:
        medication_name: Name of the medication (supports partial/fuzzy matching)
    """
    try:
        if not medication_name or not isinstance(medication_name, str):
            return {
                "success": False,
                "error": "Invalid medication name"
            }
        
        medication = _db_manager.get_medication_by_name(medication_name, exact=False)
        
        if not medication:
            return {
                "success": False,
                "error": "Medication not found"
            }
        
        # Compute stock status
        stock_status = _compute_stock_status(medication["stock_quantity"])
        
        return {
            "success": True,
            "medication": {
                "medication_name": medication["medication_name"],
                "strength": medication["strength"],
                "generic_name": medication["generic_name"],
                "active_ingredients": medication["active_ingredients"],
                "dosage_forms": medication["dosage_forms"],
                "prescription_required": medication["prescription_required"],
                "usage_instructions": medication["usage_instructions"],
                "common_side_effects": medication.get("common_side_effects", []),
                "storage_instructions": medication.get("storage_instructions", "")
            },
            "stock_info": {
                "stock_quantity": medication["stock_quantity"],
                "stock_status": stock_status
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving medication info: {str(e)}"
        }


@tool
def check_medication_stock(medication_names: List[str]) -> Dict[str, Any]:
    """
    Check stock availability for one or more medications. Supports inventory control workflows.
    
    Args:
        medication_names: List of medication names to check
    """
    try:
        if not medication_names or not isinstance(medication_names, list) or len(medication_names) == 0:
            return {
                "success": False,
                "error": "No medications specified"
            }
        
        stock_results = []
        
        for med_name in medication_names:
            if not isinstance(med_name, str):
                continue
                
            medication = _db_manager.get_medication_by_name(med_name, exact=False)
            
            if medication:
                stock_status = _compute_stock_status(medication["stock_quantity"])
                stock_results.append({
                    "medication_name": medication["medication_name"],
                    "stock_quantity": medication["stock_quantity"],
                    "stock_status": stock_status,
                    "available": stock_status != "out_of_stock"
                })
            else:
                stock_results.append({
                    "medication_name": med_name,
                    "stock_quantity": 0,
                    "stock_status": "not_found",
                    "available": False
                })
        
        return {
            "success": True,
            "stock_results": stock_results
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking stock: {str(e)}"
        }


@tool
def verify_prescription(user_id: str, prescription_id: str) -> Dict[str, Any]:
    """
    Verify a specific prescription's validity and status. Supports prescription verification workflows.
    
    Args:
        user_id: Customer ID
        prescription_id: Prescription ID to verify
    """
    try:
        if not user_id or not isinstance(user_id, str):
            return {
                "success": False,
                "error": "Invalid user ID format"
            }
        
        if not prescription_id or not isinstance(prescription_id, str):
            return {
                "success": False,
                "error": "Invalid prescription ID format"
            }
        
        user = _db_manager.get_user_by_id(user_id.upper())
        
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        prescription = next(
            (rx for rx in user.get("prescriptions", []) if rx["prescription_id"] == prescription_id),
            None
        )
        
        if not prescription:
            return {
                "success": False,
                "error": "Prescription not found for this user"
            }
        
        # Compute status
        status = _compute_prescription_status(
            prescription["prescribed_date"],
            prescription["expiry_date"],
            prescription["is_one_time"]
        )
        
        is_valid = status == "active"
        
        prescription_result = prescription.copy()
        prescription_result["status"] = status
        prescription_result["is_valid"] = is_valid
        
        return {
            "success": True,
            "prescription": prescription_result
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error verifying prescription: {str(e)}"
        }

