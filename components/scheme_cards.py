"""
LifeBridge Scheme Recommendation Cards Component
Renders clear, transparent scheme cards with status badges, match rationales,
unconfirmed criteria checklists, and application guide navigation.
"""

import streamlit as st
from typing import List, Dict, Any, Callable
from services.eligibility_engine import EligibilityResult, MatchCategory


def render_scheme_cards(
    results: List[EligibilityResult],
    on_select_guide: Callable[[str], None]
):
    """
    Renders list of scheme results categorized by match status.
    """
    if not results:
        st.info(
            "No schemes currently match the specified filters. Try expanding your search criteria or resetting filters."
        )
        return

    # Categorize results
    no_conflict = [r for r in results if r.match_category == MatchCategory.NO_KNOWN_CONFLICT]
    potential = [r for r in results if r.match_category == MatchCategory.POTENTIALLY_RELEVANT]
    requires_verif = [r for r in results if r.match_category == MatchCategory.REQUIRES_OFFICIAL_VERIFICATION]
    unmet = [r for r in results if r.match_category == MatchCategory.KNOWN_REQUIREMENT_NOT_MET]

    # Tabs for organized viewing
    tab1, tab2, tab3 = st.tabs([
        f"🎯 Potential & Eligible Matches ({len(no_conflict) + len(potential)})",
        f"🔍 Requires Further Verification ({len(requires_verif)})",
        f"⚠️ Confirmed Ineligible / Excluded ({len(unmet)})"
    ])

    with tab1:
        if not no_conflict and not potential:
            st.warning(
                "No schemes fully matched your current profile without missing information. "
                "Check the 'Requires Verification' tab or provide more details in the chat above."
            )
        else:
            for r in no_conflict + potential:
                _render_single_scheme_card(r, on_select_guide)

    with tab2:
        if not requires_verif:
            st.info("No schemes currently in pending verification state.")
        else:
            st.caption("These schemes may apply, but additional profile details are needed to assess potential relevance.")
            for r in requires_verif:
                _render_single_scheme_card(r, on_select_guide)

    with tab3:
        if not unmet:
            st.info("No schemes have been ruled out based on your current profile.")
        else:
            st.caption("The following schemes have a confirmed mandatory requirement that is not satisfied based on your answers:")
            for r in unmet:
                _render_single_scheme_card(r, on_select_guide)


def _render_single_scheme_card(result: EligibilityResult, on_select_guide: Callable[[str], None]):
    scheme = result.scheme
    scheme_id = scheme.get("scheme_id", "UNKNOWN")
    scheme_name = scheme.get("scheme_name", "Unknown Scheme")

    # Category badge styling
    badge_map = {
        MatchCategory.NO_KNOWN_CONFLICT: ("🟢 No Known Conflict", "#dcfce7", "#166534"),
        MatchCategory.POTENTIALLY_RELEVANT: ("🟡 Potential Match (Info Needed)", "#fef9c3", "#854d0e"),
        MatchCategory.REQUIRES_OFFICIAL_VERIFICATION: ("🔵 Official Verification Required", "#dbeafe", "#1e40af"),
        MatchCategory.KNOWN_REQUIREMENT_NOT_MET: ("⚪ Mandatory Requirement Not Met", "#f1f5f9", "#475569")
    }

    badge_label, bg_col, text_col = badge_map.get(
        result.match_category,
        ("ℹ️ Screening in Progress", "#f1f5f9", "#334155")
    )

    with st.container(border=True):
        # Card Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {scheme_name}")
            st.markdown(f"*{scheme.get('short_description', '')}*")
        with col2:
            st.markdown(
                f"<div style='background-color:{bg_col}; color:{text_col}; padding:6px 12px; "
                f"border-radius:20px; font-weight:700; font-size:0.8rem; text-align:center;'>"
                f"{badge_label}</div>",
                unsafe_allow_html=True
            )
            v_status = scheme.get("verification_status", "UNVERIFIED")
            v_date = scheme.get("last_verified_date", "N/A")
            st.caption(f"Status: **{v_status}** ({v_date})")

        st.markdown("---")

        # Details in 2 columns
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.markdown("**🛡️ Financial & Treatment Benefits:**")
            st.write(scheme.get("benefits", "Details available on portal."))

            st.markdown("**📍 Geographical Coverage:**")
            st.write(scheme.get("geographical_coverage", "Pan-India"))

            if result.reasons:
                st.markdown("**✅ Why This May Match Your Situation:**")
                for reason in result.reasons:
                    st.markdown(f"- {reason}")

        with c_right:
            if result.missing_information:
                st.markdown("**❓ Information Requiring Confirmation:**")
                for miss in result.missing_information:
                    st.markdown(f"- {miss}")

            if result.unmet_criteria:
                st.markdown("**❌ Confirmed Disqualifying Factor:**")
                for unmet in result.unmet_criteria:
                    st.markdown(f"- <span style='color:#dc2626;'>{unmet}</span>", unsafe_allow_html=True)

            if scheme.get("limitations_and_exclusions"):
                st.markdown("**⚠️ Limitations & Exclusions:**")
                st.write(scheme.get("limitations_and_exclusions"))

        # Footer Actions
        st.markdown("---")
        btn_c1, btn_c2 = st.columns([1, 1])

        with btn_c1:
            if st.button(
                f"📋 Open Step-by-Step Application Guide",
                key=f"guide_btn_{scheme_id}",
                type="primary",
                use_container_width=True
            ):
                on_select_guide(scheme_id)

        with btn_c2:
            apply_url = scheme.get("official_application_url")
            if apply_url:
                st.link_button("📝 Open Official Application Portal", apply_url, use_container_width=True)
            else:
                st.caption(f"Helpline: {scheme.get('official_helpline', '104')}")
