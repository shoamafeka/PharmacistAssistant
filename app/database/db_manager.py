"""
Database manager for loading and querying JSON data files.
Handles loading users and medications from JSON files.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages database operations for users and medications."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the database manager.
        
        Args:
            data_dir: Directory containing data files. Defaults to app/database/data/
        """
        if data_dir is None:
            # Get the directory where this file is located
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self._users_cache = None
        self._medications_cache = None
    
    def load_users(self) -> List[Dict]:
        """
        Load users data from JSON file.
        
        Returns:
            List of user dictionaries
        """
        if self._users_cache is None:
            users_file = self.data_dir / "users.json"
            with open(users_file, "r", encoding="utf-8") as f:
                self._users_cache = json.load(f)
        return self._users_cache
    
    def load_medications(self) -> List[Dict]:
        """
        Load medications data from JSON file.
        
        Returns:
            List of medication dictionaries
        """
        if self._medications_cache is None:
            medications_file = self.data_dir / "medications.json"
            with open(medications_file, "r", encoding="utf-8") as f:
                self._medications_cache = json.load(f)
        return self._medications_cache
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get a user by customer ID.
        
        Args:
            user_id: Customer ID to look up
            
        Returns:
            User dictionary if found, None otherwise
        """
        users = self.load_users()
        return next((u for u in users if u["customer_id"] == user_id), None)
    
    def get_medication_by_name(self, medication_name: str, exact: bool = False) -> Optional[Dict]:
        """
        Get a medication by name (supports partial matching).
        
        Args:
            medication_name: Name of the medication
            exact: If True, only exact matches. If False, supports partial matching.
            
        Returns:
            Medication dictionary if found, None otherwise
        """
        medications = self.load_medications()
        medication_name_lower = medication_name.lower().strip()
        
        if exact:
            return next(
                (m for m in medications if m["medication_name"].lower() == medication_name_lower),
                None
            )
        else:
            # Try exact match first
            medication = next(
                (m for m in medications if m["medication_name"].lower() == medication_name_lower),
                None
            )
            
            # Try partial match if exact match fails
            if not medication:
                medication = next(
                    (m for m in medications if medication_name_lower in m["medication_name"].lower()),
                    None
                )
            
            return medication
    
    def clear_cache(self):
        """Clear the cached data (useful for testing or reloading data)."""
        self._users_cache = None
        self._medications_cache = None

