"""
LifeBridge Application Guide Component
Renders the complete 12-section personalized application guide for a selected scheme.
"""

import streamlit as st
from typing import Dict, Any, Callable
from services.application_guide_service import ApplicationGuideService


def render_application_guide(
    scheme_id: str,
    user_profile: Dict[str, Any],
    on_back: Callable[[], None]
):
    guide_service = ApplicationGuideService()
    guide = guide_service.generate_guide(scheme_id, user_profile)

    if not guide:
        st.error(f"Application guide for scheme ID '{scheme_id}' could not be generated.")
        if st.button("⬅️ Return to Recommendations", type="primary"):
            on_back()
        return

    # Header with Back button
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back to Schemes", use_container_width=True):
            on_back()

    with col_title:
        st.markdown(f"### 📋 Personalized Application Guide")
        st.markdown(f"#### {guide['scheme_name']}")

    st.info(
        f"**Scheme Purpose:** {guide['purpose']}\n\n"
        f"**Official Verification Status:** {guide['verification_status']} (Verified {guide['last_verified_date']})"
    )

    # 12 Sections organized into clean readable cards / tabs
    g_tab1, g_tab2, g_tab3, g_tab4 = st.tabs([
        "1. Eligibility & Missing Details",
        "2. Required Documents Checklist",
        "3. Step-by-Step Application Steps",
        "4. Hospitals, Tracking & Grievance"
    ])

    with g_tab1:
        st.markdown("#### 🎯 Why This Scheme May Be Relevant")
        for point in guide["relevance_points"]:
            st.markdown(f"- ✅ **{point}**")

        st.markdown("---")
        col_known, col_missing = st.columns([1, 1])

        with col_known:
            st.markdown("#### 👤 Your Known Eligibility Details")
            for factor in guide["known_factors"]:
                st.markdown(f"- {factor}")

        with col_missing:
            st.markdown("#### ❓ Missing Information Needing Verification")
            for factor in guide["missing_factors"]:
                st.markdown(f"- <span style='color:#b45309;'>{factor}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🏛️ Statutory Requirements Requiring Official Confirmation")
        for conf in guide["official_confirmations"]:
            st.markdown(f"- 🔍 {conf}")

    with g_tab2:
        st.markdown("#### 📑 Required Documents Checklist")
        st.caption("Prepare these physical documents along with 2 photocopies before visiting the hospital or portal:")

        for i, doc in enumerate(guide["required_docs"], 1):
            st.checkbox(f"**{i}. {doc}**", key=f"doc_chk_{scheme_id}_{i}")

        st.markdown("---")
        st.markdown("#### ⚠️ Benefit Caps & Exclusions")
        st.write(guide["limitations"])

    with g_tab3:
        st.markdown("#### 🏢 Where to Apply")
        st.success(f"**Primary Venue / Desk:** {guide['application_venue']}")

        st.markdown("#### 🚶 Step-by-Step Instructions")
        for step in guide["steps"]:
            st.markdown(f"- {step}")

        st.markdown("---")
        st.markdown("#### 🌐 Official Application Links")
        if guide["official_links"]["application_url"]:
            st.link_button("📝 Open Official Application Portal", guide["official_links"]["application_url"], use_container_width=True)

        st.caption(f"📞 Verified Official Helpline: **{guide['official_links']['helpline']}**")

    with g_tab4:
        st.markdown("#### 🏥 Empaneled Hospitals with Arogya Mitra Desks (Bengaluru Area)")
        if not guide["empaneled_hospitals"]:
            st.info("Check hospital directory tab for empaneled network hospitals.")
        else:
            for h in guide["empaneled_hospitals"]:
                with st.expander(f"{h['hospital_name']} ({h['hospital_type']})"):
                    st.write(f"**Address:** {h['address']}")
                    st.write(f"**Helpdesk Contact:** {h['contact']}")
                    if h["website"]:
                        st.link_button("Visit Hospital Portal", h["website"])

        st.markdown("---")
        st.markdown("#### 📲 How to Track Your Application")
        st.write(guide["tracking_info"])

        st.markdown("#### 🛡️ Post-Approval Procedure (What Happens Next)")
        st.write(guide["post_approval"])

        st.markdown("#### 🚨 Delays, Rejections or Grievance Redressal")
        st.warning(guide["grievance_procedure"])

    st.markdown("---")
    if st.button("⬅️ Return to Scheme Recommendations", use_container_width=True, key="return_bottom_btn"):
        on_back()
