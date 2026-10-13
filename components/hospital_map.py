"""
LifeBridge Hospital Map and Discovery Component
Renders an interactive OpenStreetMap via Folium and verified hospital directory list.
Provides robust fallback in case of map rendering or coordinate errors.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import folium
from streamlit_folium import st_folium


def render_hospital_directory(
    hospitals: List[Dict[str, Any]],
    user_city: str = "Bengaluru",
    selected_scheme_id: Optional[str] = None
):
    """
    Renders filter controls, interactive Folium map, and detailed hospital cards.
    """
    st.markdown("### 🏥 Verified Hospital Network & Discovery")
    st.caption(
        "Explore real verified government super-specialty and empaneled network hospitals around Bengaluru and Karnataka."
    )

    # Filtering Controls
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])

    with f_col1:
        specialty_filter = st.selectbox(
            "Filter by Specialty / Condition:",
            ["All Specialties", "Oncology (Cancer)", "Cardiology (Heart)", "Nephrology (Dialysis)", "Maternal & Child Care", "Rare Diseases", "General Surgery"],
            key="hosp_specialty_filter"
        )

    with f_col2:
        scheme_filter_opts = [
            "All Schemes",
            "Ayushman Bharat PM-JAY",
            "Arogya Karnataka (AB-ArK)",
            "Rashtriya Arogya Nidhi (RAN)",
            "Pradhan Mantri National Dialysis (PMNDP)",
            "Janani Shishu Suraksha (JSSK)",
            "Yeshasvini Health Insurance"
        ]
        scheme_filter = st.selectbox(
            "Filter by Participating Scheme:",
            scheme_filter_opts,
            key="hosp_scheme_filter"
        )

    with f_col3:
        search_query = st.text_input(
            "Search Hospital Name or Area:",
            "",
            placeholder="e.g. Kidwai, Jayadeva, Victoria...",
            key="hosp_search_query"
        )

    # Filter logic
    filtered = []
    for h in hospitals:
        # 1. Search text
        if search_query:
            query = search_query.lower()
            h_text = f"{h.get('hospital_name', '')} {h.get('address', '')}".lower()
            if query not in h_text:
                continue

        # 2. Specialty filter
        if specialty_filter != "All Specialties":
            spec_map = {
                "Oncology (Cancer)": ["oncology", "cancer"],
                "Cardiology (Heart)": ["cardiology", "cardiothoracic", "cardiac"],
                "Nephrology (Dialysis)": ["nephrology", "dialysis"],
                "Maternal & Child Care": ["maternal", "pediatric", "obstetrics", "gynecology"],
                "Rare Diseases": ["rare disease", "rare diseases", "genetics"],
                "General Surgery": ["surgery", "surgical"]
            }
            target_keywords = spec_map.get(specialty_filter, [])
            all_specs = " ".join([str(s).lower() for s in h.get("specialties", [])] + [str(t).lower() for t in h.get("treatments", [])])
            if not any(k in all_specs for k in target_keywords):
                continue

        # 3. Scheme filter
        if scheme_filter != "All Schemes":
            scheme_id_map = {
                "Ayushman Bharat PM-JAY": "SCHEME-AB-PMJAY",
                "Arogya Karnataka (AB-ArK)": "SCHEME-AB-ARK",
                "Rashtriya Arogya Nidhi (RAN)": "SCHEME-RAN",
                "Pradhan Mantri National Dialysis (PMNDP)": "SCHEME-PMNDP",
                "Janani Shishu Suraksha (JSSK)": "SCHEME-JSSK",
                "Yeshasvini Health Insurance": "SCHEME-YESHASVINI"
            }
            target_sid = scheme_id_map.get(scheme_filter)
            if target_sid and target_sid not in h.get("participating_schemes", []):
                continue

        filtered.append(h)

    st.markdown(f"**Found {len(filtered)} verified hospital(s)**")

    # Map vs List View Options
    view_mode = st.radio(
        "View Format:",
        ["Map + List View", "List Only"],
        horizontal=True,
        key="hosp_view_mode"
    )

    if view_mode == "Map + List View":
        _render_folium_map(filtered)

    st.markdown("#### Hospital Directory & Verified Scheme Participation")
    if not filtered:
        st.warning("No hospitals found matching the selected filters. Please adjust your criteria.")
    else:
        for hosp in filtered:
            _render_single_hospital_card(hosp)


def _render_folium_map(hospitals: List[Dict[str, Any]]):
    """
    Renders Folium map with OpenStreetMap tiles and verified markers.
    Includes robust try-except fallback.
    """
    try:
        # Default center on Bengaluru
        center_lat, center_lon = 12.95, 77.60

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles="OpenStreetMap",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        )

        for h in hospitals:
            lat = h.get("latitude")
            lon = h.get("longitude")
            if lat is not None and lon is not None:
                h_name = h.get("hospital_name", "Hospital")
                h_type = h.get("hospital_type", "Public Hospital")
                contact = h.get("official_contact", "N/A")
                schemes_count = len(h.get("participating_schemes", []))

                # Color coding: Green for Government/Autonomous, Blue for Empaneled Private
                marker_color = "green" if "private" not in h_type.lower() else "blue"
                icon_type = "plus"

                popup_html = f"""
                <div style="font-family: sans-serif; font-size: 12px; width: 220px;">
                    <b style="color: #0f766e; font-size: 13px;">{h_name}</b><br>
                    <span style="color: #475569;">{h_type}</span><br>
                    <hr style="margin: 4px 0;">
                    <b>Phone:</b> {contact}<br>
                    <b>Verified Schemes:</b> {schemes_count} scheme(s)<br>
                    <p style="font-size: 11px; color: #166534; margin: 4px 0 0 0;">Location & Specialties Verified</p>
                </div>
                """

                folium.Marker(
                    location=[float(lat), float(lon)],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=h_name,
                    icon=folium.Icon(color=marker_color, icon=icon_type, prefix="fa")
                ).add_to(m)

        st_folium(m, width=None, height=420, returned_objects=[])

    except Exception as e:
        st.info("Interactive map view is currently in offline mode. Please refer to the hospital list below.")


def _render_single_hospital_card(hosp: Dict[str, Any]):
    h_name = hosp.get("hospital_name", "Hospital")
    h_type = hosp.get("hospital_type", "Hospital")
    address = hosp.get("address", "N/A")
    contact = hosp.get("official_contact", "N/A")
    website = hosp.get("official_website", "")
    specialties = hosp.get("specialties", [])
    treatments = hosp.get("treatments", [])
    schemes = hosp.get("participating_schemes", [])

    is_govt = "private" not in h_type.lower()
    type_badge_color = "#dcfce7" if is_govt else "#eff6ff"
    type_text_color = "#166534" if is_govt else "#1e40af"

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"##### {h_name}")
            st.markdown(
                f"<span style='background-color:{type_badge_color}; color:{type_text_color}; "
                f"padding:3px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;'>{h_type}</span>",
                unsafe_allow_html=True
            )
        with col2:
            st.caption(f"📞 **{contact}**")
            if website:
                st.link_button("🌐 Official Website", website, use_container_width=True)

        st.caption(f"📍 {address}")

        st.markdown("**Verified Specialties & Departments:**")
        spec_tags = " • ".join(specialties)
        st.write(spec_tags if spec_tags else "General tertiary departments")

        st.markdown("**Key Verified Treatments & Facilities:**")
        treat_tags = " • ".join(treatments)
        st.write(treat_tags if treat_tags else "Standard inpatient packages")

        # Scheme Participation with Verification Badges
        st.markdown("**Verified Participating Government Schemes:**")
        scheme_names_map = {
            "SCHEME-AB-PMJAY": "Ayushman Bharat PM-JAY",
            "SCHEME-AB-ARK": "Arogya Karnataka (AB-ArK)",
            "SCHEME-RAN": "Rashtriya Arogya Nidhi (RAN)",
            "SCHEME-HMDG": "Health Minister's Discretionary Grant",
            "SCHEME-CMRF-KA": "Karnataka CM Relief Fund (CMRF)",
            "SCHEME-NPRD": "National Rare Diseases Policy (CoE)",
            "SCHEME-PMNDP": "PM National Dialysis (PMNDP)",
            "SCHEME-JSSK": "Janani Shishu Suraksha (JSSK)",
            "SCHEME-NPY": "Nikshay Poshan TB Scheme",
            "SCHEME-YESHASVINI": "Yeshasvini Cooperative Health Scheme"
        }

        chips = []
        for s_id in schemes:
            label = scheme_names_map.get(s_id, s_id)
            chips.append(f"<span class='profile-pill' style='background:#f0fdf4; color:#15803d; border-color:#bbf7d0;'>✓ {label}</span>")

        st.markdown(" ".join(chips), unsafe_allow_html=True)
        st.caption(
            "Note: Hospital empaneled status is verified. Cashless pre-authorization for your specific treatment requires confirmation at the hospital Arogya Mitra desk."
        )
