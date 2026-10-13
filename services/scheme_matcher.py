"""
LifeBridge Scheme Matcher Service
Loads healthcare scheme records and evaluates them against user profile criteria.
"""

import json
import os
from typing import List, Dict, Any, Optional
from services.eligibility_engine import EligibilityEngine, EligibilityResult, MatchCategory


class SchemeMatcher:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "healthcare_schemes.json")
        self.data_path = data_path
        self.engine = EligibilityEngine()
        self._schemes_cache: Optional[List[Dict[str, Any]]] = None

    def load_schemes(self) -> List[Dict[str, Any]]:
        """
        Loads schemes from JSON safely, handling missing or corrupt files.
        """
        if self._schemes_cache is not None:
            return self._schemes_cache

        if not os.path.exists(self.data_path):
            return []

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._schemes_cache = data
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        schemes = self.load_schemes()
        for s in schemes:
            if s.get("scheme_id") == scheme_id:
                return s
        return None

    def match_schemes(self, user_profile: Dict[str, Any]) -> List[EligibilityResult]:
        """
        Evaluates and ranks all available schemes for the user.
        """
        schemes = self.load_schemes()
        results: List[EligibilityResult] = []

        for s in schemes:
            res = self.engine.evaluate_scheme(s, user_profile)
            results.append(res)

        # Sort by rank score descending
        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results

    def get_actionable_matches(self, user_profile: Dict[str, Any]) -> List[EligibilityResult]:
        """
        Returns matches that are potentially relevant or have no known conflict.
        """
        all_results = self.match_schemes(user_profile)
        return [
            r for r in all_results
            if r.match_category in [
                MatchCategory.NO_KNOWN_CONFLICT,
                MatchCategory.POTENTIALLY_RELEVANT,
                MatchCategory.REQUIRES_OFFICIAL_VERIFICATION
            ]
        ]
