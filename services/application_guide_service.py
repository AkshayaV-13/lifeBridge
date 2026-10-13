"""
LifeBridge Personalized Application Guide Service
Generates an evidence-based, 12-section step-by-step application guide
customized to the user's known and missing profile factors.
"""

from typing import Dict, Any, List, Optional
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService
from services.eligibility_engine import EligibilityEngine


class ApplicationGuideService:
    def __init__(self):
        self.scheme_matcher = SchemeMatcher()
        self.hospital_service = HospitalService()
        self.engine = EligibilityEngine()

    def generate_guide(self, scheme_id: str, user_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        scheme = self.scheme_matcher.get_scheme_by_id(scheme_id)
        if not scheme:
            return None

        eval_result = self.engine.evaluate_scheme(scheme, user_profile)

        # Find verified empaneled hospitals for this scheme
        empaneled_hospitals = self.hospital_service.search_hospitals(
            city=user_profile.get("city", "Bengaluru"),
            scheme_id=scheme_id
        )

        # 1. Why Relevant
        relevance_points = eval_result.reasons
        if not relevance_points:
            relevance_points = [
                f"Supports medical treatments and procedures in {scheme.get('geographical_coverage', 'India')}."
            ]

        # 2. Known Eligibility Factors
        known_factors = []
        if user_profile.get("state"):
            known_factors.append(f"Residency / Location: {user_profile['state']} ({user_profile.get('city', 'Specified')})")
        if user_profile.get("condition"):
            known_factors.append(f"Condition / Treatment Needed: {user_profile['condition'].title()}")
        if user_profile.get("ration_card_type"):
            known_factors.append(f"Ration Card Category: {user_profile['ration_card_type']}")
        if user_profile.get("annual_income"):
            known_factors.append(f"Reported Annual Income: ₹{user_profile['annual_income']:,.0f}")
        if user_profile.get("has_cooperative_membership") is not None:
            status = "Yes, Active Member" if user_profile["has_cooperative_membership"] else "No"
            known_factors.append(f"Cooperative Society Membership: {status}")

        if not known_factors:
            known_factors = ["General inquiry; detailed profile parameters pending."]

        # 3. Missing Eligibility Information
        missing_factors = eval_result.missing_information
        if not missing_factors:
            missing_factors = ["No critical preliminary profile fields are missing."]

        # 4. Requirements needing official confirmation
        official_confirmations = [
            "Biometric e-KYC authentication matching Aadhaar and state beneficiary database.",
            "Active inclusion in government beneficiary lists (NFSA / SECC / SAST / Nikshay).",
            "Medical case summary and pre-authorization sign-off by empaneled hospital treating specialist."
        ]

        # 5. Documents Checklist
        required_docs = scheme.get("required_documents", [
            "Aadhaar Card",
            "Ration Card / Income Certificate",
            "Doctor's Prescription and Medical Estimate"
        ])

        # 6. Where to apply
        application_venue = scheme.get(
            "application_method",
            "Arogya Mitra Helpdesk at empaneled government or network hospital."
        )

        # 7. Step-by-Step Instructions
        steps = scheme.get("application_steps", [
            "Visit the hospital helpdesk with your identity and medical records.",
            "Complete biometric e-KYC authentication.",
            "Submit clinical case documents for pre-authorization."
        ])

        # 8. Official Links
        official_links = {
            "information_url": scheme.get("official_information_url"),
            "application_url": scheme.get("official_application_url"),
            "helpline": scheme.get("official_helpline", "104")
        }

        # 9. Hospital assistance desk info
        hospital_info_list = []
        for h in empaneled_hospitals[:5]:
            hospital_info_list.append({
                "hospital_name": h.get("hospital_name"),
                "hospital_type": h.get("hospital_type"),
                "address": h.get("address"),
                "contact": h.get("official_contact"),
                "website": h.get("official_website")
            })

        # 10. Application Tracking
        tracking_info = (
            f"You can track pre-authorization progress through the SMS reference number issued by the hospital Arogya Mitra, "
            f"or via the official beneficiary portal ({scheme.get('official_application_url') or scheme.get('official_information_url')})."
        )

        # 11. Post-approval procedure
        post_approval = (
            "Once pre-authorization is approved by the trust/nodal agency, your treatment package is locked as cashless. "
            "Ensure you receive an acknowledgment receipt and do not pay any unauthorized out-of-pocket charges for covered items."
        )

        # 12. Grievance / Delays
        grievance_procedure = (
            f"If your application is delayed or you face issues, immediately contact the hospital Medical Social Worker (MSW), "
            f"call the official helpline ({scheme.get('official_helpline', '104')}), or register a complaint on the state grievance portal (e.g., SAST or CPGRAMS)."
        )

        return {
            "scheme_id": scheme.get("scheme_id"),
            "scheme_name": scheme.get("scheme_name"),
            "purpose": scheme.get("purpose"),
            "benefits": scheme.get("benefits"),
            "limitations": scheme.get("limitations_and_exclusions"),
            "verification_status": scheme.get("verification_status"),
            "last_verified_date": scheme.get("last_verified_date"),
            "relevance_points": relevance_points,
            "known_factors": known_factors,
            "missing_factors": missing_factors,
            "official_confirmations": official_confirmations,
            "required_docs": required_docs,
            "application_venue": application_venue,
            "steps": steps,
            "official_links": official_links,
            "empaneled_hospitals": hospital_info_list,
            "tracking_info": tracking_info,
            "post_approval": post_approval,
            "grievance_procedure": grievance_procedure
        }
