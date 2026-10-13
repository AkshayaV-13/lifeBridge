"""
LifeBridge Education Module Page
Helps students and families discover Indian scholarships, school admissions,
fee assistance, and entrance examination procedures.
"""

import streamlit as st
from components.navigation import render_header, render_footer
from services.education_service import EducationService, EducationMatchResult


def render_education_page():
    render_header()

    # Session State Initialization
    if "edu_profile" not in st.session_state:
        st.session_state.edu_profile = {}
    if "edu_active_guide" not in st.session_state:
        st.session_state.edu_active_guide = None

    edu_service = EducationService()

    # If user selected an application guide
    if st.session_state.edu_active_guide:
        _render_education_guide_view(st.session_state.edu_active_guide, edu_service)
        render_footer()
        return

    # Title & Subtitle
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='color: #0f172a; margin-bottom: 0.2rem;'>🎓 Education & Scholarship Discovery</h2>
            <p style='color: #475569; font-size: 1.05rem;'>
                Discover government scholarships, free residential school admissions (JNVST), 
                fee reimbursement, and official entrance examination procedures (NEET, JEE) without knowing scheme names in advance.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Quick Demonstration Scenarios
    st.markdown("**💡 Quick Demonstration Scenarios (Click to test):**")
    d_c1, d_c2, d_c3, d_c4 = st.columns(4)

    with d_c1:
        if st.button("🏫 Class 6 Residential School", use_container_width=True, key="demo_edu_jnv"):
            st.session_state.edu_profile = {
                "education_level": "School Education",
                "current_class": "Class 5",
                "assistance_type": "Government & Residential Schools",
                "target_exam": "JNVST",
                "state": "Karnataka"
            }
            st.rerun()

    with d_c2:
        if st.button("💰 Class 10 Girl Scholarship", use_container_width=True, key="demo_edu_nmms"):
            st.session_state.edu_profile = {
                "education_level": "School Education",
                "current_class": "Class 10",
                "gender": "Female",
                "assistance_type": "Scholarships",
                "family_income": 180000,
                "state": "Karnataka"
            }
            st.rerun()

    with d_c3:
        if st.button("💻 BTech College Scholarship", use_container_width=True, key="demo_edu_btech"):
            st.session_state.edu_profile = {
                "education_level": "Undergraduate",
                "current_class": "Undergraduate (BTech)",
                "course": "Engineering / BTech",
                "assistance_type": "Scholarships",
                "family_income": 250000,
                "state": "Karnataka"
            }
            st.rerun()

    with d_c4:
        if st.button("🩺 NEET-UG Medical Exam", use_container_width=True, key="demo_edu_neet"):
            st.session_state.edu_profile = {
                "education_level": "Pre-University Passed",
                "current_class": "Class 12",
                "assistance_type": "Entrance Examinations",
                "target_exam": "NEET-UG",
                "course": "Medicine / MBBS"
            }
            st.rerun()

    st.markdown("---")

    # 2. Main Interface: Input Form & Filters
    col_input, col_results = st.columns([1, 2])

    with col_input:
        with st.container(border=True):
            st.markdown("#### 🎯 Student Profile")
            st.caption("Tell us what kind of educational assistance you need:")

            cat_options = [
                "All Categories",
                "Scholarships",
                "Fee Assistance",
                "Government & Residential Schools",
                "Entrance Examinations",
                "Free or Subsidised Education"
            ]
            current_cat = st.session_state.edu_profile.get("assistance_type", "All Categories")
            cat_idx = cat_options.index(current_cat) if current_cat in cat_options else 0

            selected_cat = st.selectbox(
                "Type of Assistance Needed:",
                cat_options,
                index=cat_idx,
                key="edu_cat_select"
            )

            # Natural text search box
            user_text_input = st.text_input(
                "Or describe your situation in words:",
                placeholder="e.g. studying Class 6 need residential school, or BTech student",
                key="edu_text_input"
            )

            if user_text_input:
                extracted = edu_service.extract_education_entities(
                    user_text_input,
                    st.session_state.edu_profile
                )
                st.session_state.edu_profile.update(extracted)

            st.markdown("---")
            st.markdown("##### Detailed Parameters")

            # Progressive inputs
            grade_opts = [
                "Not Specified",
                "LKG / Class 1",
                "Class 5",
                "Class 6",
                "Class 8",
                "Class 10",
                "Class 11",
                "Class 12",
                "Undergraduate (BTech)",
                "Undergraduate (General Degree)",
                "Postgraduate"
            ]
            curr_grade = st.session_state.edu_profile.get("current_class", "Not Specified")
            grade_idx = grade_opts.index(curr_grade) if curr_grade in grade_opts else 0

            sel_grade = st.selectbox("Current Class / Level:", grade_opts, index=grade_idx)
            if sel_grade != "Not Specified":
                st.session_state.edu_profile["current_class"] = sel_grade

            state_opts = ["All / Pan-India", "Karnataka", "Delhi", "Other State"]
            curr_state = st.session_state.edu_profile.get("state", "Karnataka")
            state_idx = state_opts.index(curr_state) if curr_state in state_opts else 1
            sel_state = st.selectbox("Home State:", state_opts, index=state_idx)
            st.session_state.edu_profile["state"] = sel_state

            inc_opts = ["Not Specified", "Below ₹1,20,000", "₹1,20,000 - ₹3,50,000", "₹3,50,000 - ₹8,00,000", "Above ₹8,00,000"]
            sel_inc = st.selectbox("Approx. Annual Family Income:", inc_opts)
            if sel_inc == "Below ₹1,20,000":
                st.session_state.edu_profile["family_income"] = 100000
            elif sel_inc == "₹1,20,000 - ₹3,50,000":
                st.session_state.edu_profile["family_income"] = 250000
            elif sel_inc == "₹3,50,000 - ₹8,00,000":
                st.session_state.edu_profile["family_income"] = 500000
            elif sel_inc == "Above ₹8,00,000":
                st.session_state.edu_profile["family_income"] = 900000

            if selected_cat != "All Categories":
                st.session_state.edu_profile["assistance_type"] = selected_cat

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Apply Filters 🔍", type="primary", use_container_width=True):
                    st.rerun()
            with c_btn2:
                if st.button("Reset Profile 🔄", use_container_width=True):
                    st.session_state.edu_profile = {}
                    st.rerun()

    # 3. Results Section
    with col_results:
        results = edu_service.match_schemes(st.session_state.edu_profile)
        actionable = [r for r in results if r.score > 0 and r.status_label == "Potential Match"]
        unmet = [r for r in results if r.status_label == "Not a Match — Mandatory Requirement Not Met"]

        st.markdown(f"### 📋 Recommended Opportunities ({len(actionable)} Found)")

        if not actionable:
            st.warning(
                "No active opportunities matched all your specified parameters. "
                "The current LifeBridge prototype dataset includes 10 verified core programmes. "
                "You can check broader national opportunities on the official **[National Scholarship Portal](https://scholarships.gov.in)** "
                "or the **[NTA Examinations Portal](https://nta.ac.in)**."
            )
        else:
            for r in actionable:
                _render_single_education_card(r)

        if unmet:
            with st.expander(f"⚠️ View Opportunities Not Matching Your Profile ({len(unmet)})"):
                for r in unmet:
                    _render_single_education_card(r, is_unmet=True)

    render_footer()


def _render_single_education_card(result: EducationMatchResult, is_unmet: bool = False):
    scheme = result.scheme
    sid = scheme.get("scheme_id")
    name = scheme.get("name")
    ptype = scheme.get("programme_type")
    desc = scheme.get("description")
    benefits = scheme.get("benefits")
    v_status = scheme.get("verification_status")
    v_date = scheme.get("last_verified_date")

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"#### {name}")
            st.markdown(
                f"<span style='background-color:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700;'>{ptype}</span>",
                unsafe_allow_html=True
            )
        with c2:
            if not is_unmet:
                st.markdown(
                    "<div style='background-color:#dcfce7; color:#166534; padding:5px 10px; border-radius:15px; font-size:0.78rem; font-weight:700; text-align:center;'>Potential Match</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='background-color:#fee2e2; color:#991b1b; padding:5px 10px; border-radius:15px; font-size:0.78rem; font-weight:700; text-align:center;'>Requirement Unmet</div>",
                    unsafe_allow_html=True
                )
            st.caption(f"Status: **{v_status}** ({v_date})")

        st.markdown(f"*{desc}*")

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**🎓 Main Assistance / Benefits:**")
            st.write(benefits)
            st.markdown("**📍 Geographical Coverage:**")
            st.write(", ".join(scheme.get("eligible_states", ["All"])))

            if result.reasons:
                st.markdown("**✅ Why This May Match Your Profile:**")
                for r in result.reasons:
                    st.markdown(f"- {r}")

        with col_r:
            st.markdown("**📌 Key Eligibility Criteria:**")
            st.write(f"• Income: {scheme.get('income_criteria')}")
            st.write(f"• Academic: {scheme.get('academic_requirements')}")

            if result.unmet_criteria:
                st.markdown("**❌ Mandatory Disqualifying Factor:**")
                for u in result.unmet_criteria:
                    st.markdown(f"- <span style='color:#dc2626;'>{u}</span>", unsafe_allow_html=True)

            if result.missing_information:
                st.markdown("**❓ Information Requiring Verification:**")
                for m in result.missing_information:
                    st.markdown(f"- <span style='color:#b45309;'>{m}</span>", unsafe_allow_html=True)

        st.markdown("---")
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button("📋 Open Step-by-Step Application Guide", key=f"guide_btn_{sid}", type="primary", use_container_width=True):
                st.session_state.edu_active_guide = sid
                st.rerun()
        with btn_c2:
            if scheme.get("official_application_url"):
                st.link_button("📝 Open Official Application Portal", scheme["official_application_url"], use_container_width=True)


def _render_education_guide_view(scheme_id: str, edu_service: EducationService):
    scheme = edu_service.get_scheme_by_id(scheme_id)
    if not scheme:
        st.error("Programme details could not be found.")
        if st.button("⬅️ Back to Opportunities"):
            st.session_state.edu_active_guide = None
            st.rerun()
        return

    c_back, c_title = st.columns([1, 4])
    with c_back:
        if st.button("⬅️ Back to Education List", type="secondary", use_container_width=True):
            st.session_state.edu_active_guide = None
            st.rerun()

    with c_title:
        st.markdown(f"### 📋 Step-by-Step Educational Application Guide")
        st.markdown(f"#### {scheme.get('name')}")

    st.info(
        f"**Programme Type:** {scheme.get('programme_type')} • "
        f"**Cycle Status:** {scheme.get('application_cycle_or_year')} • "
        f"**Verification:** {scheme.get('verification_status')} ({scheme.get('last_verified_date')})"
    )

    t1, t2, t3, t4 = st.tabs([
        "1. Eligibility & Cycle Check",
        "2. Required Documents Checklist",
        "3. Application Walkthrough",
        "4. Official Portals & Helpline"
    ])

    with t1:
        st.markdown("#### 🎯 Eligibility Guidelines")
        st.write(f"• **Target Classes/Grades:** {', '.join(scheme.get('applicable_classes', []))}")
        st.write(f"• **Eligible Courses/Streams:** {', '.join(scheme.get('eligible_courses', []))}")
        st.write(f"• **Income Ceilings:** {scheme.get('income_criteria')}")
        st.write(f"• **Category Requirements:** {scheme.get('category_requirements')}")
        st.write(f"• **Academic Merit:** {scheme.get('academic_requirements')}")

        st.markdown("---")
        st.markdown("#### ⏳ Admission / Application Dates")
        st.warning(
            f"**Application Window:** {scheme.get('application_start_date')}\n\n"
            f"**Application Deadline:** {scheme.get('application_deadline')}\n\n"
            "*Notice: Application windows open and close per annual academic cycles. Always verify current cycle status on the official portal.*"
        )

    with t2:
        st.markdown("#### 📑 Required Documents Checklist")
        st.caption("Keep digital scanned copies (PDF/JPG) and original physical documents ready:")
        for idx, doc in enumerate(scheme.get("documents_required", []), 1):
            st.checkbox(f"**{idx}. {doc}**", key=f"edu_doc_{scheme_id}_{idx}")

    with t3:
        st.markdown("#### 🚶 Step-by-Step Application Instructions")
        for step in scheme.get("application_steps", []):
            st.markdown(f"- {step}")

        st.markdown("---")
        st.markdown("#### 🛡️ Post-Submission & Merit List Verification")
        st.write(
            "1. Save and print your Application Confirmation Page and Registration / Roll Number.\n"
            "2. Note your Application Reference Number for school/institute e-attestation.\n"
            "3. Track merit list publication or admit card release exclusively on the official department portal."
        )

    with t4:
        st.markdown("#### 🌐 Official Application Links")
        if scheme.get("official_application_url"):
            st.link_button("📝 Open Official Application Portal", scheme["official_application_url"], use_container_width=True)

        st.caption(f"📞 Official Authority Helpline: **{scheme.get('official_contact', 'N/A')}**")


if __name__ == "__main__":
    st.set_page_config(page_title="LifeBridge - Education", page_icon="🎓", layout="wide")
    render_education_page()
