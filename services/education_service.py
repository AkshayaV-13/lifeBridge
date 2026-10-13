"""
LifeBridge Education Service
Implements rule-based matching, entity extraction, and application guidance
for Indian education schemes, scholarships, admissions, and entrance exams.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional


class EducationMatchResult:
    def __init__(
        self,
        scheme: Dict[str, Any],
        status_label: str,
        reasons: List[str],
        missing_information: List[str],
        unmet_criteria: List[str],
        score: int
    ):
        self.scheme = scheme
        self.status_label = status_label
        self.reasons = reasons
        self.missing_information = missing_information
        self.unmet_criteria = unmet_criteria
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scheme_id": self.scheme.get("scheme_id"),
            "name": self.scheme.get("name"),
            "status_label": self.status_label,
            "reasons": self.reasons,
            "missing_information": self.missing_information,
            "unmet_criteria": self.unmet_criteria,
            "score": self.score
        }


class EducationService:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "education_schemes.json")
        self.data_path = data_path
        self._cache: Optional[List[Dict[str, Any]]] = None

    def load_schemes(self) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache
        if not os.path.exists(self.data_path):
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._cache = data
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for s in self.load_schemes():
            if s.get("scheme_id") == scheme_id:
                return s
        return None

    def extract_education_entities(self, text: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts student level, course, exams, and financial circumstances from natural text.
        """
        updated = dict(current_profile)
        lower = text.lower()

        # 1. Assistance Type
        if any(w in lower for w in ["scholarship", "scholarships", "financial aid", "stipend"]):
            updated["assistance_type"] = "Scholarships"
        elif any(w in lower for w in ["fee", "fees", "fee assistance", "fee reimbursement", "tuition"]):
            updated["assistance_type"] = "Fee Assistance"
        elif any(w in lower for w in ["residential school", "navodaya", "jnv", "hostel school", "boarding"]):
            updated["assistance_type"] = "Government & Residential Schools"
        elif any(w in lower for w in ["exam", "entrance", "neet", "jee", "test", "nta"]):
            updated["assistance_type"] = "Entrance Examinations"
        elif any(w in lower for w in ["free education", "free school", "subsidised", "rte", "right to education"]):
            updated["assistance_type"] = "Free or Subsidised Education"

        # 2. Specific Exam Mentions
        if "neet" in lower:
            updated["target_exam"] = "NEET-UG"
            updated["course"] = "Medicine / MBBS"
            updated["assistance_type"] = "Entrance Examinations"
        elif "jee" in lower or "iit" in lower or "nit" in lower:
            updated["target_exam"] = "JEE (Main)"
            updated["course"] = "Engineering / BTech"
            updated["assistance_type"] = "Entrance Examinations"
        elif "navodaya" in lower or "jnvst" in lower:
            updated["target_exam"] = "JNVST"
            updated["assistance_type"] = "Government & Residential Schools"
        elif "nmms" in lower:
            updated["target_exam"] = "NMMS"
            updated["assistance_type"] = "Scholarships"

        # 3. Class / Educational Level
        # Class 6 or 5
        if re.search(r'\b(class\s*6|6th\s*class|grade\s*6|sixth\s*standard|6th\s*standard|std\s*6)\b', lower):
            updated["education_level"] = "School Education"
            updated["current_class"] = "Class 6"
        elif re.search(r'\b(class\s*5|5th\s*class|grade\s*5|fifth\s*standard|5th\s*standard|std\s*5)\b', lower):
            updated["education_level"] = "School Education"
            updated["current_class"] = "Class 5"
        # Class 8
        elif re.search(r'\b(class\s*8|8th\s*class|grade\s*8|eighth\s*standard|8th\s*standard|std\s*8)\b', lower):
            updated["education_level"] = "School Education"
            updated["current_class"] = "Class 8"
        # Class 10
        elif re.search(r'\b(class\s*10|10th\s*class|grade\s*10|tenth\s*standard|10th\s*standard|sslc|std\s*10)\b', lower):
            updated["education_level"] = "School Education"
            updated["current_class"] = "Class 10"
        # Class 11 / PUC 1
        elif re.search(r'\b(class\s*11|11th\s*class|grade\s*11|eleventh\s*standard|11th\s*standard|puc\s*1|first\s*puc)\b', lower):
            updated["education_level"] = "Pre-University"
            updated["current_class"] = "Class 11"
        # Class 12 / PUC 2
        elif re.search(r'\b(class\s*12|12th\s*class|grade\s*12|twelfth\s*standard|12th\s*standard|puc\s*2|second\s*puc|puc)\b', lower):
            updated["education_level"] = "Pre-University"
            updated["current_class"] = "Class 12"
        # LKG / Nursery / 1st
        elif re.search(r'\b(lkg|ukg|nursery|class\s*1|1st\s*standard)\b', lower):
            updated["education_level"] = "Early Childhood"
            updated["current_class"] = "LKG / Class 1"
        # College / BTech / UG
        elif any(w in lower for w in ["btech", "b.tech", "be", "b.e", "engineering"]):
            updated["education_level"] = "Undergraduate"
            updated["current_class"] = "Undergraduate (BTech)"
            updated["course"] = "Engineering / BTech"
        elif any(w in lower for w in ["mbbs", "bds", "medical student"]):
            updated["education_level"] = "Undergraduate"
            updated["current_class"] = "Undergraduate (MBBS)"
            updated["course"] = "Medicine / MBBS"
        elif any(w in lower for w in ["college", "degree", "undergraduate", "bcom", "bsc", "ba", "ug"]):
            updated["education_level"] = "Undergraduate"
            if not updated.get("current_class"):
                updated["current_class"] = "Undergraduate"
        elif any(w in lower for w in ["postgraduate", "mtech", "msc", "mba", "pg"]):
            updated["education_level"] = "Postgraduate"
            updated["current_class"] = "Postgraduate"

        # 4. State
        if "karnataka" in lower:
            updated["state"] = "Karnataka"
        elif "delhi" in lower:
            updated["state"] = "Delhi"
        elif "tamil nadu" in lower:
            updated["state"] = "Tamil Nadu"

        # 5. Gender (Relevant for AICTE Pragati)
        if any(w in lower for w in ["daughter", "girl", "female", "woman", "sister"]):
            updated["gender"] = "Female"
        elif any(w in lower for w in ["son", "boy", "male", "brother"]):
            updated["gender"] = "Male"

        # 6. Income
        if any(w in lower for w in ["low income", "poor", "cannot afford", "bpl", "financial difficulty", "need help paying"]):
            if not updated.get("family_income"):
                updated["income_category"] = "low_income"

        income_match = re.search(r'(?:rs\.?|inr|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(lakh|lac|k)?', lower)
        if income_match:
            try:
                raw_num = income_match.group(1).replace(",", "")
                unit = income_match.group(2)
                val = float(raw_num)
                if unit in ["lakh", "lac"]:
                    val = val * 100000
                elif unit == "k":
                    val = val * 1000
                if 10000 <= val <= 10000000:
                    updated["family_income"] = val
            except (ValueError, TypeError):
                pass

        return updated

    def evaluate_scheme(self, scheme: Dict[str, Any], profile: Dict[str, Any]) -> EducationMatchResult:
        """
        Evaluates a single education record against student profile answers.
        """
        reasons: List[str] = []
        missing_info: List[str] = []
        unmet_criteria: List[str] = []
        score = 0

        prog_type = scheme.get("programme_type", "")
        req_classes = scheme.get("applicable_classes", [])
        req_levels = scheme.get("education_levels", [])
        eligible_states = scheme.get("eligible_states", ["All"])

        student_class = profile.get("current_class", "")
        student_level = profile.get("education_level", "")
        student_course = profile.get("course", "")
        student_state = profile.get("state", "")
        student_income = profile.get("family_income")
        student_gender = profile.get("gender")
        target_exam = profile.get("target_exam")
        assistance_type = profile.get("assistance_type")

        # 1. State / Geography Check
        if student_state:
            if "All" in eligible_states or any(s.lower() == student_state.lower() for s in eligible_states):
                reasons.append(f"State coverage: Scheme supports students residing in {student_state}.")
                score += 15
            else:
                unmet_criteria.append(
                    f"Geographic limitation: Scheme is restricted to {', '.join(eligible_states)}, but user is in {student_state}."
                )
        else:
            if "All" not in eligible_states:
                missing_info.append(f"State eligibility requires confirmation (restricted to: {', '.join(eligible_states)}).")

        # 2. Programme / Exam Specific Matching
        # If student specifically asked for an exam (e.g. NEET), heavily boost matching exam and exclude unrelated scholarships
        if target_exam:
            scheme_id = scheme.get("scheme_id", "")
            if target_exam == "NEET-UG" and scheme_id == "EDU-NEET-UG":
                reasons.append("Exact examination match: Official NEET-UG admission and application information.")
                score += 60
            elif target_exam == "JEE (Main)" and scheme_id == "EDU-JEE-MAIN":
                reasons.append("Exact examination match: Official JEE (Main) admission and application information.")
                score += 60
            elif target_exam == "JNVST" and scheme_id == "EDU-JNVST-CL6":
                reasons.append("Exact school entrance match: Jawahar Navodaya Vidyalaya Selection Test.")
                score += 60
            elif target_exam == "NMMS" and scheme_id == "EDU-NMMS":
                reasons.append("Exact scholarship examination match: National Means-cum-Merit Scholarship.")
                score += 60
            elif prog_type == "Entrance Examination":
                # Different entrance exam requested
                unmet_criteria.append(f"Examination mismatch: You requested {target_exam}, but this record is for {scheme.get('name')}.")
            elif assistance_type == "Entrance Examinations":
                # Student specifically wanted an entrance exam, but this is a regular scholarship/school
                unmet_criteria.append(f"Request type mismatch: You requested entrance examination guidance, but this is a {prog_type.lower()}.")

        # 3. Class and Educational Level Matching
        # Strict rule: Class 11 student should NOT receive Class 6 admission
        # Class 6 student should NOT receive college/undergraduate scholarship
        class_conflict = False

        if student_class:
            # Check for Class 6 / Navodaya specific restriction
            if "Class 6" in student_class or "Class 5" in student_class:
                if scheme.get("scheme_id") == "EDU-JNVST-CL6":
                    reasons.append("Applicable grade: Perfectly matches Class 5/6 Navodaya residential admission criteria.")
                    score += 40
                elif any("Undergraduate" in l or "Postgraduate" in l for l in req_levels):
                    class_conflict = True
                    unmet_criteria.append(f"Level mismatch: Programme is for college/undergraduate study, but student is in {student_class}.")
                elif "Class 11" in str(req_classes) or "Class 12" in str(req_classes):
                    class_conflict = True
                    unmet_criteria.append(f"Grade mismatch: For higher secondary classes, not applicable to {student_class}.")
            
            elif "Class 11" in student_class or "Class 12" in student_class:
                if scheme.get("scheme_id") == "EDU-JNVST-CL6":
                    class_conflict = True
                    unmet_criteria.append("Grade mismatch: Navodaya JNVST Class 6 admission is strictly for Class 5 students entering Class 6.")
                elif scheme.get("scheme_id") == "EDU-RTE-KA":
                    class_conflict = True
                    unmet_criteria.append("Grade mismatch: RTE Section 12(1)(c) admission is strictly for entry-level LKG and Class 1.")
                elif any(c in str(req_classes) for c in ["Class 11", "Class 12", "PUC"]):
                    reasons.append(f"Applicable grade: Supports students in {student_class} (Pre-University / Higher Secondary).")
                    score += 35
                elif any("Undergraduate" in l for l in req_levels) and "Class 12" in student_class:
                    reasons.append(f"Transition match: Students completing {student_class} can prepare for this undergraduate opportunity.")
                    score += 20

            elif "Undergraduate" in student_level or "BTech" in student_class or "Degree" in student_class:
                if any(s in scheme.get("scheme_id", "") for s in ["EDU-JNVST-CL6", "EDU-NMMS", "EDU-RTE-KA"]):
                    class_conflict = True
                    unmet_criteria.append(f"Grade mismatch: School-level programme not applicable for undergraduate/college students.")
                elif any("Undergraduate" in l for l in req_levels):
                    reasons.append("Applicable education level: Specifically supports undergraduate and professional degree students.")
                    score += 40
                elif any("Pre-University" in l for l in req_levels):
                    # Some post-matric schemes support both PUC and Degree (e.g. SSP Karnataka, Vidyasiri)
                    if "Undergraduate" in str(req_levels):
                        reasons.append("Education level: Supports university degree courses under post-matric guidelines.")
                        score += 35

            elif "LKG" in student_class:
                if scheme.get("scheme_id") == "EDU-RTE-KA":
                    reasons.append("Applicable age & grade: Matches entry-level LKG/Class 1 free school admission.")
                    score += 50
                else:
                    class_conflict = True
                    unmet_criteria.append("Grade mismatch: This programme is for older primary/secondary/higher education students.")

            else:
                # General class matching
                if any(student_class.lower() in str(c).lower() for c in req_classes):
                    reasons.append(f"Class match: Programme supports {student_class}.")
                    score += 25
                else:
                    missing_info.append(f"Check if current grade ({student_class}) meets applicable levels ({', '.join(req_classes[:3])}).")

        else:
            missing_info.append("Current class or educational level not specified to confirm admission/scholarship eligibility.")

        # 4. Gender Check (for AICTE Pragati)
        if scheme.get("scheme_id") == "EDU-AICTE-PRAGATI":
            if student_gender == "Female":
                reasons.append("Beneficiary requirement: Pragati scholarship specifically supports girl students in technical education.")
                score += 20
            elif student_gender == "Male":
                unmet_criteria.append("Category requirement: AICTE Pragati scholarship is strictly reserved for female students.")

        # 5. Income Criteria Check
        scheme_id = scheme.get("scheme_id", "")
        if student_income is not None:
            if scheme_id == "EDU-NMMS" and student_income > 350000:
                unmet_criteria.append(f"Income ceiling exceeded: Reported income (₹{student_income:,.0f}) exceeds ₹3,50,000 NMMS limit.")
            elif scheme_id == "EDU-PM-USP-CSSS" and student_income > 450000:
                unmet_criteria.append(f"Income ceiling exceeded: Reported income (₹{student_income:,.0f}) exceeds ₹4,50,000 CSSS limit.")
            elif scheme_id == "EDU-AICTE-PRAGATI" and student_income > 800000:
                unmet_criteria.append(f"Income ceiling exceeded: Reported income (₹{student_income:,.0f}) exceeds ₹8,00,000 Pragati limit.")
            elif scheme_id == "EDU-RTE-KA" and student_income > 350000:
                unmet_criteria.append(f"Income ceiling exceeded: EWS category requires annual family income under ₹3,50,000.")
            else:
                reasons.append("Reported income satisfies preliminary scheme income requirements.")
                score += 10
        else:
            if "income" in scheme.get("income_criteria", "").lower() and "no income ceiling" not in scheme.get("income_criteria", "").lower():
                missing_info.append("Annual family income certificate required to confirm financial eligibility.")

        # 6. Cycle and Deadline Verification
        # As per Section 5 & 15: An expired or unverified deadline is NOT presented as current
        deadline_note = "Current application cycle status & deadlines must be verified on the official portal."
        missing_info.append(deadline_note)

        # 7. Outcome Classification
        if unmet_criteria:
            status_label = "Not a Match — Mandatory Requirement Not Met"
            score = 0
        elif not reasons and missing_info:
            status_label = "Programme Information Needs Verification"
            score = 10
        elif missing_info and reasons:
            status_label = "Potential Match"
            score += 20
        else:
            status_label = "Potential Match"

        return EducationMatchResult(
            scheme=scheme,
            status_label=status_label,
            reasons=reasons,
            missing_information=missing_info,
            unmet_criteria=unmet_criteria,
            score=score
        )

    def match_schemes(self, student_profile: Dict[str, Any]) -> List[EducationMatchResult]:
        schemes = self.load_schemes()
        results: List[EducationMatchResult] = []

        for s in schemes:
            res = self.evaluate_scheme(s, student_profile)
            results.append(res)

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def get_actionable_matches(self, student_profile: Dict[str, Any]) -> List[EducationMatchResult]:
        all_res = self.match_schemes(student_profile)
        return [r for r in all_res if r.status_label in ["Potential Match", "More Information Needed", "Programme Information Needs Verification"] and r.score > 0]
