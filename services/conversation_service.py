"""
LifeBridge Conversation Service
Provides Python-based intent and entity extraction, slot filling,
dynamic follow-up generation, and grounded query response.
Operates deterministically without requiring an LLM API key, with
an optional LLM integration only if configured in the environment.
"""

import re
import os
from typing import Dict, Any, List, Tuple, Optional
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService
from services.eligibility_engine import MatchCategory


class ConversationService:
    def __init__(self):
        self.scheme_matcher = SchemeMatcher()
        self.hospital_service = HospitalService()

    def extract_entities(self, text: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts entities from user text and merges into user profile.
        Preserves previously extracted fields.
        """
        updated = dict(current_profile)
        lower = text.lower()

        # 1. State extraction
        if "karnataka" in lower:
            updated["state"] = "Karnataka"
        elif "delhi" in lower:
            updated["state"] = "Delhi"
        elif "tamil nadu" in lower or "chennai" in lower:
            updated["state"] = "Tamil Nadu"
        elif "maharashtra" in lower or "mumbai" in lower:
            updated["state"] = "Maharashtra"

        # 2. City / Locality extraction
        if any(c in lower for c in ["bengaluru", "bangalore", "blore"]):
            updated["city"] = "Bengaluru"
            if not updated.get("state"):
                updated["state"] = "Karnataka"
        elif "mysuru" in lower or "mysore" in lower:
            updated["city"] = "Mysuru"
            if not updated.get("state"):
                updated["state"] = "Karnataka"
        elif "hubballi" in lower or "hubli" in lower:
            updated["city"] = "Hubballi"
            if not updated.get("state"):
                updated["state"] = "Karnataka"
        elif "mangalore" in lower or "mangaluru" in lower:
            updated["city"] = "Mangaluru"
            if not updated.get("state"):
                updated["state"] = "Karnataka"

        # 3. Medical Condition / Treatment extraction
        if any(w in lower for w in ["cancer", "oncolog", "tumor", "chemotherapy", "radiation therapy", "carcinoma", "leukemia"]):
            updated["condition"] = "cancer"
        elif any(w in lower for w in ["heart", "cardiac", "bypass", "angioplasty", "valve", "cabg", "chest pain", "heart attack"]):
            updated["condition"] = "cardiac"
        elif any(w in lower for w in ["dialysis", "kidney", "renal", "creatinine", "esrd", "hemodialysis"]):
            updated["condition"] = "dialysis"
        elif any(w in lower for w in ["deliver", "pregnan", "matern", "c-section", "cesarean", "baby", "infant", "newborn"]):
            updated["condition"] = "maternal"
        elif any(w in lower for w in ["tb", "tuberculo", "nikshay", "dots"]):
            updated["condition"] = "tuberculosis"
        elif any(w in lower for w in ["rare disease", "genetic disorder", "sma", "gaucher", "spinal muscular"]):
            updated["condition"] = "rare disease"
        elif any(w in lower for w in ["surgery", "operation", "orthopedic", "knee replacement", "laparoscop"]):
            updated["condition"] = "surgery"

        # 4. Beneficiary / Ration Card extraction
        if any(w in lower for w in ["bpl", "phh", "anthyodaya", "aay", "below poverty"]):
            updated["ration_card_type"] = "BPL"
        elif any(w in lower for w in ["apl", "above poverty"]):
            updated["ration_card_type"] = "APL"
        elif any(w in lower for w in ["no ration card", "don't have a card", "without card", "no card"]):
            updated["ration_card_type"] = "None"

        # 5. Income extraction
        # Look for explicit numbers or terms
        if any(w in lower for w in ["low income", "income is low", "poor", "cannot afford", "can't afford", "indigent", "poverty", "financial distress"]):
            if not updated.get("annual_income") and not updated.get("ration_card_type"):
                updated["income_category"] = "low_income"
                if not updated.get("ration_card_type"):
                    updated["ration_card_type"] = "BPL"

        # Regex for amounts like "1.25 lakhs", "100000", "80,000", "50k", etc.
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
                if 5000 <= val <= 5000000:
                    updated["annual_income"] = val
            except (ValueError, TypeError):
                pass

        # 6. Cooperative Society extraction
        if any(w in lower for w in ["cooperative", "co-operative", "milk union", "pacs", "yeshasvini member", "farmer society"]):
            updated["has_cooperative_membership"] = True
        elif any(w in lower for w in ["not a member", "no cooperative", "not in cooperative"]):
            updated["has_cooperative_membership"] = False

        # 7. Treating Hospital Type
        if any(w in lower for w in ["government hospital", "govt hospital", "victoria", "bowring", "kc general", "nimhans", "kidwai"]):
            updated["treating_hospital_type"] = "government"
        elif any(w in lower for w in ["private hospital", "manipal", "narayana", "apollo", "private clinic"]):
            updated["treating_hospital_type"] = "private"

        return updated

    def get_dynamic_follow_up_questions(
        self,
        user_profile: Dict[str, Any],
        answered_questions: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Determines the next most helpful questions based on candidate schemes and missing profile items.
        Explains WHY each question is asked. Avoids repeating answered questions.
        """
        questions: List[Dict[str, Any]] = []

        # Question 1: Location (State / City)
        if not user_profile.get("state") and "location" not in answered_questions:
            questions.append({
                "id": "location",
                "question": "Which state and city do you live in?",
                "rationale": "State residency determines whether state-specific schemes (like Arogya Karnataka) or national schemes apply.",
                "options": ["Bengaluru, Karnataka", "Other Karnataka District", "Outside Karnataka"],
                "input_type": "choice_or_text"
            })

        # Question 2: Condition / Treatment
        if not user_profile.get("condition") and "condition" not in answered_questions:
            questions.append({
                "id": "condition",
                "question": "What medical condition or treatment are you seeking assistance for?",
                "rationale": "Government schemes cover specific medical procedures, surgeries, or critical illnesses.",
                "options": ["Cancer / Oncology", "Heart / Cardiac Surgery", "Kidney Dialysis / Renal Care", "Maternity / Child Care", "Other Surgery / Critical Illness"],
                "input_type": "choice_or_text"
            })

        # Question 3: Ration Card / Beneficiary Category
        if not user_profile.get("ration_card_type") and "ration_card" not in answered_questions:
            questions.append({
                "id": "ration_card",
                "question": "Do you hold a government ration card (BPL / PHH / AAY or APL)?",
                "rationale": "Schemes like Ayushman Bharat and Arogya Karnataka provide 100% cashless treatment for BPL/PHH holders, and co-payment or alternate assistance for APL holders.",
                "options": ["BPL / PHH / AAY Card", "APL Card", "No Ration Card / In Process"],
                "input_type": "choice"
            })

        # Question 4: Cooperative membership (if surgery or karnataka and relevant)
        condition = user_profile.get("condition", "")
        state = user_profile.get("state", "")
        if (condition in ["surgery", "cardiac"] or not condition) and state == "Karnataka":
            if user_profile.get("has_cooperative_membership") is None and "cooperative" not in answered_questions:
                questions.append({
                    "id": "cooperative",
                    "question": "Are you or your family members registered with a Karnataka cooperative society (e.g., dairy union, PACS, weavers)?",
                    "rationale": "Karnataka's Revamped Yeshasvini Scheme offers up to ₹5 Lakhs cashless surgical coverage exclusively for cooperative members.",
                    "options": ["Yes, Registered Member", "No / Not Applicable"],
                    "input_type": "choice"
                })

        # Question 5: Annual Income (if not already answered and BPL status unknown)
        if (not user_profile.get("annual_income") and
                user_profile.get("ration_card_type") not in ["BPL", "PHH", "AAY"] and
                "income" not in answered_questions):
            questions.append({
                "id": "income",
                "question": "What is your approximate annual family income?",
                "rationale": "Discretionary funds like Health Minister's Discretionary Grant require income below ₹1.25 Lakhs per year.",
                "options": ["Below ₹1,25,000", "₹1,25,000 to ₹2,50,000", "Above ₹2,50,000"],
                "input_type": "choice"
            })

        return questions

    def handle_user_query(
        self,
        message: str,
        user_profile: Dict[str, Any],
        active_scheme_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a grounded, empathetic response using deterministic rules and structured datasets.
        """
        lower = message.lower().strip()

        # Check for specific FAQ patterns
        # 1. "Why did you recommend this scheme?"
        if any(w in lower for w in ["why did you recommend", "why this scheme", "reason for recommendation", "why recommend"]):
            target_scheme = active_scheme_id
            if not target_scheme:
                matches = self.scheme_matcher.get_actionable_matches(user_profile)
                if matches:
                    target_scheme = matches[0].scheme.get("scheme_id")

            if target_scheme:
                scheme = self.scheme_matcher.get_scheme_by_id(target_scheme)
                eval_res = self.scheme_matcher.engine.evaluate_scheme(scheme, user_profile)
                reasons_text = "\n".join([f"- {r}" for r in eval_res.reasons]) or "- Relevant to your stated region and treatment needs."
                missing_text = "\n".join([f"- {m}" for m in eval_res.missing_information]) or "- None! Core basic criteria satisfied."
                return {
                    "text": (
                        f"**Why {scheme.get('scheme_name')} was recommended:**\n\n"
                        f"**Matching Factors:**\n{reasons_text}\n\n"
                        f"**Items Still Requiring Verification:**\n{missing_text}\n\n"
                        f"*Note: This is a rule-based preliminary screening to guide you to official resources, not an official approval.*"
                    ),
                    "action": "explain_scheme"
                }

        # 2. "Which documents should I prepare?"
        if any(w in lower for w in ["document", "docs", "what do i need", "papers required", "certificate"]):
            target_scheme = active_scheme_id
            if not target_scheme:
                matches = self.scheme_matcher.get_actionable_matches(user_profile)
                if matches:
                    target_scheme = matches[0].scheme.get("scheme_id")

            if target_scheme:
                scheme = self.scheme_matcher.get_scheme_by_id(target_scheme)
                docs = scheme.get("required_documents", [])
                docs_text = "\n".join([f"1. {d}" for d in docs])
                return {
                    "text": (
                        f"**Required Documents for {scheme.get('scheme_name')}:**\n\n"
                        f"{docs_text}\n\n"
                        f"**Important Tip:** Keep both original documents and 2-3 photocopies ready when visiting the hospital Arogya Mitra desk or government kiosk."
                    ),
                    "action": "show_documents"
                }

        # 3. "Where do I apply?"
        if any(w in lower for w in ["where do i apply", "how do i apply", "application procedure", "where to apply"]):
            target_scheme = active_scheme_id
            if not target_scheme:
                matches = self.scheme_matcher.get_actionable_matches(user_profile)
                if matches:
                    target_scheme = matches[0].scheme.get("scheme_id")

            if target_scheme:
                scheme = self.scheme_matcher.get_scheme_by_id(target_scheme)
                steps = scheme.get("application_steps", [])
                steps_text = "\n".join([f"{s}" for s in steps])
                method = scheme.get("application_method", "At designated hospital helpdesk")
                portal_url = scheme.get("official_application_url") or scheme.get("official_information_url")
                return {
                    "text": (
                        f"**Application Steps for {scheme.get('scheme_name')}:**\n\n"
                        f"**Primary Application Method:** {method}\n\n"
                        f"{steps_text}\n\n"
                        f"Official portal: [{portal_url}]({portal_url})"
                    ),
                    "action": "show_application_steps"
                }

        # 4. "Does this hospital accept the scheme?"
        if any(w in lower for w in ["accept", "participate", "empaneled", "tie-up", "tie up", "does hospital"]):
            hospitals = self.hospital_service.load_hospitals()
            # Check if user mentioned a specific hospital
            matched_hosp = None
            for h in hospitals:
                if any(k.lower() in lower for k in h.get("hospital_name", "").split() if len(k) > 3):
                    matched_hosp = h
                    break

            if matched_hosp:
                schemes_list = matched_hosp.get("participating_schemes", [])
                schemes_names = []
                for s_id in schemes_list:
                    s_obj = self.scheme_matcher.get_scheme_by_id(s_id)
                    schemes_names.append(s_obj.get("scheme_name", s_id) if s_obj else s_id)

                schemes_text = "\n".join([f"- {name}" for name in schemes_names]) if schemes_names else "- Specific scheme participation needs hospital verification."
                return {
                    "text": (
                        f"**Verified Schemes at {matched_hosp.get('hospital_name')}:**\n\n"
                        f"{schemes_text}\n\n"
                        f"**Contact Desk:** {matched_hosp.get('official_contact', 'N/A')}\n"
                        f"**Address:** {matched_hosp.get('address', 'N/A')}\n\n"
                        f"*Verification Note: Specialty coverage under the scheme is verified, but exact cashless package availability for your specific procedure requires confirmation at the hospital Arogya Mitra desk.*"
                    ),
                    "action": "hospital_scheme_info"
                }

        # General Assistant Guidance
        matches = self.scheme_matcher.get_actionable_matches(user_profile)
        top_matches = matches[:3]

        recs_summary = []
        for m in top_matches:
            recs_summary.append(f"• **{m.scheme.get('scheme_name')}**: {m.scheme.get('short_description')}")

        summary_text = "\n".join(recs_summary) if recs_summary else "We are screening schemes based on your information."

        return {
            "text": (
                f"Thank you. Based on the details provided, here are the most relevant government healthcare assistance options:\n\n"
                f"{summary_text}\n\n"
                f"You can review the cards below to see why each scheme matches, check any unconfirmed criteria, or explore verified network hospitals in Bengaluru."
            ),
            "action": "recommendations_updated"
        }
