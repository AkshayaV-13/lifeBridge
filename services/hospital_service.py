"""
LifeBridge Hospital Service
Handles hospital directory querying, filtering, specialty matching, and distance estimation.
Distinguishes between location verification, specialty verification, and scheme participation.
"""

import json
import os
import math
from typing import List, Dict, Any, Optional


class HospitalService:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "hospitals.json")
        self.data_path = data_path
        self._hospitals_cache: Optional[List[Dict[str, Any]]] = None

    def load_hospitals(self) -> List[Dict[str, Any]]:
        if self._hospitals_cache is not None:
            return self._hospitals_cache

        if not os.path.exists(self.data_path):
            return []

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._hospitals_cache = data
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    @staticmethod
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine formula to compute great-circle distance between two points in km.
        """
        try:
            r = 6371.0  # Earth radius in kilometers
            d_lat = math.radians(lat2 - lat1)
            d_lon = math.radians(lon2 - lon1)
            a = (
                math.sin(d_lat / 2) ** 2
                + math.cos(math.radians(lat1))
                * math.cos(math.radians(lat2))
                * math.sin(d_lon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(r * c, 1)
        except (TypeError, ValueError):
            return -1.0

    def search_hospitals(
        self,
        city: Optional[str] = None,
        condition: Optional[str] = None,
        scheme_id: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters hospitals by city, condition/specialty, and scheme participation.
        Attaches calculated distance if user coordinates are provided.
        """
        hospitals = self.load_hospitals()
        results: List[Dict[str, Any]] = []

        norm_city = city.lower().strip() if city else None
        norm_cond = condition.lower().strip() if condition else None
        target_scheme = scheme_id.strip() if scheme_id else None

        for h in hospitals:
            # 1. City check
            if norm_city:
                h_city = str(h.get("city", "")).lower()
                h_dist = str(h.get("district", "")).lower()
                if norm_city not in h_city and norm_city not in h_dist and "bengaluru" not in norm_city and "bangalore" not in norm_city:
                    continue

            # 2. Scheme check
            participating_schemes = h.get("participating_schemes", [])
            is_scheme_matched = True
            if target_scheme:
                is_scheme_matched = target_scheme in participating_schemes

            # 3. Specialty / Condition check
            is_cond_matched = True
            if norm_cond:
                specialties = [str(s).lower() for s in h.get("specialties", [])]
                treatments = [str(t).lower() for s in h.get("treatments", []) for t in [s]]
                all_text = " ".join(specialties + treatments)

                # Keyword grouping
                cancer_terms = ["cancer", "oncolog", "tumor", "chemo"]
                cardiac_terms = ["heart", "cardiac", "angio", "bypass"]
                kidney_terms = ["kidney", "renal", "dialysis", "nephro"]
                maternal_terms = ["pregnan", "matern", "deliver", "baby", "infant", "child", "pediatric"]
                rare_terms = ["rare", "genetic"]
                tb_terms = ["tb", "tuberculo", "dots"]
                surgery_terms = ["surger", "operat", "laparo", "ortho"]

                if any(k in norm_cond for k in cancer_terms):
                    is_cond_matched = any(k in all_text for k in cancer_terms)
                elif any(k in norm_cond for k in cardiac_terms):
                    is_cond_matched = any(k in all_text for k in cardiac_terms)
                elif any(k in norm_cond for k in kidney_terms):
                    is_cond_matched = any(k in all_text for k in kidney_terms)
                elif any(k in norm_cond for k in maternal_terms):
                    is_cond_matched = any(k in all_text for k in maternal_terms)
                elif any(k in norm_cond for k in rare_terms):
                    is_cond_matched = any(k in all_text for k in rare_terms)
                elif any(k in norm_cond for k in tb_terms):
                    is_cond_matched = any(k in all_text for k in tb_terms)
                elif any(k in norm_cond for k in surgery_terms):
                    is_cond_matched = any(k in all_text for k in surgery_terms) or "surgery" in all_text
                else:
                    is_cond_matched = norm_cond in all_text

            # Copy record and enrich with distance & flags
            record = dict(h)
            record["matched_scheme"] = is_scheme_matched
            record["matched_condition"] = is_cond_matched

            # Calculate distance if coordinates exist
            h_lat = h.get("latitude")
            h_lon = h.get("longitude")
            if user_lat is not None and user_lon is not None and h_lat and h_lon:
                record["distance_km"] = self.calculate_distance_km(user_lat, user_lon, float(h_lat), float(h_lon))
            else:
                record["distance_km"] = None

            # Include if either scheme matches or condition matches (if filtered)
            if target_scheme and not is_scheme_matched:
                continue
            if norm_cond and not is_cond_matched:
                continue

            results.append(record)

        # Sort by distance if available, otherwise preserve order
        if user_lat is not None and user_lon is not None:
            results.sort(key=lambda r: (r["distance_km"] if r["distance_km"] is not None else 9999))

        return results

    def get_hospital_by_id(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        for h in self.load_hospitals():
            if h.get("hospital_id") == hospital_id:
                return h
        return None
