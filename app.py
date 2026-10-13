"""
LifeBridge - AI-Assisted Healthcare, Government Scheme Discovery and Hospital Navigation Platform
Main Entry Point.
"""

import streamlit as st
from components.navigation import render_header, render_footer
from pages.healthcare import render_healthcare_page
from pages.education import render_education_page
from pages.food_services import render_food_services_page
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService

# Streamlit Page Setup
st.set_page_config(
    page_title="LifeBridge - Healthcare & Scheme Discovery",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
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


def render_home_page():
    render_header()

    # Hero Banner
    hero_col1, hero_col2 = st.columns([3, 2])
    with hero_col1:
        st.markdown("""
            <h1 style='color: #0f172a; font-size: 2.4rem; font-weight: 800; line-height: 1.2;'>
                Bridge the Gap to <span style='color: #0d9488;'>Government Healthcare</span> and Verified Hospitals
            </h1>
            <p style='color: #475569; font-size: 1.1rem; line-height: 1.6; margin-top: 1rem;'>
                Navigating public assistance shouldn't be overwhelming during medical emergencies. 
                LifeBridge guides you through verified central and Karnataka state healthcare schemes, 
                checks preliminary eligibility transparently, and pinpoints participating hospitals near you.
            </p>
        """, unsafe_allow_html=True)

        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button("🩺 Launch Healthcare Assistant", type="primary", use_container_width=True):
                st.session_state.current_page = "healthcare"
                st.rerun()
        with btn_c2:
            if st.button("🏥 Explore Verified Hospitals", use_container_width=True):
                st.session_state.current_page = "hospitals"
                st.rerun()

    with hero_col2:
        st.markdown("""
            <div style='background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
                <h4 style='color: #0f766e; margin-top: 0;'>🌟 Why LifeBridge?</h4>
                <ul style='color: #334155; line-height: 1.8; padding-left: 1.2rem; margin-bottom: 0;'>
                    <li><b>Rule-Based Transparency:</b> Understand exactly <i>why</i> a scheme matches.</li>
                    <li><b>No Missing Assumptions:</b> Unconfirmed criteria are clearly labeled.</li>
                    <li><b>Verified Karnataka Datasets:</b> 10 Real Government Schemes & 10 Bengaluru Apex Hospitals.</li>
                    <li><b>Privacy First:</b> No Aadhaar or password collection. 100% offline-ready.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Three Major Service Cards
    st.markdown("### 🏛️ Public Service Discovery Portals")
    st.caption("Access public assistance programs across critical domains:")

    col_h, col_e, col_f = st.columns(3)

    # 1. Healthcare Card (Active)
    with col_h:
        with st.container(border=True):
            st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-size: 2rem;'>🩺</span>
                    <span class='badge-active'>Active Module</span>
                </div>
                <h3 style='margin: 0.8rem 0 0.4rem 0; color: #0f172a;'>Healthcare</h3>
                <p style='color: #64748b; font-size: 0.92rem; min-height: 85px;'>
                    Find government financial aid, cashless surgery schemes (PM-JAY, Arogya Karnataka, Yeshasvini), 
                    and locate super-specialty hospitals near Bengaluru.
                </p>
            """, unsafe_allow_html=True)
            if st.button("Explore Healthcare ➔", type="primary", use_container_width=True, key="card_btn_health"):
                st.session_state.current_page = "healthcare"
                st.rerun()

    # 2. Education Card (Active)
    with col_e:
        with st.container(border=True):
            st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-size: 2rem;'>🎓</span>
                    <span class='badge-active'>Active Module</span>
                </div>
                <h3 style='margin: 0.8rem 0 0.4rem 0; color: #0f172a;'>Education</h3>
                <p style='color: #64748b; font-size: 0.92rem; min-height: 85px;'>
                    Discover scholarships (NSP, SSP Post-Matric, NMMS), free residential schools (JNVST Class 6), 
                    and official entrance exams (NEET, JEE).
                </p>
            """, unsafe_allow_html=True)
            if st.button("Explore Education ➔", type="primary", use_container_width=True, key="card_btn_edu"):
                st.session_state.current_page = "education"
                st.rerun()

    # 3. Food & Essential Services Card (Active)
    with col_f:
        with st.container(border=True):
            st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-size: 2rem;'>🌾</span>
                    <span class='badge-active'>Active Module</span>
                </div>
                <h3 style='margin: 0.8rem 0 0.4rem 0; color: #0f172a;'>Food & Essentials</h3>
                <p style='color: #64748b; font-size: 0.92rem; min-height: 85px;'>
                    Apply for ration cards (Karnataka Ahara), explore BPL food & cash entitlements (Anna Bhagya, PMGKAY), 
                    check ONORC portability, and locate nearby Fair Price Shops.
                </p>
            """, unsafe_allow_html=True)
            if st.button("Explore Food Services ➔", type="primary", use_container_width=True, key="card_btn_food"):
                st.session_state.current_page = "food_services"
                st.rerun()

    st.markdown("---")

    # How LifeBridge Works (4 Steps)
    st.markdown("### 💡 How LifeBridge Works")
    st.caption("A guided 4-step path from describing your medical need to stepping into an empaneled hospital.")

    s_c1, s_c2, s_c3, s_c4 = st.columns(4)

    with s_c1:
        st.markdown("""
            <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; text-align:center;'>
                <div style='font-size:1.8rem;'>💬</div>
                <h4 style='color:#0f766e; margin:0.5rem 0;'>1. Describe Situation</h4>
                <p style='font-size:0.85rem; color:#475569;'>Share your diagnosis, district, or family income in natural conversational language.</p>
            </div>
        """, unsafe_allow_html=True)

    with s_c2:
        st.markdown("""
            <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; text-align:center;'>
                <div style='font-size:1.8rem;'>⚖️</div>
                <h4 style='color:#0f766e; margin:0.5rem 0;'>2. Screen Eligibility</h4>
                <p style='font-size:0.85rem; color:#475569;'>Transparent rule engine evaluates central & state schemes without fake approval claims.</p>
            </div>
        """, unsafe_allow_html=True)

    with s_c3:
        st.markdown("""
            <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; text-align:center;'>
                <div style='font-size:1.8rem;'>🗺️</div>
                <h4 style='color:#0f766e; margin:0.5rem 0;'>3. Locate Hospitals</h4>
                <p style='font-size:0.85rem; color:#475569;'>Filter verified government & network hospitals equipped with Arogya Mitra helpdesks.</p>
            </div>
        """, unsafe_allow_html=True)

    with s_c4:
        st.markdown("""
            <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; text-align:center;'>
                <div style='font-size:1.8rem;'>📋</div>
                <h4 style='color:#0f766e; margin:0.5rem 0;'>4. Step-by-Step Guide</h4>
                <p style='font-size:0.85rem; color:#475569;'>Receive a checklist of documents, portal links, and what to do if your claim is delayed.</p>
            </div>
        """, unsafe_allow_html=True)

    render_footer()


def main():
    init_session()

    # Sidebar Navigation & Quick Controls
    with st.sidebar:
        st.markdown("### 🌉 Navigation")
        nav_options = [
            "🏠 Home",
            "🩺 Healthcare Assistant",
            "🎓 Education Discovery",
            "🌾 Food & Essential Services",
            "🏥 Verified Hospitals Directory"
        ]
        page_to_idx = {
            "home": 0,
            "healthcare": 1,
            "education": 2,
            "food_services": 3,
            "hospitals": 4
        }
        current_idx = page_to_idx.get(st.session_state.current_page, 0)
        nav_choice = st.radio("Go to Section:", nav_options, index=current_idx)

        idx_to_page = {
            0: "home",
            1: "healthcare",
            2: "education",
            3: "food_services",
            4: "hospitals"
        }
        chosen_page = idx_to_page[nav_options.index(nav_choice)]
        if chosen_page != st.session_state.current_page:
            st.session_state.current_page = chosen_page
            st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Dataset Overview")
        st.write("• **10** Healthcare Schemes")
        st.write("• **10** Education Programmes")
        st.write("• **10** Food Security Services")
        st.write("• **10** Bengaluru Apex Hospitals")
        st.write("• **10** Verified Food Offices / Kiosks")
        st.write("• **100% Offline** Rule Engine")

        st.markdown("---")
        st.caption("Academic Entrepreneurship Prototype (v2.0)")

    # Page Routing
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "healthcare":
        render_healthcare_page()
    elif st.session_state.current_page == "education":
        render_education_page()
    elif st.session_state.current_page == "food_services":
        render_food_services_page()
    elif st.session_state.current_page == "hospitals":
        from components.hospital_map import render_hospital_directory
        render_header()
        hosp_service = HospitalService()
        hospitals = hosp_service.load_hospitals()
        render_hospital_directory(hospitals)
        render_footer()


if __name__ == "__main__":
    main()
