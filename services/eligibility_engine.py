"""
LifeBridge Eligibility Matching Engine
Implements transparent, rule-based healthcare scheme screening.
Does not make official eligibility decisions. Distinguishes between:
- NO_KNOWN_CONFLICT
- POTENTIALLY_RELEVANT
- REQUIRES_OFFICIAL_VERIFICATION
- KNOWN_REQUIREMENT_NOT_MET
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class MatchCategory(str, Enum):
    NO_KNOWN_CONFLICT = "NO_KNOWN_CONFLICT"
    POTENTIALLY_RELEVANT = "POTENTIALLY_RELEVANT"
    REQUIRES_OFFICIAL_VERIFICATION = "REQUIRES_OFFICIAL_VERIFICATION"
    KNOWN_REQUIREMENT_NOT_MET = "KNOWN_REQUIREMENT_NOT_MET"


class EligibilityResult:
    def __init__(
        self,
        scheme: Dict[str, Any],
        match_category: MatchCategory,
        reasons: List[str],
        missing_information: List[str],
        unmet_criteria: List[str],
        official_verification_items: List[str],
        rank_score: int
    ):
        self.scheme = scheme
        self.match_category = match_category
        self.reasons = reasons
        self.missing_information = missing_information
        self.unmet_criteria = unmet_criteria
        self.official_verification_items = official_verification_items
        self.rank_score = rank_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scheme_id": self.scheme.get("scheme_id", "UNKNOWN"),
            "scheme_name": self.scheme.get("scheme_name", "Unknown Scheme"),
            "match_category": self.match_category.value,
            "reasons": self.reasons,
            "missing_information": self.missing_information,
            "unmet_criteria": self.unmet_criteria,
            "official_verification_items": self.official_verification_items,
            "rank_score": self.rank_score
        }


class EligibilityEngine:
    """
    Transparent, rule-based screening engine comparing a user profile against structured scheme rules.
    """

    @staticmethod
    def normalize_condition(condition: Optional[str]) -> str:
        if not condition:
            return ""
        c = condition.lower()
        import re
        if re.search(r'\b(cancer|tumor|chemo|radiation|oncolog|carcinoma|leukemia)\b', c):
            return "cancer"
        if re.search(r'\b(heart|cardiac|bypass|angio|valve|cabg|coronary)\b', c):
            return "cardiac"
        if re.search(r'\b(dialysis|kidney|renal|nephro|creatinine|esrd)\b', c):
            return "dialysis"
        if re.search(r'\b(deliver|pregnan|matern|c-section|cesarean|newborn|infant)\b', c):
            return "maternal"
        if re.search(r'\b(tb|tuberculo|nikshay|dots)\b', c):
            return "tuberculosis"
        if re.search(r'\b(rare disease|rare genetic|sma|gaucher|metabolic disorder)\b', c):
            return "rare disease"
        if re.search(r'\b(surger|operat|laparo|ortho|trauma)\b', c):
            return "surgery"
        return c

    def evaluate_scheme(self, scheme: Dict[str, Any], user_profile: Dict[str, Any]) -> EligibilityResult:
        """
        Evaluate a single scheme against user profile details.
        Handles missing fields gracefully.
        """
        reasons: List[str] = []
        missing_info: List[str] = []
        unmet_criteria: List[str] = []
        verification_items: List[str] = []

        rules = scheme.get("eligibility_rules", {})
        if not isinstance(rules, dict):
            rules = {}

        # 1. Geographic Check
        supported_states = rules.get("supported_states", ["All"])
        user_state = user_profile.get("state")
        
        if user_state:
            norm_user_state = user_state.strip().title()
            if "All" in supported_states or any(s.lower() == norm_user_state.lower() for s in supported_states):
                reasons.append(f"Geographic coverage: Scheme supports residents in {norm_user_state}.")
            else:
                unmet_criteria.append(
                    f"Geographic limitation: Scheme is restricted to {', '.join(supported_states)}, but user is in {norm_user_state}."
                )
        else:
            missing_info.append("Your home state is not specified to verify location eligibility.")

        # 2. Medical Condition / Treatment Check
        supported_conditions = rules.get("supported_conditions", [])
        user_condition = user_profile.get("condition")
        normalized_user_condition = self.normalize_condition(user_condition)

        if normalized_user_condition:
            match_found = False
            for cond in supported_conditions:
                if cond.lower() in normalized_user_condition or normalized_user_condition in cond.lower():
                    match_found = True
                    break
            
            # Also check if general surgery or general tertiary is supported
            if not match_found and ("general" in supported_conditions or "surgery" in supported_conditions):
                if any(w in normalized_user_condition for w in ["surgery", "general", "treatment", "illness", "care"]):
                    match_found = True

            if match_found:
                reasons.append(f"Medical relevance: Supports treatment related to '{user_condition or normalized_user_condition}'.")
            else:
                # If scheme has specific condition mandate and does not support general/other treatments
                scheme_id = scheme.get("scheme_id", "")
                if scheme_id in ["SCHEME-NPRD", "SCHEME-NPY", "SCHEME-JSSK", "SCHEME-PMNDP"]:
                    unmet_criteria.append(
                        f"Medical scope restriction: Scheme is specifically restricted to {', '.join(supported_conditions)}, which does not match '{user_condition}'."
                    )
                elif supported_conditions and "general" not in supported_conditions:
                    missing_info.append(
                        f"Scheme specifically targets: {', '.join(supported_conditions)}. Verification needed if your diagnosis qualifies."
                    )
        else:
            missing_info.append("Medical diagnosis or required treatment has not been specified.")

        # 3. Income / BPL Card Checks
        income_limit = rules.get("income_limit_annual")
        user_income = user_profile.get("annual_income")
        user_card_type = user_profile.get("ration_card_type")  # e.g., 'BPL', 'APL', 'PHH', 'AAY', 'None'
        is_bpl_or_card = rules.get("requires_bpl_or_card", False)

        if income_limit is not None:
            if user_income is not None:
                try:
                    income_val = float(user_income)
                    if income_val <= income_limit:
                        reasons.append(
                            f"Income criterion: Reported annual income (₹{income_val:,.0f}) is within the scheme ceiling of ₹{income_limit:,.0f}."
                        )
                    else:
                        unmet_criteria.append(
                            f"Income ceiling exceeded: Reported annual income (₹{income_val:,.0f}) exceeds maximum threshold of ₹{income_limit:,.0f}."
                        )
                except (ValueError, TypeError):
                    missing_info.append("Annual income format could not be parsed numerically; official income certificate required.")
            else:
                missing_info.append(f"Scheme requires annual family income below ₹{income_limit:,.0f}; current income is unconfirmed.")
        
        if is_bpl_or_card:
            if user_card_type:
                card_upper = str(user_card_type).upper()
                if any(k in card_upper for k in ["BPL", "PHH", "AAY", "POVERTY", "LOW_INCOME"]):
                    reasons.append(f"Beneficiary category: Confirmed qualifying ration card category ({card_upper}).")
                elif card_upper == "APL":
                    # For schemes that strictly require BPL (like PMNDP or RAN)
                    if scheme.get("scheme_id") in ["SCHEME-RAN", "SCHEME-PMNDP"]:
                        unmet_criteria.append(
                            "Scheme free benefit strictly requires a BPL/PHH ration card. APL cardholders are not eligible for 100% cashless waiver."
                        )
                    else:
                        missing_info.append("Requires verification: May have restricted or co-pay benefits for APL cards.")
                elif card_upper in ["NONE", "NO"]:
                    unmet_criteria.append("Requires BPL or recognized ration card, but user indicated having no ration card.")
            else:
                missing_info.append("Ration card category (BPL / PHH / AAY) is unconfirmed.")

        # 4. Specific Scheme Requirements
        # A. Cooperative Membership (Yeshasvini)
        if rules.get("requires_cooperative_membership", False):
            has_coop = user_profile.get("has_cooperative_membership")
            if has_coop is True or str(has_coop).lower() in ["true", "yes"]:
                reasons.append("Cooperative society membership confirmed.")
            elif has_coop is False or str(has_coop).lower() in ["false", "no"]:
                unmet_criteria.append("Requires active membership in a Karnataka cooperative society.")
            else:
                missing_info.append("Cooperative society membership status is unconfirmed.")

        # B. TB Notification (Nikshay)
        if rules.get("requires_tb_notification", False):
            is_tb_notified = user_profile.get("is_tb_notified")
            if is_tb_notified is True or str(is_tb_notified).lower() in ["true", "yes"]:
                reasons.append("Tuberculosis case notification in Nikshay confirmed.")
            elif is_tb_notified is False or str(is_tb_notified).lower() in ["false", "no"]:
                missing_info.append("Requires notification in Nikshay portal by treating doctor or public clinic.")
            else:
                missing_info.append("Nikshay portal TB registration status needs verification.")

        # C. Rare Disease Certification (NPRD)
        if rules.get("requires_rare_disease", False):
            if normalized_user_condition != "rare disease":
                missing_info.append("Requires documented clinical diagnosis of a recognized rare genetic/metabolic disorder.")
            else:
                reasons.append("Diagnostic indication matches Rare Disease assistance framework.")

        # D. Government Hospital Admission Requirement (RAN, HMDG)
        if rules.get("requires_govt_hospital_admission", False):
            treating_hospital_type = user_profile.get("treating_hospital_type")
            if treating_hospital_type:
                if "govt" in treating_hospital_type.lower() or "public" in treating_hospital_type.lower() or "autonomous" in treating_hospital_type.lower():
                    reasons.append("Receiving care at a recognized public/autonomous tertiary government hospital.")
                elif "private" in treating_hospital_type.lower():
                    unmet_criteria.append("Scheme strictly funds treatment in designated government apex hospitals; private hospital care is excluded.")
            else:
                verification_items.append("Treatment must be undertaken at an empaneled government super-specialty institute.")

        # 5. Determine Match Category and Rank Score
        if unmet_criteria:
            category = MatchCategory.KNOWN_REQUIREMENT_NOT_MET
            rank_score = 0
        elif not reasons and missing_info:
            category = MatchCategory.REQUIRES_OFFICIAL_VERIFICATION
            rank_score = 10
        elif missing_info:
            category = MatchCategory.POTENTIALLY_RELEVANT
            # Score based on how many positive matches were found
            rank_score = 40 + (len(reasons) * 15)
        else:
            category = MatchCategory.NO_KNOWN_CONFLICT
            rank_score = 80 + (len(reasons) * 10)

        # Standard verification items for all schemes
        verification_items.append("Final eligibility determination and benefit authorization must be verified at hospital Arogya Mitra desk.")
        verification_items.append("Active card / Aadhaar biometric authentication required at admission.")

        return EligibilityResult(
            scheme=scheme,
            match_category=category,
            reasons=reasons,
            missing_information=missing_info,
            unmet_criteria=unmet_criteria,
            official_verification_items=verification_items,
            rank_score=rank_score
        )
