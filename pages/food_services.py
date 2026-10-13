"""
LifeBridge Food & Essential Services Module Page
Provides citizen-friendly guidance for ration cards, BPL entitlements,
One Nation One Ration Card (ONORC) portability, and nearby verified service centres.
"""

import streamlit as st
from components.navigation import render_header, render_footer
from services.food_services_service import FoodServicesService, FoodServiceMatchResult
import folium
from streamlit_folium import st_folium


def render_food_services_page():
    render_header()

    if "food_profile" not in st.session_state:
        st.session_state.food_profile = {
            "state": "Karnataka",
            "service_category": "Apply for New Ration Card"
        }
    if "food_active_guide" not in st.session_state:
        st.session_state.food_active_guide = None

    food_service = FoodServicesService()

    # Active Guide View
    if st.session_state.food_active_guide:
        _render_food_guide_view(st.session_state.food_active_guide, food_service)
        render_footer()
        return

    # Title & Subtitle
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='color: #0f172a; margin-bottom: 0.2rem;'>🌾 Food Security & Essential Public Services</h2>
            <p style='color: #475569; font-size: 1.05rem;'>
                Navigate ration-card applications, BPL food entitlements (Anna Bhagya & PMGKAY), 
                nationwide portability (ONORC), and locate verified Fair Price Shops & government supply offices in Bengaluru.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Quick Demonstration Scenarios
    st.markdown("**💡 Quick Demonstration Scenarios (Click to test):**")
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)

    with f_c1:
        if st.button("📝 Apply for BPL Card (Karnataka)", use_container_width=True, key="demo_food_new"):
            st.session_state.food_profile = {
                "service_category": "Apply for New Ration Card",
                "state": "Karnataka",
                "has_existing_card": False
            }
            st.rerun()

    with f_c2:
        if st.button("🔄 Ration Portability (ONORC)", use_container_width=True, key="demo_food_onorc"):
            st.session_state.food_profile = {
                "service_category": "Check Portability (One Nation One Ration Card)",
                "state": "Karnataka",
                "has_existing_card": True
            }
            st.rerun()

    with f_c3:
        if st.button("🍚 Anna Bhagya & Free Grain", use_container_width=True, key="demo_food_grain"):
            st.session_state.food_profile = {
                "service_category": "Food & Ration Entitlements",
                "state": "Karnataka",
                "has_existing_card": True
            }
            st.rerun()

    with f_c4:
        if st.button("📍 Find Nearby Service Centre", use_container_width=True, key="demo_food_centres"):
            st.session_state.food_profile = {
                "service_category": "Find Nearby Service Centre / Ration Shop",
                "state": "Karnataka"
            }
            st.rerun()

    st.markdown("---")

    # 2. Main Interface Tabs: Services vs Nearby Centres
    tab_services, tab_centres = st.tabs([
        "📋 Public Food Services & Ration Assistance",
        "🗺️ Verified Ration Offices & Service Centre Locator"
    ])

    with tab_services:
        col_form, col_cards = st.columns([1, 2])

        with col_form:
            with st.container(border=True):
                st.markdown("#### 🎯 Service Request")
                st.caption("Select what service you need:")

                cat_list = [
                    "Apply for New Ration Card",
                    "Food & Ration Entitlements",
                    "Check Portability (One Nation One Ration Card)",
                    "Update or Correct Ration Card Details",
                    "BPL Eligibility & Benefit Information",
                    "Track Application Status",
                    "Find Nearby Service Centre / Ration Shop"
                ]

                curr_cat = st.session_state.food_profile.get("service_category", "Apply for New Ration Card")
                cat_idx = cat_list.index(curr_cat) if curr_cat in cat_list else 0

                sel_cat = st.selectbox(
                    "Service Category:",
                    cat_list,
                    index=cat_idx,
                    key="food_cat_select"
                )
                st.session_state.food_profile["service_category"] = sel_cat

                # Optional natural query
                user_msg = st.text_input(
                    "Or describe what you need:",
                    placeholder="e.g. moving to another state with my card",
                    key="food_query_input"
                )
                if user_msg:
                    extracted = food_service.extract_food_entities(user_msg, st.session_state.food_profile)
                    st.session_state.food_profile.update(extracted)

                st.markdown("---")
                st.markdown("##### Minimal Household Details")

                card_status = st.radio(
                    "Does your family currently hold a ration card?",
                    ["No / Applying for First Time", "Yes, Already have an active card", "Not Sure / In Process"],
                    index=0 if not st.session_state.food_profile.get("has_existing_card") else 1
                )
                if "Yes" in card_status:
                    st.session_state.food_profile["has_existing_card"] = True
                elif "No" in card_status:
                    st.session_state.food_profile["has_existing_card"] = False
                else:
                    st.session_state.food_profile["has_existing_card"] = None

                state_list = ["Karnataka", "Delhi", "Maharashtra", "Tamil Nadu", "Other State"]
                curr_st = st.session_state.food_profile.get("state", "Karnataka")
                st_idx = state_list.index(curr_st) if curr_st in state_list else 0
                sel_st = st.selectbox("Your State of Residence:", state_list, index=st_idx)
                st.session_state.food_profile["state"] = sel_st

                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    if st.button("Find Services 🔍", type="primary", use_container_width=True):
                        st.rerun()
                with c_f2:
                    if st.button("Reset 🔄", use_container_width=True):
                        st.session_state.food_profile = {"state": "Karnataka"}
                        st.rerun()

        with col_cards:
            matches = food_service.match_services(st.session_state.food_profile)
            actionable = [m for m in matches if m.score > 0 and m.status_label == "Potential Match"]
            other = [m for m in matches if m.status_label == "Not a Match — Mandatory Requirement Not Met"]

            st.markdown(f"### 📦 Recommended Public Services ({len(actionable)} Found)")

            if not actionable:
                st.warning(
                    "No specific service matched your request in the initial screening. "
                    "You can visit the official **[National Food Security Portal](https://nfsa.gov.in)** "
                    "or the **[Karnataka Ahara Portal](https://ahara.kar.nic.in)**."
                )
            else:
                for m in actionable:
                    _render_single_food_service_card(m)

            if other:
                with st.expander(f"ℹ️ Other Services Not Directly Relevant ({len(other)})"):
                    for m in other:
                        _render_single_food_service_card(m, is_other=True)

    with tab_centres:
        _render_nearby_centres_section(food_service)

    render_footer()


def _render_single_food_service_card(result: FoodServiceMatchResult, is_other: bool = False):
    svc = result.service
    sid = svc.get("service_id")
    name = svc.get("name")
    rtype = svc.get("record_type")
    desc = svc.get("description")
    benefits = svc.get("benefits_or_service")
    v_status = svc.get("verification_status")
    v_date = svc.get("last_verified_date")

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"#### {name}")
            st.markdown(
                f"<span style='background-color:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700;'>{rtype}</span>",
                unsafe_allow_html=True
            )
        with c2:
            badge_bg = "#fee2e2" if is_other else "#dcfce7"
            badge_text = "#991b1b" if is_other else "#166534"
            badge_label = "Excluded / Unmet" if is_other else "Potential Match"
            st.markdown(
                f"<div style='background-color:{badge_bg}; color:{badge_text}; padding:5px 10px; border-radius:15px; font-size:0.78rem; font-weight:700; text-align:center;'>{badge_label}</div>",
                unsafe_allow_html=True
            )
            st.caption(f"Status: **{v_status}** ({v_date})")

        st.markdown(f"*{desc}*")

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**🛡️ Entitlements & Public Services:**")
            st.write(benefits)
            st.markdown("**📍 Geographical Jurisdiction:**")
            st.write(svc.get("geographical_coverage"))

            if result.reasons:
                st.markdown("**✅ Why This Service Matches Your Need:**")
                for r in result.reasons:
                    st.markdown(f"- {r}")

        with col_r:
            st.markdown("**⚖️ Verified Eligibility Rules:**")
            st.write(svc.get("eligibility_criteria"))

            if result.unmet_criteria:
                st.markdown("**❌ Restriction / Ineligibility Factor:**")
                for u in result.unmet_criteria:
                    st.markdown(f"- <span style='color:#dc2626;'>{u}</span>", unsafe_allow_html=True)

            if result.missing_information:
                st.markdown("**❓ Information Requiring Verification:**")
                for m in result.missing_information:
                    st.markdown(f"- <span style='color:#b45309;'>{m}</span>", unsafe_allow_html=True)

        st.markdown("---")
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button("📋 View Step-by-Step Application Guide", key=f"guide_food_{sid}", type="primary", use_container_width=True):
                st.session_state.food_active_guide = sid
                st.rerun()
        with btn_c2:
            if svc.get("official_application_url"):
                st.link_button("📝 Open Official Application Portal", svc["official_application_url"], use_container_width=True)


def _render_food_guide_view(service_id: str, food_service: FoodServicesService):
    svc = food_service.get_service_by_id(service_id)
    if not svc:
        st.error("Service information could not be found.")
        if st.button("⬅️ Back to Services"):
            st.session_state.food_active_guide = None
            st.rerun()
        return

    c_back, c_title = st.columns([1, 4])
    with c_back:
        if st.button("⬅️ Back to Food Services", type="secondary", use_container_width=True):
            st.session_state.food_active_guide = None
            st.rerun()

    with c_title:
        st.markdown(f"### 📋 Step-by-Step Citizen Service Guide")
        st.markdown(f"#### {svc.get('name')}")

    st.info(
        f"**Service Type:** {svc.get('record_type')} • "
        f"**Jurisdiction:** {svc.get('geographical_coverage')} • "
        f"**Status:** {svc.get('verification_status')} ({svc.get('last_verified_date')})"
    )

    t1, t2, t3, t4 = st.tabs([
        "1. Service Overview & Eligibility",
        "2. Required Documents Checklist",
        "3. Step-by-Step Instructions",
        "4. Status Tracking & Helplines"
    ])

    with t1:
        st.markdown("#### 🎯 Service Purpose")
        st.write(svc.get("description"))

        st.markdown("#### 🛡️ Entitlements & Services Granted")
        st.write(svc.get("benefits_or_service"))

        st.markdown("#### ⚖️ Eligibility Criteria")
        st.write(svc.get("eligibility_criteria"))

    with t2:
        st.markdown("#### 📑 Required Documents Checklist")
        st.caption("Ensure all family member details match official Aadhaar records:")
        for idx, doc in enumerate(svc.get("required_documents", []), 1):
            st.checkbox(f"**{idx}. {doc}**", key=f"food_chk_{service_id}_{idx}")

    with t3:
        st.markdown("#### 🚶 Step-by-Step Process")
        for step in svc.get("application_steps", []):
            st.markdown(f"- {step}")

    with t4:
        st.markdown("#### 🌐 Official Application Links")
        if svc.get("official_application_url"):
            st.link_button("📝 Open Official Application Portal", svc["official_application_url"], use_container_width=True)

        st.caption(f"📞 Verified Government Helpline: **{svc.get('official_contact', '1967')}**")


def _render_nearby_centres_section(food_service: FoodServicesService):
    st.markdown("### 🗺️ Verified Food Supply Offices & Service Centres (Bengaluru Area)")
    st.caption(
        "Find authorized Taluk Food Offices, official Bangalore One / Seva Sindhu citizen centres, "
        "and licensed Fair Price Shops. Location verification is strictly backed by government records."
    )

    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col1:
        type_filter = st.selectbox(
            "Filter by Centre Category:",
            ["All Categories", "Government Office", "Officially Listed Service Centre", "Fair Price Shop"],
            key="food_type_filter"
        )
    with f_col2:
        search_loc = st.text_input(
            "Search Bengaluru Locality:",
            "",
            placeholder="e.g. Jayanagar, Malleshwaram, Indiranagar, BTM...",
            key="food_loc_filter"
        )
    with f_col3:
        view_opt = st.radio("View Format:", ["Map + List View", "List Only"], horizontal=True, key="food_view_opt")

    # Filter centres
    norm_type = None if type_filter == "All Categories" else type_filter
    centres = food_service.search_nearby_centres(locality=search_loc, centre_type=norm_type)

    st.markdown(f"**Found {len(centres)} verified centre(s)**")

    if view_opt == "Map + List View":
        _render_centres_map(centres)

    st.markdown("#### Centre Directory & Contact Details")
    if not centres:
        st.warning(
            "No verified centres found for the specified search. "
            "Please check the official **[Karnataka Fair Price Shop Locator](https://ahara.kar.nic.in/status2/fps_details.aspx)** "
            "for live statewide listings."
        )
    else:
        for c in centres:
            _render_single_centre_card(c)


def _render_centres_map(centres):
    try:
        m = folium.Map(
            location=[12.97, 77.59],
            zoom_start=11,
            tiles="OpenStreetMap",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        )

        for c in centres:
            lat = c.get("latitude")
            lon = c.get("longitude")
            if lat and lon:
                c_name = c.get("name")
                c_type = c.get("centre_type")
                phone = c.get("contact_phone", "N/A")
                agency = c.get("authorized_agency", "Authorized")

                color = "green" if "Government Office" in c_type else ("blue" if "Service Centre" in c_type else "orange")
                popup_html = f"""
                <div style="font-family:sans-serif; font-size:12px; width:220px;">
                    <b style="color:#0f766e;">{c_name}</b><br>
                    <span style="color:#475569;">{c_type}</span><br>
                    <hr style="margin:4px 0;">
                    <b>Phone:</b> {phone}<br>
                    <b>Agency:</b> {agency}<br>
                    <p style="font-size:11px; color:#166534; margin:4px 0 0 0;">Verified Official Centre</p>
                </div>
                """

                folium.Marker(
                    location=[float(lat), float(lon)],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=c_name,
                    icon=folium.Icon(color=color, icon="home", prefix="fa")
                ).add_to(m)

        st_folium(m, width=None, height=400, returned_objects=[])

    except Exception:
        st.info("Interactive map view is currently in offline mode. Please refer to the centre directory below.")


def _render_single_centre_card(c):
    c_name = c.get("name")
    c_type = c.get("centre_type")
    addr = c.get("address")
    phone = c.get("contact_phone")
    agency = c.get("authorized_agency")
    portal = c.get("official_portal")
    services = c.get("services_offered", [])

    badge_color = "#dcfce7" if "Government Office" in c_type else ("#eff6ff" if "Service Centre" in c_type else "#fef3c7")
    text_color = "#166534" if "Government Office" in c_type else ("#1e40af" if "Service Centre" in c_type else "#92400e")

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"##### {c_name}")
            st.markdown(
                f"<span style='background-color:{badge_color}; color:{text_color}; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;'>{c_type}</span>",
                unsafe_allow_html=True
            )
        with col2:
            st.caption(f"📞 **{phone}**")
            if portal:
                st.link_button("🌐 Official Portal", portal, use_container_width=True)

        st.caption(f"📍 {addr}")
        st.markdown(f"**Authorized Agency:** {agency}")

        if services:
            st.markdown("**Services Offered at this Centre:**")
            chips = " • ".join(services)
            st.write(chips)


if __name__ == "__main__":
    st.set_page_config(page_title="LifeBridge - Food & Essential Services", page_icon="🌾", layout="wide")
    render_food_services_page()
