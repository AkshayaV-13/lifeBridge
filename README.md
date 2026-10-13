# LifeBridge: AI-Assisted Healthcare, Education & Food Services Platform

🌉 **LifeBridge** is an integrated public-welfare assistance, government scheme discovery, and hospital/service navigation platform built for Indian citizens and families, with an initial regional focus on Karnataka and the Bengaluru metropolitan area.

> **⚠️ Public Assistance & Transparency Notice:**
> LifeBridge complements existing government websites. It does not replace official government portals, schools, examination authorities, hospitals, or statutory eligibility determinations. Final benefit approvals, admissions, and cashless pre-authorizations are issued strictly by competent government bodies (e.g., SAST, NHA, NVS, NTA, Karnataka Food & Civil Supplies Department) and empaneled hospital helpdesks.

---

## 1. Project Vision & Architecture

LifeBridge brings together three vital public-welfare pillars into a single, cohesive, citizen-friendly platform:

1. **🩺 Healthcare:** Transparent eligibility screening for central and Karnataka state healthcare assistance schemes (AB-PMJAY, Arogya Karnataka, Yeshasvini, RAN, etc.), empaneled apex hospital discovery, and 12-section personalized application guides.
2. **🎓 Education:** Smart discovery of scholarships, free residential schooling (JNVST Class 6), fee reimbursement, and official entrance examination information (NEET-UG, JEE Main) without requiring students to know scheme names beforehand.
3. **🌾 Food & Essential Services:** Streamlined citizen guidance for new ration cards (Karnataka Ahara BPL/APL), monthly food and cash entitlements (Anna Bhagya, PMGKAY), nationwide portability (One Nation One Ration Card - ONORC), and location-based discovery of verified Fair Price Shops and government food offices.

---

## 2. Key Modules & Features

### 🩺 Healthcare Module (Active)
- **ChatGPT / Copilot-style Conversational Interface:** Natural-language interaction with deterministic Python entity extraction for medical condition, location, income, and beneficiary card status.
- **Dynamic Follow-Up Questioning:** Asks only missing questions required by candidate schemes, explaining *why* each question is asked.
- **Rule-Based Eligibility Engine:** Categorizes schemes into `🟢 No Known Conflict`, `🟡 Potential Match (Info Needed)`, `🔵 Requires Official Verification`, and `⚪ Confirmed Requirement Not Met`.
- **Verified Hospital Discovery & Map:** Interactive OpenStreetMap display of 10 apex Bengaluru hospitals with custom pins, popups, specialty search, and scheme filters.
- **12-Section Personalized Application Guide:** Step-by-step instructions, interactive document checklists, official portal links, empaneled hospital helpdesk contacts, and grievance redressal channels.

### 🎓 Education Module (Newly Integrated)
- **Needs-Based Opportunity Discovery:** Select from 6 intuitive assistance categories (Scholarships, Fee Assistance, Government & Residential Schools, Entrance Examinations, Free/Subsidised Education, or All Schemes) or describe your situation in natural words.
- **Progressive Student Profiling:** Gathers educational grade (Class 5, Class 6, Class 10, Class 11, Class 12, Undergraduate BTech, etc.), stream, state, and approximate income without unnecessary repetitive questioning.
- **Strict Educational Level Separation:**
  - Class 5/6 students receive school admission opportunities (JNVST Class 6) rather than unrelated college scholarships.
  - Class 11 students are not given Class 6 admissions.
  - College/BTech students receive higher education scholarships (PM-USP CSSS, Karnataka SSP Post-Matric, AICTE Pragati).
  - Entrance exam queries (NEET-UG, JEE Main) immediately produce official exam authority details and application procedures.
- **Transparent Match Labels:** `Potential Match`, `More Information Needed`, `Not a Match — Mandatory Requirement Not Met`, `Programme Information Needs Verification`.
- **8-Step Educational Application Guide:** Clear sequence covering eligibility verification, cycle/deadline verification, document checklists, official portal links, and merit list tracking.

### 🌾 Food & Essential Services Module (Newly Integrated)
- **Minimal Citizen Friction:** Choose directly from 7 service pathways (Apply for new ration card, Food entitlements, ONORC portability, Member modification, BPL eligibility, Service centres, Application status).
- **Entitlement Guidance Without Red Tape:** Users asking about monthly rice or cash transfers (Anna Bhagya) are not forced through a new-card application questionnaire.
- **Nationwide Portability (ONORC):** Guidance for migrant workers to lift subsidised foodgrains anywhere in India with zero new registration required.
- **Nearby Service Centre & Fair Price Shop Locator:**
  - Interactive Folium map of verified Bengaluru government food offices, Bangalore One / Seva Sindhu kiosks, and authorized Fair Price Shops.
  - Clear distinction between *Government Offices*, *Officially Listed Service Centres*, and *Fair Price Shops*.
  - Honest fallback: Explains when a locality is outside the verified directory and provides the official Karnataka Ahara locator link.

---

## 3. Technology Stack

- **Application Logic:** Python 3.10+
- **Web Interface:** Streamlit (v1.35+)
- **Map & Spatial Visualization:** Folium & Streamlit-Folium (OpenStreetMap tiles)
- **Data Persistence:** JSON (`data/healthcare_schemes.json`, `data/education_schemes.json`, `data/food_services.json`, `data/food_service_centres.json`, `data/hospitals.json`)
- **Testing Suite:** Pytest
- **Environment Management:** python-dotenv (Optional LLM integration via `.env`)

---

## 4. Project Folder Structure

```
lifebridge/
│
├── app.py                            # Main application entry point, multi-page router, and homepage
├── requirements.txt                  # Python dependencies
├── README.md                         # Detailed system documentation
├── .env.example                      # Safe environment variable template
├── conftest.py                       # Pytest path configuration
├── .gitignore                        # Git ignore patterns
│
├── pages/
│   ├── healthcare.py                 # Healthcare module page
│   ├── education.py                  # Education & scholarship module page
│   └── food_services.py              # Food security & ration services module page
│
├── components/
│   ├── __init__.py
│   ├── navigation.py                 # Header, branding & footer
│   ├── chat_interface.py             # Chat UI, history & dynamic question chips
│   ├── scheme_cards.py               # Categorized scheme recommendation cards
│   ├── hospital_map.py               # Folium hospital interactive map & directory
│   └── application_guide.py          # 12-section personalized healthcare guide
│
├── services/
│   ├── __init__.py
│   ├── eligibility_engine.py         # Transparent rule-based healthcare eligibility engine
│   ├── scheme_matcher.py             # Healthcare scheme loader, ranking & fallbacks
│   ├── hospital_service.py           # Hospital filtering & Haversine distance
│   ├── conversation_service.py       # Python NLP entity extractor & slot tracker
│   ├── application_guide_service.py  # Evidence-based healthcare guide generator
│   ├── education_service.py          # Rule-based education matching & guide generator
│   └── food_services_service.py      # Food services matcher & nearby centre locator
│
├── data/
│   ├── healthcare_schemes.json       # 10 verified real healthcare schemes
│   ├── education_schemes.json        # 10 verified real educational programmes
│   ├── food_services.json            # 10 verified real food security services
│   ├── food_service_centres.json     # 10 verified Bengaluru government food offices/centres
│   └── hospitals.json                # 10 verified Bengaluru apex hospitals
│
└── tests/
    ├── __init__.py
    ├── test_eligibility_engine.py    # Healthcare matching, missing info & unmet rules
    ├── test_scheme_matcher.py        # Healthcare dataset loading & fallback handling
    ├── test_hospital_service.py      # Hospital verification & coordinates
    ├── test_conversation_service.py  # Healthcare conversation continuity & slot filling
    ├── test_guide_and_data_integrity.py # Healthcare guide & coordinate integrity
    ├── test_education_service.py     # Education matching, grade separation & exam logic
    ├── test_food_services_service.py # Food services, ONORC portability & centre search
    └── test_integration_modules.py  # Cross-module integration, offline execution & imports
```

---

## 5. Datasets (Accurately Sourced & Verified)

### A. 10 Real Education Schemes (`data/education_schemes.json`)
1. **Jawahar Navodaya Vidyalaya Selection Test (JNVST - Class 6):** 100% free residential schooling for rural talent.
2. **National Means-cum-Merit Scholarship Scheme (NMMSS):** ₹12,000/year for Class 9-12 students in Govt/Aided schools.
3. **PM-USP Central Sector Scheme of Scholarship (CSSS):** ₹12,000 to ₹20,000/year for undergraduate & PG students.
4. **Karnataka SSP Post-Matric Scholarship:** Tuition fee reimbursement & maintenance allowance for Karnataka students.
5. **AICTE Pragati Scholarship for Girls:** ₹50,000/year for female technical degree/diploma students.
6. **NEET-UG (NTA):** National single entrance exam for undergraduate medical (MBBS/BDS) admissions.
7. **JEE (Main) (NTA):** National entrance examination for NITs, IIITs, and JEE Advanced qualifying.
8. **Right to Education (RTE Section 12(1)(c)):** 25% free private school seats for disadvantaged LKG/Class 1 entry.
9. **Karnataka Vidyasiri Scheme:** ₹1,500/month food and accommodation stipend for rural OBC/SC/ST college students.
10. **PM SHRI Schools Initiative:** Upgraded smart government schools with modern labs and zero/nominal fees.

### B. 10 Real Food & Essential Services (`data/food_services.json`)
1. **Priority Household (PHH) Ration Card:** 5 kg free foodgrains/person/month under PMGKAY.
2. **Antyodaya Anna Yojana (AAY):** 35 kg free foodgrains/household/month for indigent families.
3. **One Nation One Ration Card (ONORC):** Nationwide interstate portability using biometric e-PoS.
4. **Karnataka Ahara - New Ration Card Application:** Online portal service for new BPL/APL cards.
5. **Karnataka Ahara - Member Modification Service:** Add child/spouse, delete member, address change.
6. **Karnataka Anna Bhagya Scheme:** 5 kg free rice + ₹170 cash DBT/person/month for BPL cardholders.
7. **Fair Price Shop & Taluk Office Locator:** Public search directory for authorized ration dealers.
8. **Ration Card Status Tracking:** Real-time online verification of new applications and inspector reports.
9. **PM Garib Kalyan Anna Yojana (PMGKAY):** Central 100% free foodgrain guarantee.
10. **Mera Ration Mobile Application (NIC):** Entitlements tracking, GPS ration shop locator, and grievance portal.

### C. 10 Verified Bengaluru Food Offices & Centres (`data/food_service_centres.json`)
- Deputy Director Office, Food & Civil Supplies (KG Road)
- Taluk Food Supply Office, Bengaluru South (Jayanagar Mini Vidhana Soudha)
- Taluk Food Supply Office, Bengaluru North (Yelahanka)
- Taluk Food Supply Office, Bengaluru East (KR Puram)
- Bangalore One Citizen Service Centres (Jayanagar, Malleshwaram, Indiranagar)
- Seva Sindhu Citizen Service Centre (Shivajinagar)
- Authorized Fair Price Shops (BTM Layout No. 142, Rajajinagar No. 88)

---

## 6. Local Execution & Testing

### Installation
```bash
pip install -r requirements.txt
```

### Run the Web Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Run the Complete Automated Test Suite
```bash
python -m pytest -v
```

All 40 unit and integration tests pass with 100% success rate:
- **Conversation Service (3 tests):** Slot retention, dynamic follow-up logic, grounded FAQs.
- **Education Service (8 tests):** Class 6 residential vs college scholarship, Class 11 vs Class 6 separation, NEET entrance exam, missing income, unverified deadline labeling, fallback handling.
- **Food Services Service (8 tests):** New card applicant, ONORC portability, entitlement inquiries, state jurisdiction guarding, unknown eligibility handling, honest nearby centre search, missing data resilience.
- **Eligibility Engine (4 tests):** Potential match, missing data requests, confirmed unmet requirements, data resilience.
- **Hospital Service (5 tests):** Real dataset loading, scheme participation distinction, Haversine distance, specialty filtering, missing data resilience.
- **Guide & Data Integrity (3 tests):** 12-section guide validation, end-to-end conversation scenarios, coordinate validity.
- **Integration Tests (5 tests):** Healthcare module functional, Education module functional, Food module functional, 100% offline operation without API keys, clean imports of all pages and components.

---

## 7. Cloud Deployment (Streamlit Community Cloud)

1. Commit and push the repository to GitHub:
   ```bash
   git add .
   git commit -m "Integrate Education and Food & Essential Services modules"
   git push origin main
   ```
2. Log in to **[share.streamlit.io](https://share.streamlit.io)** with GitHub.
3. Click **"New app"**, select your repository, set the **Main file path** to `app.py`, and click **"Deploy"**.
