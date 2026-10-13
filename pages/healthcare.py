"""
LifeBridge Healthcare Module Page
Streamlit multi-page entry point for the Healthcare Discovery Assistant.
"""

import streamlit as st
from components.navigation import render_header, render_footer
from components.chat_interface import render_chat_interface
from components.scheme_cards import render_scheme_cards
from components.hospital_map import render_hospital_directory
from components.application_guide import render_application_guide
from services.conversation_service import ConversationService
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService


def render_healthcare_page():
    # Initialize session states
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "👋 Welcome to **LifeBridge Healthcare Discovery**!\n\n"
                    "I can help you find government healthcare schemes, financial assistance, and empaneled hospitals near Bengaluru.\n\n"
                    "Please describe your medical situation, treatment needs, or family location to get started."
                )
            }
        ]
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "answered_question_ids" not in st.session_state:
        st.session_state.answered_question_ids = []
    if "active_scheme_id" not in st.session_state:
        st.session_state.active_scheme_id = None
    if "active_view" not in st.session_state:
        st.session_state.active_view = "assistant"

    conv_service = ConversationService()
    scheme_matcher = SchemeMatcher()
    hospital_service = HospitalService()

    render_header()

    # Route between Guide view and Main Assistant view
    if st.session_state.active_view == "guide" and st.session_state.active_scheme_id:
        def on_back():
            st.session_state.active_view = "assistant"
            st.rerun()

        render_application_guide(
            scheme_id=st.session_state.active_scheme_id,
            user_profile=st.session_state.user_profile,
            on_back=on_back
        )
    else:
        # Conversational Chat Interface
        def on_profile_change():
            pass

        render_chat_interface(conv_service, on_profile_change)

        st.markdown("---")

        # Two main resource sections: Schemes and Hospitals
        sec_tab1, sec_tab2 = st.tabs([
            "📋 Recommended Healthcare Schemes",
            "🏥 Hospital Search & Map Directory"
        ])

        with sec_tab1:
            results = scheme_matcher.match_schemes(st.session_state.user_profile)

            def on_select_guide(s_id: str):
                st.session_state.active_scheme_id = s_id
                st.session_state.active_view = "guide"
                st.rerun()

            render_scheme_cards(results, on_select_guide)

        with sec_tab2:
            user_city = st.session_state.user_profile.get("city", "Bengaluru")
            hospitals = hospital_service.search_hospitals(city=user_city)
            render_hospital_directory(hospitals, user_city=user_city)

    render_footer()


if __name__ == "__main__":
    st.set_page_config(
        page_title="LifeBridge - Healthcare Assistant",
        page_icon="🌉",
        layout="wide"
    )
    render_healthcare_page()
