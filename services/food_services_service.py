"""
LifeBridge Food & Essential Services Service
Handles rule-based matching for ration-card services, BPL entitlements,
food portability (ONORC), and verified nearby government service centres.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional


class FoodServiceMatchResult:
    def __init__(
        self,
        service: Dict[str, Any],
        status_label: str,
        reasons: List[str],
        missing_information: List[str],
        unmet_criteria: List[str],
        score: int
    ):
        self.service = service
        self.status_label = status_label
        self.reasons = reasons
        self.missing_information = missing_information
        self.unmet_criteria = unmet_criteria
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service.get("service_id"),
            "name": self.service.get("name"),
            "status_label": self.status_label,
            "reasons": self.reasons,
            "missing_information": self.missing_information,
            "unmet_criteria": self.unmet_criteria,
            "score": self.score
        }


class FoodServicesService:
    def __init__(
        self,
        services_data_path: Optional[str] = None,
        centres_data_path: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if services_data_path is None:
            services_data_path = os.path.join(base_dir, "data", "food_services.json")
        if centres_data_path is None:
            centres_data_path = os.path.join(base_dir, "data", "food_service_centres.json")
        
        self.services_data_path = services_data_path
        self.centres_data_path = centres_data_path
        self._services_cache: Optional[List[Dict[str, Any]]] = None
        self._centres_cache: Optional[List[Dict[str, Any]]] = None

    def load_services(self) -> List[Dict[str, Any]]:
        if self._services_cache is not None:
            return self._services_cache
        if not os.path.exists(self.services_data_path):
            return []
        try:
            with open(self.services_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._services_cache = data
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def load_centres(self) -> List[Dict[str, Any]]:
        if self._centres_cache is not None:
            return self._centres_cache
        if not os.path.exists(self.centres_data_path):
            return []
        try:
            with open(self.centres_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._centres_cache = data
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        for s in self.load_services():
            if s.get("service_id") == service_id:
                return s
        return None

    def extract_food_entities(self, text: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts user intent, ration card ownership, and location from natural language text.
        """
        updated = dict(current_profile)
        lower = text.lower()

        # 1. Primary Need / Intent
        if any(w in lower for w in ["apply for a bpl", "apply for bpl", "apply for a ration card", "new ration card", "apply for new card", "get a ration card", "how can my family get a ration card"]):
            updated["service_category"] = "Apply for New Ration Card"
            updated["has_existing_card"] = False
        elif any(w in lower for w in ["portability", "move to another state", "moving to another", "migrant", "interstate", "other state"]):
            updated["service_category"] = "Check Portability (One Nation One Ration Card)"
            updated["has_existing_card"] = True
        elif any(w in lower for w in ["update", "correct", "add member", "delete member", "change address", "modification"]):
            updated["service_category"] = "Update or Correct Ration Card Details"
            updated["has_existing_card"] = True
        elif any(w in lower for w in ["receive ration", "entitlement", "how much rice", "how much ration", "anna bhagya", "free grain", "food entitlement"]):
            updated["service_category"] = "Food & Ration Entitlements"
        elif any(w in lower for w in ["bpl eligibility", "qualify for bpl", "bpl criteria", "bpl rules"]):
            updated["service_category"] = "BPL Eligibility & Benefit Information"
        elif any(w in lower for w in ["service centre", "ration office", "fps locator", "ration shop", "where is the nearest", "near me"]):
            updated["service_category"] = "Find Nearby Service Centre / Ration Shop"
        elif any(w in lower for w in ["status", "track", "application number"]):
            updated["service_category"] = "Track Application Status"

        # 2. Existing Card Status
        if any(w in lower for w in ["i have a ration card", "existing card", "already have", "already got a card"]):
            updated["has_existing_card"] = True
        elif any(w in lower for w in ["don't have a card", "no ration card", "first time", "new family"]):
            updated["has_existing_card"] = False

        # 3. State
        if "karnataka" in lower or "bengaluru" in lower or "bangalore" in lower:
            updated["state"] = "Karnataka"
        elif "delhi" in lower:
            updated["state"] = "Delhi"
        elif "tamil nadu" in lower:
            updated["state"] = "Tamil Nadu"

        # 4. Locality
        for loc in ["jayanagar", "malleshwaram", "indiranagar", "btm", "rajajinagar", "shivajinagar", "yelahanka", "kr puram"]:
            if loc in lower:
                updated["locality"] = loc.title()
                break

        return updated

    def evaluate_service(self, service: Dict[str, Any], profile: Dict[str, Any]) -> FoodServiceMatchResult:
        """
        Evaluates a single food service record against user profile answers.
        Minimizes user friction and gives clear rationale.
        """
        reasons: List[str] = []
        missing_info: List[str] = []
        unmet_criteria: List[str] = []
        score = 0

        sid = service.get("service_id", "")
        coverage = service.get("geographical_coverage", "")
        rec_type = service.get("record_type", "")

        user_cat = profile.get("service_category", "")
        user_state = profile.get("state", "")
        has_card = profile.get("has_existing_card")

        # 1. State / Geography Check
        is_karnataka_specific = "karnataka" in coverage.lower() and "pan-india" not in coverage.lower()
        if is_karnataka_specific:
            if user_state:
                if user_state.lower() == "karnataka":
                    reasons.append(f"State jurisdiction: Service is administered by Karnataka Food & Civil Supplies.")
                    score += 20
                else:
                    unmet_criteria.append(f"State limitation: Service is exclusively for Karnataka residents; you indicated {user_state}.")
            else:
                missing_info.append("Karnataka residency must be confirmed before accessing state-specific services.")
                score += 5
        else:
            reasons.append("National coverage: Available across all Indian States & UTs under NFSA guidelines.")
            score += 15

        # 2. Category Intent Matching
        if user_cat == "Apply for New Ration Card":
            if sid == "FOOD-KA-NEW-RC":
                reasons.append("Exact match: Official Karnataka online portal for new Priority (BPL) and APL ration cards.")
                score += 60
            elif sid in ["FOOD-NFSA-PHH", "FOOD-AAY"]:
                reasons.append("Relevant entitlement: Explains the foodgrain allocation granted upon card approval.")
                score += 30
            elif sid in ["FOOD-ONORC", "FOOD-KA-UPDATE-RC"]:
                unmet_criteria.append("Not applicable: This service is for existing cardholders seeking modification or portability.")

        elif user_cat == "Check Portability (One Nation One Ration Card)":
            if sid == "FOOD-ONORC":
                reasons.append("Exact match: Nationwide ONORC scheme allows lifting ration across any state in India.")
                score += 70
            elif sid == "FOOD-MERA-RATION":
                reasons.append("Official companion app: Check portability status and find nearest biometric e-PoS shop.")
                score += 40
            elif sid == "FOOD-KA-NEW-RC":
                unmet_criteria.append("Not applicable: Portability utilizes your existing ration card; new card application is unnecessary.")

        elif user_cat == "Food & Ration Entitlements":
            if sid in ["FOOD-KA-ANNA-BHAGYA", "FOOD-PMGKAY", "FOOD-NFSA-PHH", "FOOD-AAY"]:
                reasons.append("Entitlement match: Details monthly foodgrain quantities and direct cash benefit transfers.")
                score += 50
            elif sid == "FOOD-KA-NEW-RC":
                # Don't force user into new application when they just asked about entitlements
                score -= 10

        elif user_cat == "Update or Correct Ration Card Details":
            if sid == "FOOD-KA-UPDATE-RC":
                reasons.append("Exact match: Official service for family member addition, deletion, and address change.")
                score += 60
            elif sid == "FOOD-RC-STATUS-KA":
                reasons.append("Tracking service: Monitor Food Inspector review of modification requests.")
                score += 30
            elif sid == "FOOD-KA-NEW-RC":
                unmet_criteria.append("Not applicable: Existing cardholders should use the modification service instead of a new application.")

        elif user_cat == "Find Nearby Service Centre / Ration Shop":
            if sid in ["FOOD-KA-FPS-LOCATOR", "FOOD-MERA-RATION"]:
                reasons.append("Service directory match: Find authorized Fair Price Shops and government food supply offices.")
                score += 60

        elif user_cat == "Track Application Status":
            if sid == "FOOD-RC-STATUS-KA":
                reasons.append("Exact match: Real-time tracking of new ration card or modification applications.")
                score += 70

        elif user_cat == "BPL Eligibility & Benefit Information":
            if sid in ["FOOD-NFSA-PHH", "FOOD-AAY", "FOOD-KA-ANNA-BHAGYA"]:
                reasons.append("Eligibility guidance: Outlines BPL income criteria and household exclusion rules.")
                score += 50

        # General Card Ownership Consistency Check
        if has_card is True:
            if sid == "FOOD-KA-NEW-RC":
                if user_cat != "Apply for New Ration Card":
                    unmet_criteria.append("You already hold an active ration card; duplicate new card applications are disallowed.")
        elif has_card is False:
            if sid in ["FOOD-KA-UPDATE-RC", "FOOD-ONORC"]:
                missing_info.append("Active ration card required to utilize member modification or portability services.")

        # Outcome Classification
        if unmet_criteria:
            status_label = "Not a Match — Mandatory Requirement Not Met"
            score = 0
        elif not reasons and missing_info:
            status_label = "Service Information Needs Verification"
            score = 10
        elif reasons and not missing_info:
            status_label = "Potential Match"
            score += 25
        else:
            status_label = "Potential Match"
            score += 15

        return FoodServiceMatchResult(
            service=service,
            status_label=status_label,
            reasons=reasons,
            missing_information=missing_info,
            unmet_criteria=unmet_criteria,
            score=score
        )

    def match_services(self, profile: Dict[str, Any]) -> List[FoodServiceMatchResult]:
        services = self.load_services()
        results: List[FoodServiceMatchResult] = []

        for s in services:
            res = self.evaluate_service(s, profile)
            results.append(res)

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def get_actionable_matches(self, profile: Dict[str, Any]) -> List[FoodServiceMatchResult]:
        all_res = self.match_services(profile)
        return [r for r in all_res if r.status_label == "Potential Match" and r.score > 0]

    def search_nearby_centres(
        self,
        locality: Optional[str] = None,
        centre_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters verified service centres in Bengaluru.
        Does not fabricate locations if query is outside verified records.
        """
        centres = self.load_centres()
        results: List[Dict[str, Any]] = []

        norm_loc = locality.lower().strip() if locality else None
        norm_type = centre_type.lower().strip() if centre_type else None

        for c in centres:
            # 1. Type filter
            if norm_type and norm_type != "all":
                c_type = str(c.get("centre_type", "")).lower()
                if norm_type not in c_type:
                    continue

            # 2. Locality filter
            if norm_loc:
                all_text = f"{c.get('name', '')} {c.get('address', '')} {c.get('district', '')}".lower()
                if norm_loc not in all_text and "bengaluru" not in norm_loc and "bangalore" not in norm_loc:
                    continue

            results.append(c)

        return results
