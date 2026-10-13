"""
LifeBridge Chat Interface Component
Provides ChatGPT / Copilot-style conversational experience with entity extraction,
visible conversation history, dynamic follow-up chips, and grounded answers.
"""

import streamlit as st
from typing import Dict, Any, Callable, List
from services.conversation_service import ConversationService


def render_chat_interface(
    conv_service: ConversationService,
    on_profile_updated: Callable[[], None]
):
    """
    Renders conversational assistant interface with history, follow-up prompts,
    and profile status chips.
    """
    st.markdown("### 💬 Conversational Healthcare Assistance")
    st.caption(
        "Describe your medical situation, family circumstances, or questions in plain language. "
        "LifeBridge will identify relevant factors and guide you to official schemes and hospitals."
    )

    # 1. Profile Status Bar
    _render_profile_status(on_profile_updated)

    # 2. Sample Prompt Quick-Starters (if chat history is small)
    if len(st.session_state.get("chat_history", [])) <= 1:
        st.markdown("**💡 Quick Demonstration Scenarios (Click to test):**")
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("🎗️ Cancer Treatment in Bengaluru", use_container_width=True):
                _handle_user_submission(
                    "I have cancer and need treatment, but I cannot afford it. I am looking for government assistance and hospitals near Bengaluru.",
                    conv_service,
                    on_profile_updated
                )
        with p_col2:
            if st.button("❤️ Heart Surgery in Karnataka", use_container_width=True):
                _handle_user_submission(
                    "My father needs heart treatment. Our family income is low and we live in Karnataka. Can you help us find financial assistance?",
                    conv_service,
                    on_profile_updated
                )
        with p_col3:
            if st.button("🩺 Kidney Dialysis Support", use_container_width=True):
                _handle_user_submission(
                    "My family member needs regular kidney dialysis in Bengaluru. We have a BPL ration card. Where can we get free dialysis?",
                    conv_service,
                    on_profile_updated
                )

    st.markdown("---")

    # 3. Visible Chat History
    chat_container = st.container(height=380)
    with chat_container:
        for msg in st.session_state.get("chat_history", []):
            role = msg.get("role", "assistant")
            avatar = "🧑" if role == "user" else "🌉"
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg.get("content", ""))

    # 4. Dynamic Follow-Up Questions (if profile needs essential details)
    user_prof = st.session_state.get("user_profile", {})
    answered = st.session_state.get("answered_question_ids", [])
    follow_ups = conv_service.get_dynamic_follow_up_questions(user_prof, answered)

    if follow_ups:
        q = follow_ups[0]
        q_id = q["id"]
        with st.container(border=True):
            st.markdown(f"**❓ Next Helpful Detail: {q['question']}**")
            st.caption(f"ℹ️ *Why we ask:* {q['rationale']}")

            q_cols = st.columns(len(q["options"]) + 1)
            for idx, opt in enumerate(q["options"]):
                with q_cols[idx]:
                    if st.button(opt, key=f"q_opt_{q_id}_{idx}", use_container_width=True):
                        st.session_state.answered_question_ids.append(q_id)
                        _handle_user_submission(
                            f"My answer for {q_id}: {opt}",
                            conv_service,
                            on_profile_updated
                        )
            with q_cols[-1]:
                if st.button("Skip ⏩", key=f"q_skip_{q_id}", use_container_width=True):
                    st.session_state.answered_question_ids.append(q_id)
                    st.rerun()

    # 5. User Input Area
    with st.form(key="chat_input_form", clear_on_submit=True):
        input_c1, input_c2 = st.columns([5, 1])
        with input_c1:
            user_text = st.text_input(
                "Type your message here...",
                placeholder="Describe your medical condition, question, or type 'Which documents do I need?'",
                label_visibility="collapsed"
            )
        with input_c2:
            submit_btn = st.form_submit_button("Send 🚀", type="primary", use_container_width=True)

    if submit_btn and user_text.strip():
        _handle_user_submission(user_text.strip(), conv_service, on_profile_updated)


def _render_profile_status(on_reset: Callable[[], None]):
    prof = st.session_state.get("user_profile", {})
    pills = []

    if prof.get("state"):
        pills.append(f"📍 State: <b>{prof['state']}</b>")
    if prof.get("city"):
        pills.append(f"🏙️ City: <b>{prof['city']}</b>")
    if prof.get("condition"):
        pills.append(f"🩺 Medical Condition: <b>{prof['condition'].title()}</b>")
    if prof.get("ration_card_type"):
        pills.append(f"💳 Ration Card: <b>{prof['ration_card_type']}</b>")
    if prof.get("annual_income"):
        pills.append(f"💰 Income: <b>₹{prof['annual_income']:,.0f}</b>")
    if prof.get("has_cooperative_membership") is not None:
        status = "Yes" if prof["has_cooperative_membership"] else "No"
        pills.append(f"🤝 Coop Member: <b>{status}</b>")

    col_info, col_reset = st.columns([4, 1])
    with col_info:
        if pills:
            pills_html = "".join([f"<span class='profile-pill'>{p}</span>" for p in pills])
            st.markdown(f"**Identified Information:** {pills_html}", unsafe_allow_html=True)
        else:
            st.caption("No specific profile details identified yet. Type your situation to begin.")

    with col_reset:
        if pills and st.button("🔄 Reset Details", use_container_width=True, key="reset_profile_btn"):
            st.session_state.user_profile = {}
            st.session_state.answered_question_ids = []
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": "Profile has been reset. How can I help you find healthcare schemes or hospitals today?"
                }
            ]
            on_reset()
            st.rerun()


def _handle_user_submission(
    user_text: str,
    conv_service: ConversationService,
    on_profile_updated: Callable[[], None]
):
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_text})

    # Extract entities
    updated_profile = conv_service.extract_entities(
        user_text,
        st.session_state.get("user_profile", {})
    )
    st.session_state.user_profile = updated_profile

    # Generate assistant reply grounded in data
    active_scheme = st.session_state.get("active_scheme_id")
    response_data = conv_service.handle_user_query(user_text, updated_profile, active_scheme)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_data["text"]
    })

    on_profile_updated()
    st.rerun()
