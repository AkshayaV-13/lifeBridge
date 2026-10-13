"""
LifeBridge Navigation and Global Header Component
Provides consistent visual identity, color scheme, and top navigation.
"""

import streamlit as st


def render_header():
    """
    Renders top branding bar and global styling.
    """
    st.markdown("""
        <style>
        /* LifeBridge Global Styles */
        :root {
            --lb-teal-dark: #0f766e;
            --lb-teal: #0d9488;
            --lb-teal-light: #ccfbf1;
            --lb-blue-dark: #1e40af;
            --lb-blue: #2563eb;
            --lb-blue-light: #eff6ff;
            --lb-bg: #f8fafc;
            --lb-card-bg: #ffffff;
            --lb-text-main: #0f172a;
            --lb-text-muted: #475569;
            --lb-border: #e2e8f0;
        }

        .lb-header-container {
            background: linear-gradient(135deg, #0f766e 0%, #1e40af 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .lb-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin: 0;
            color: #ffffff !important;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .lb-tagline {
            font-size: 1.05rem;
            opacity: 0.95;
            margin-top: 0.4rem;
            color: #f0fdfa !important;
            font-weight: 400;
        }

        .lb-disclaimer-pill {
            display: inline-block;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.8rem;
            font-weight: 500;
            color: #f8fafc;
            margin-top: 0.8rem;
        }

        /* Card Styles */
        .service-card {
            background-color: var(--lb-card-bg);
            border: 1px solid var(--lb-border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            height: 100%;
        }

        .service-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border-color: #0d9488;
        }

        .badge-active {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .badge-coming-soon {
            background-color: #f1f5f9;
            color: #64748b;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .profile-pill {
            display: inline-flex;
            align-items: center;
            background-color: #eff6ff;
            color: #1e40af;
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 3px 10px;
            font-size: 0.82rem;
            font-weight: 600;
            margin: 2px 4px 2px 0;
        }
        </style>

        <div class="lb-header-container">
            <div class="lb-title">
                <span>🌉 LifeBridge</span>
            </div>
            <div class="lb-tagline">
                AI-Assisted Healthcare Assistance, Government Scheme Discovery & Hospital Navigation
            </div>
            <div class="lb-disclaimer-pill">
                ℹ️ Complements official government portals • Transparent rule-based guidance • Karnataka & Bengaluru Prototype
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_footer():
    """
    Renders standard footer with disclaimers and emergency information.
    """
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1.5rem 0;">
            <p><strong>⚠️ Public Assistance & Transparency Notice:</strong><br>
            LifeBridge is an independent, non-profit academic prototype designed for public healthcare discovery. 
            It does not replace government authorities, hospitals, or official statutory eligibility determinations.<br>
            Final benefit approvals and cashless pre-authorizations are issued strictly by competent government bodies and empaneled hospital helpdesks.</p>
            <p style="margin-top: 0.5rem;">
                🚨 <strong>Emergency Numbers:</strong> <strong>112</strong> (National Emergency) • <strong>108</strong> (Ambulance) • <strong>104</strong> (Karnataka State Health Helpline)
            </p>
            <p style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.5rem;">
                Data source: National Health Authority (NHA PM-JAY), Suvarna Arogya Suraksha Trust (SAST), MoHFW Government of India.
            </p>
        </div>
    """, unsafe_allow_html=True)
