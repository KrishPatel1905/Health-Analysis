import streamlit as st
import pandas as pd
import re
import os
import textwrap
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit.components.v1 as components

load_dotenv()

# Set Page Config
st.set_page_config(
    page_title="HemaLoom | Advanced Blood Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Best-effort JavaScript to hide the parent Streamlit Cloud header toolbar
components.html("""
<script>
    const hidePlatformElements = () => {
        try {
            const parentDoc = window.parent.document;
            
            // 1. Hide the header/toolbar entirely
            const headers = parentDoc.querySelectorAll('header, [data-testid="stHeader"]');
            headers.forEach(h => {
                if (h) {
                    h.style.display = 'none';
                    h.style.visibility = 'hidden';
                    h.style.height = '0px';
                }
            });

            // 2. Hide any specific links/buttons to github.com
            const githubLinks = parentDoc.querySelectorAll('a[href*="github.com"]');
            githubLinks.forEach(link => {
                if (link) {
                    link.style.display = 'none';
                }
            });

            // 3. Find and hide spans/buttons containing the word 'Fork'
            const spans = parentDoc.getElementsByTagName('span');
            for (let i = 0; i < spans.length; i++) {
                if (spans[i].textContent.includes('Fork')) {
                    spans[i].style.display = 'none';
                }
            }
            const buttons = parentDoc.getElementsByTagName('button');
            for (let i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.includes('Fork')) {
                    buttons[i].style.display = 'none';
                }
            }
        } catch (e) {
            console.log("Streamlit Cloud wrapper is cross-origin. Hiding parent UI elements programmatically is restricted by browser security.");
        }
    };
    
    // Execute immediately and set intervals to handle dynamic rendering
    hidePlatformElements();
    setInterval(hidePlatformElements, 500);
</script>
""", height=0, width=0)

# Custom Premium Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Apply global font */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Metric cards grid style */
.metric-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-bottom: 25px;
}

.metric-card {
    background-color: #1a1e24;
    border: 1px solid #2e353f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: #00ffd0;
    box-shadow: 0 8px 24px rgba(0, 255, 208, 0.15);
}

.metric-title {
    font-size: 0.85rem;
    color: #8c9ba5;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
    font-weight: 500;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
}

.metric-value.total { color: #00d2ff; }
.metric-value.normal { color: #00e676; }
.metric-value.high { color: #ff5252; }
.metric-value.low { color: #ffd600; }

/* Custom Diet Cards */
.diet-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 25px;
}

.diet-card {
    flex: 1;
    min-width: 280px;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.diet-card.include {
    background: linear-gradient(135deg, rgba(0, 230, 118, 0.08) 0%, rgba(10, 35, 22, 0.35) 100%);
    border-left: 5px solid #00e676;
}

.diet-card.avoid {
    background: linear-gradient(135deg, rgba(255, 82, 82, 0.08) 0%, rgba(40, 12, 12, 0.35) 100%);
    border-left: 5px solid #ff5252;
}

.diet-card h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.25rem;
    font-weight: 600;
}

.diet-card.include h3 { color: #00e676; }
.diet-card.avoid h3 { color: #ff5252; }

.diet-list {
    margin: 0;
    padding: 0;
    list-style-type: none;
}

.diet-list li {
    margin-bottom: 12px;
    line-height: 1.6;
    padding-left: 20px;
    position: relative;
    color: #e2e8f0;
}

.diet-list.include li::before {
    content: "✓";
    color: #00e676;
    font-weight: bold;
    position: absolute;
    left: 0;
}

.diet-list.avoid li::before {
    content: "✗";
    color: #ff5252;
    font-weight: bold;
    position: absolute;
    left: 0;
}

/* Styled Table for Test Data */
.modern-table-container {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #2e353f;
    margin-top: 15px;
}

.modern-table {
    width: 100%;
    border-collapse: collapse;
    color: #e2e8f0;
    background-color: #11151c;
}

.modern-table th {
    background-color: #1e242e;
    color: #00ffd0;
    text-align: left;
    padding: 14px 18px;
    font-weight: 600;
    font-size: 0.95rem;
    border-bottom: 2px solid #2e353f;
}

.modern-table td {
    padding: 14px 18px;
    border-bottom: 1px solid #202630;
    font-size: 0.9rem;
}

.modern-table tr:hover {
    background-color: #1c222c;
}

.badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: bold;
    display: inline-block;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
}

.badge-high {
    background-color: rgba(255, 82, 82, 0.15);
    color: #ff5252;
    border: 1px solid rgba(255, 82, 82, 0.3);
}

.badge-low {
    background-color: rgba(255, 214, 0, 0.12);
    color: #ffd600;
    border: 1px solid rgba(255, 214, 0, 0.3);
}

.badge-normal {
    background-color: rgba(0, 230, 118, 0.12);
    color: #00e676;
    border: 1px solid rgba(0, 230, 118, 0.3);
}

/* Scroll-box for summary */
.summary-container {
    background-color: #161a22;
    border: 1px solid #2e353f;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    line-height: 1.7;
    color: #e2e8f0;
}

/* Hide default Streamlit GitHub icon, deploy button, menu, and footer */
#GithubIcon, [data-testid="stHeaderActionElements"] {
    display: none !important;
}
.stDeployButton, .stAppDeployButton {
    display: none !important;
}
#MainMenu {
    visibility: hidden;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# Helper: Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except ImportError:
        st.error("The 'pypdf' package is not installed. Please run 'pip install pypdf' to upload PDFs.")
        return ""
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return ""

# Helper: Parse Stage 1 Extraction
def parse_extracted_values(text):
    # Match: - Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range
    pattern = r"-\s*(.*?):\s*(.*?)\|\s*Status:\s*(HIGH|LOW|NORMAL)\s*\|\s*Reference:\s*(.*)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    records = []
    
    for match in matches:
        records.append({
            "Test Name": match[0].strip(),
            "Value": match[1].strip(),
            "Status": match[2].strip().upper(),
            "Reference Range": match[3].strip()
        })
        
    if not records:
        # Fallback split-based line parsing
        for line in text.split("\n"):
            line = line.strip()
            if not line or not (line.startswith("-") or line.startswith("*")):
                continue
            try:
                line = line[1:].strip()
                parts = line.split("|")
                if len(parts) >= 3:
                    test_part = parts[0].split(":")
                    test_name = test_part[0].strip()
                    value = ":".join(test_part[1:]).strip()
                    status = parts[1].replace("Status:", "").strip().upper()
                    ref = parts[2].replace("Reference:", "").strip()
                    records.append({
                        "Test Name": test_name,
                        "Value": value,
                        "Status": status,
                        "Reference Range": ref
                    })
            except Exception:
                pass
                
    return pd.DataFrame(records)

# Helper: Parse Stage 2 Diet Plan & Summary response
def parse_diet_response(text):
    health_summary = ""
    foods_include = []
    foods_avoid = []
    meal_plan = {}
    
    # Extract health summary
    summary_match = re.search(r"\[HEALTH SUMMARY\](.*?)(\[FOODS TO INCLUDE\]|\[FOODS TO AVOID\]|\[MEAL PLAN\]|$)", text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        health_summary = summary_match.group(1).strip()
        
    # Extract Foods to Include
    include_match = re.search(r"\[FOODS TO INCLUDE\](.*?)(\[FOODS TO AVOID\]|\[MEAL PLAN\]|$)", text, re.DOTALL | re.IGNORECASE)
    if include_match:
        lines = include_match.group(1).strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("*") or line.startswith("-"):
                parts = line[1:].split("-", 1)
                if len(parts) == 2:
                    foods_include.append((parts[0].strip(), parts[1].strip()))
                else:
                    foods_include.append((parts[0].strip(), ""))
                    
    # Extract Foods to Avoid
    avoid_match = re.search(r"\[FOODS TO AVOID\](.*?)(\[MEAL PLAN\]|$)", text, re.DOTALL | re.IGNORECASE)
    if avoid_match:
        lines = avoid_match.group(1).strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("*") or line.startswith("-"):
                parts = line[1:].split("-", 1)
                if len(parts) == 2:
                    foods_avoid.append((parts[0].strip(), parts[1].strip()))
                else:
                    foods_avoid.append((parts[0].strip(), ""))
                    
    # Extract Meal Plan
    meal_match = re.search(r"\[MEAL PLAN\](.*)", text, re.DOTALL | re.IGNORECASE)
    if meal_match:
        meal_lines = meal_match.group(1).strip().split("\n")
        for line in meal_lines:
            if ":" in line:
                meal_type, meal_desc = line.split(":", 1)
                meal_plan[meal_type.strip()] = meal_desc.replace(";", "").strip()
                
    # Fallback if parsing fails and it's just raw text
    if not health_summary and not foods_include and not foods_avoid:
        health_summary = text
        
    return health_summary, foods_include, foods_avoid, meal_plan

# Sample Report fallback
MOCK_REPORT = """Patient: Rajesh Sharma, Age 48, Male
Date: May 7, 2026

COMPLETE BLOOD COUNT (CBC)
--------------------------
Hemoglobin:        15.1 g/dL        (Normal: 13.5–17.5)
Hematocrit:        44%              (Normal: 41–53%)
WBC:               6.8 x10^3/uL     (Normal: 4.5–11.0)
Platelets:         220 x10^3/uL     (Normal: 150–400)

LIPID PANEL
-----------
Total Cholesterol: 238 mg/dL        (Normal: <200)
LDL Cholesterol:   162 mg/dL        (Normal: <100)
HDL Cholesterol:   36 mg/dL         (Normal: >40)
Triglycerides:     188 mg/dL        (Normal: <150)

METABOLIC PANEL
---------------
Glucose (Fasting): 92 mg/dL         (Normal: 70–99)
HbA1c:             5.3%             (Normal: <5.7%)
Creatinine:        1.0 mg/dL        (Normal: 0.7–1.3)
eGFR:              82 mL/min        (Normal: >60)

LIVER FUNCTION
--------------
ALT:               28 U/L           (Normal: 7–40)
AST:               25 U/L           (Normal: 10–40)
Bilirubin Total:   0.8 mg/dL        (Normal: 0.2–1.2)

Reviewing Physician: Dr. Priya Nair"""

# Initialize Session States
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'extracted_values' not in st.session_state:
    st.session_state['extracted_values'] = ""
if 'full_response' not in st.session_state:
    st.session_state['full_response'] = ""
if 'df_results' not in st.session_state:
    st.session_state['df_results'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'patient_profile' not in st.session_state:
    st.session_state['patient_profile'] = {}
if 'blood_report_text' not in st.session_state:
    st.session_state['blood_report_text'] = ""

# Sidebar Layout & Patient Profiling
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #00ffd0; margin-bottom: 0;">🩸 HemaLoom</h2>
    <p style="font-size: 0.85rem; color: #8c9ba5;">Precision AI Blood Diagnostics</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader("👤 Patient Profile")
p_name = st.sidebar.text_input("Name", value="Rajesh Sharma")
p_age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=48)
p_gender = st.sidebar.selectbox("Gender", options=["Male", "Female", "Other"])

st.sidebar.subheader("🥗 Dietary & Habits")
p_diet = st.sidebar.selectbox("Diet Preference", options=["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"])
p_activity = st.sidebar.selectbox("Activity Level", options=["Sedentary", "Moderately Active", "Very Active"])
p_goal = st.sidebar.selectbox("Health Focus", options=["Manage Cholesterol", "Blood Sugar Control", "General Wellness", "Weight Loss"])

# API Key handling
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("Groq_API_Key") or os.environ.get("groq_api_key")
if not api_key:
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        elif "Groq_API_Key" in st.secrets:
            api_key = st.secrets["Groq_API_Key"]
        elif "groq_api_key" in st.secrets:
            api_key = st.secrets["groq_api_key"]
    except Exception:
        pass

# Strip whitespaces or quotes if loaded
if api_key:
    api_key = api_key.strip().strip("'").strip('"')
else:
    api_key = ""

# Set the key in env so langchain can pick it up automatically
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# Set model with defaults (no UI configs exposed)
llm = None
if api_key:
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, groq_api_key=api_key)
    except Exception as e:
        st.sidebar.error(f"Failed to initialize Groq model: {e}")

# Main Title Header
col_header, col_logo = st.columns([8, 2])
with col_header:
    st.markdown("<h1 style='margin-bottom: 0;'>Blood Work Analyzer</h1>", unsafe_allow_html=True)
st.markdown("---")

# Tab setups
tab_input, tab_dashboard, tab_insights, tab_diet, tab_chat = st.tabs([
    "📥 Upload & Input", 
    "📊 Health Dashboard", 
    "💡 AI Clinical Insights", 
    "🥗 Custom Indian Diet Plan", 
    "💬 Ask AI Health Assistant"
])

# Loading Sample Report Trigger
def load_sample():
    st.session_state.blood_report_text = MOCK_REPORT

# ----------------- TAB 1: INPUT -----------------
with tab_input:
    st.subheader("Provide Blood Report")
    st.write("Upload a PDF/Text report file OR paste the report text manually below.")
    
    col_file, col_btn = st.columns([7, 3])
    with col_file:
        uploaded_file = st.file_uploader("Upload Blood Report (.pdf, .txt)", type=["pdf", "txt"])
    with col_btn:
        st.write("")
        st.write("")
        if st.button("💡 Load Sample Report", use_container_width=True):
            load_sample()
            st.rerun()

    # Determine input text
    report_content = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            report_content = extract_text_from_pdf(uploaded_file)
        else:
            report_content = uploaded_file.read().decode("utf-8")
        st.session_state.blood_report_text = report_content
    
    blood_report = st.text_area(
        label="Or paste your report here",
        value=st.session_state.blood_report_text,
        height=320,
        placeholder="Paste clinical test outputs here..."
    )
    
    st.write("")
    analyze_clicked = st.button("🚀 Analyze Report & Generate Diet", type="primary", use_container_width=True)

    if analyze_clicked:
        if not blood_report.strip():
            st.warning("Please paste a report or upload a file first!")
        elif not llm:
            st.error("🔑 Groq API Key is required. Please set the GROQ_API_KEY environment variable, configure it in Streamlit Secrets, or enter it in the sidebar.")
        else:
            # Save patient profile to session
            st.session_state.patient_profile = {
                "name": p_name,
                "age": p_age,
                "gender": p_gender,
                "diet": p_diet,
                "activity": p_activity,
                "goal": p_goal
            }
            
            with st.spinner("Step 1: Extracting and profiling lab parameters..."):
                extraction_prompt = f"""
You are an expert medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL
based on the reference ranges provided in the report.

Format your response as a list of points exactly like this:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""
                try:
                    extraction_response = llm.invoke(extraction_prompt)
                    st.session_state['extracted_values'] = extraction_response.text
                    st.session_state['df_results'] = parse_extracted_values(st.session_state['extracted_values'])
                except Exception as ex:
                    error_msg = str(ex)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                        st.error("⚠️ **Gemini API Rate Limit / Quota Exceeded (429)**: You have exceeded the free tier quota for this Gemini model. Please wait a few minutes before retrying, change the Gemini model configuration in the sidebar, or configure a different API key.")
                    else:
                        st.error(f"Error executing Stage 1 Extraction: {ex}")
                    st.stop()
            
            with st.spinner("Step 2: Synthesizing clinical insights and Indian diet plan..."):
                diet_prompt = f"""
You are an expert clinical nutritionist specializing in Indian dietary habits and medical nutrition therapy.

Analyze the following blood work results for a {p_age}-year-old {p_gender} with a {p_diet} diet preference, activity level '{p_activity}', and primary health goal '{p_goal}'.

Blood Work Results:
{st.session_state.get('extracted_values', '')}

Provide the output in exactly the following structure:

[HEALTH SUMMARY]
Write a detailed 4-5 line summary of the patient's overall health based on these results. Highlight any red flags (High/Low) and explain their physiological implications in simple, reassuring terms.

[FOODS TO INCLUDE]
Provide 4-5 key Indian foods to include in their diet. For each, give the food name and a short explanation of how it helps their specific condition (e.g. "Oats - Rich in beta-glucan to lower LDL cholesterol").
Format as:
* Food Name - Explanation

[FOODS TO AVOID]
Provide 4-5 Indian foods to strictly limit or avoid. For each, give the food name and why they should avoid it (e.g. "Maida/Refined flour - Raises triglycerides and blood sugar rapidly").
Format as:
* Food Name - Explanation

[MEAL PLAN]
Provide a 1-day sample Indian meal plan tailored to their profile and health needs. Format this as a simple semicolon-separated format for each meal, exactly like this:
Breakfast: Meal details;
Mid-Day: Meal details;
Lunch: Meal details;
Evening: Meal details;
Dinner: Meal details;
"""
                try:
                    diet_response = llm.invoke(diet_prompt)
                    st.session_state['full_response'] = diet_response.text
                    st.session_state['analyzed'] = True
                    # Reset chat history for the new report
                    st.session_state['chat_history'] = []
                    
                    # Rerun to switch to view dashboard
                    st.success("Analysis complete!")
                    st.rerun()
                except Exception as ex:
                    error_msg = str(ex)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                        st.error("⚠️ **Gemini API Rate Limit / Quota Exceeded (429)**: You have exceeded the free tier quota for this Gemini model. Please wait a few minutes before retrying, change the Gemini model configuration in the sidebar, or configure a different API key.")
                    else:
                        st.error(f"Error executing Stage 2 Analysis: {ex}")
                    st.stop()

# ----------------- TAB 2: HEALTH DASHBOARD -----------------
with tab_dashboard:
    if not st.session_state.get('analyzed', False):
        st.info("Please submit your report in the 'Upload & Input' tab to view the dashboard.")
    else:
        profile = st.session_state.get('patient_profile', {})
        st.subheader(f"Dashboard: {profile.get('name', 'Patient')}'s Metrics")
        
        # Calculate summary numbers
        df = st.session_state.get('df_results')
        
        if df is not None and not df.empty:
            total_count = len(df)
            high_count = len(df[df["Status"] == "HIGH"])
            low_count = len(df[df["Status"] == "LOW"])
            normal_count = len(df[df["Status"] == "NORMAL"])
            
            # Display stats cards
            st.markdown(textwrap.dedent(f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-title">Parameters Checked</div>
                    <div class="metric-value total">{total_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Normal Range</div>
                    <div class="metric-value normal">{normal_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">High Parameters</div>
                    <div class="metric-value high">{high_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Low Parameters</div>
                    <div class="metric-value low">{low_count}</div>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            # Interactive Filter & Search
            col_search, col_filter = st.columns([6, 4])
            with col_search:
                search_query = st.text_input("🔍 Search lab parameters...", placeholder="e.g. Cholesterol, Hemoglobin")
            with col_filter:
                filter_status = st.selectbox("Filter by Status", options=["All Statuses", "Abnormal Only (HIGH/LOW)", "NORMAL", "HIGH", "LOW"])
            
            # Filter DataFrame
            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[filtered_df["Test Name"].str.contains(search_query, case=False)]
            
            if filter_status == "Abnormal Only (HIGH/LOW)":
                filtered_df = filtered_df[filtered_df["Status"].isin(["HIGH", "LOW"])]
            elif filter_status != "All Statuses":
                filtered_df = filtered_df[filtered_df["Status"] == filter_status]
                
            # Render Table
            st.markdown("### Blood Panel Results")
            if filtered_df.empty:
                st.write("No matching parameters found.")
            else:
                table_html = ""
                # Build custom HTML table for absolute aesthetic premium control
                table_html = """
                <div class="modern-table-container">
                    <table class="modern-table">
                        <thead>
                            <tr>
                                <th>Test Name</th>
                                <th>Value</th>
                                <th>Status</th>
                                <th>Reference Range</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for idx, row in filtered_df.iterrows():
                    status = row["Status"]
                    badge_class = "badge-normal"
                    if status == "HIGH":
                        badge_class = "badge-high"
                    elif status == "LOW":
                        badge_class = "badge-low"
                    
                    table_html += f"""
                            <tr>
                                <td style="font-weight: 600;">{row['Test Name']}</td>
                                <td>{row['Value']}</td>
                                <td><span class="badge {badge_class}">{status}</span></td>
                                <td style="color: #8c9ba5;">{row['Reference Range']}</td>
                            </tr>
                    """
                table_html += """
                        </tbody>
                    </table>
                </div>
                """
                # Strip leading whitespace from each line to prevent markdown from rendering it as a code block
                clean_table_html = "\n".join([line.strip() for line in table_html.splitlines()])
                st.markdown(clean_table_html, unsafe_allow_html=True)
        else:
            st.warning("We extracted the parameters, but could not structure them in a grid. Please check the raw insights in 'AI Clinical Insights' or review your inputs.")

# ----------------- TAB 3: INSIGHTS -----------------
with tab_insights:
    if not st.session_state.get('analyzed', False):
        st.info("Please submit your report in the 'Upload & Input' tab to view insights.")
    else:
        st.subheader("💡 AI Medical Summary")
        
        # Parse Response
        health_summary, foods_include, foods_avoid, meal_plan = parse_diet_response(st.session_state.get('full_response', ''))
        
        st.markdown(textwrap.dedent(f"""
        <div class="summary-container">
            <h4 style="color:#00ffd0; margin-top:0; font-size:1.1rem; font-weight:600;">Clinical Notes & Overview</h4>
            {health_summary}
        </div>
        """), unsafe_allow_html=True)
        
        st.info("⚠️ **Disclaimer:** All analysis and suggestions are generated by an AI assistant for educational purposes. They are not substitutes for professional medical diagnosis, advice, or treatment. Please discuss these insights with a qualified physician.")

# ----------------- TAB 4: DIET PLAN -----------------
with tab_diet:
    if not st.session_state.get('analyzed', False):
        st.info("Please submit your report in the 'Upload & Input' tab to view your diet planner.")
    else:
        st.subheader("🥗 Personalized Indian Diet Plan")
        
        health_summary, foods_include, foods_avoid, meal_plan = parse_diet_response(st.session_state.get('full_response', ''))
        
        # Display Foods to Include & Avoid side-by-side
        include_items_html = "".join([f"<li><strong>{item}</strong>: {desc}</li>" for item, desc in foods_include])
        avoid_items_html = "".join([f"<li><strong>{item}</strong>: {desc}</li>" for item, desc in foods_avoid])
        
        st.markdown(textwrap.dedent(f"""
        <div class="diet-grid">
            <div class="diet-card include">
                <h3>👍 Foods to Eat / Include</h3>
                <ul class="diet-list include">
                    {include_items_html if include_items_html else "<li>Consult AI chatbot for specifics</li>"}
                </ul>
            </div>
            <div class="diet-card avoid">
                <h3>⚠️ Foods to Limit / Avoid</h3>
                <ul class="diet-list avoid">
                    {avoid_items_html if avoid_items_html else "<li>Consult AI chatbot for details</li>"}
                </ul>
            </div>
        </div>
        """), unsafe_allow_html=True)
        
        # Display Meal Plan
        st.markdown("### Sample 1-Day Indian Meal Schedule")
        if meal_plan:
            meal_df = pd.DataFrame([
                {"Meal Time": key.title(), "Suggested Indian Selection": val}
                for key, val in meal_plan.items()
            ])
            st.dataframe(meal_df, use_container_width=True, hide_index=True)
        else:
            st.write("Custom meal plan schedule is detailed in the raw response. You can consult the AI chatbot for a personalized schedule.")

        # Export Report functionality
        st.subheader("📂 Export Report")
        st.write("Download this complete clinical insights sheet and Indian diet blueprint as a formatted Markdown report.")
        
        # Generate MD content
        profile = st.session_state.get('patient_profile', {})
        md_text = f"""# Clinical Diagnostics & Indian Diet Plan
**Patient:** {profile.get('name', 'Patient')} | **Age:** {profile.get('age', '')} | **Gender:** {profile.get('gender', '')}
**Dietary Goal:** {profile.get('goal', '')} ({profile.get('diet', '')})
---
## 💡 Medical Overview Summary
{health_summary}

## 📊 Extracted Parameters
"""
        df_results = st.session_state.get('df_results')
        if df_results is not None:
            for idx, row in df_results.iterrows():
                md_text += f"- **{row['Test Name']}**: {row['Value']} | {row['Status']} (Ref: {row['Reference Range']})\n"
                
        md_text += "\n## 👍 Recommended Indian Foods to Include\n"
        for i, d in foods_include:
            md_text += f"- **{i}**: {d}\n"
            
        md_text += "\n## ⚠️ Foods to Avoid\n"
        for i, d in foods_avoid:
            md_text += f"- **{i}**: {d}\n"
            
        md_text += "\n## 📆 Sample 1-Day Indian Meal Plan\n"
        for meal, desc in meal_plan.items():
            md_text += f"- **{meal.title()}**: {desc}\n"
            
        md_text += "\n---\n*Disclaimer: AI health summary report. Discuss with your primary healthcare physician.*"
        
        profile = st.session_state.get('patient_profile', {})
        patient_name = profile.get('name', 'Patient').replace(' ', '_')
        st.download_button(
            label="⬇️ Download Markdown Report",
            data=md_text,
            file_name=f"BloodWorkAnalysis_{patient_name}.md",
            mime="text/markdown",
            use_container_width=True
        )

# ----------------- TAB 5: AI CHATBOT -----------------
with tab_chat:
    if not st.session_state.get('analyzed', False):
        st.info("Please submit your report in the 'Upload & Input' tab to unlock the chat assistant.")
    else:
        st.subheader("💬 Ask AI Assistant")
        st.write("Ask any question regarding your lab findings, dietary plans, or health metrics. Let the chatbot explain indicators in simpler terms.")
        
        if not llm:
            st.warning("🔑 Gemini API Key is missing. Please configure it in the sidebar or app secrets to enable the chatbot.")
            
        # Render past conversations
        chat_history = st.session_state.get('chat_history', [])
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Ask user input
        if prompt := st.chat_input("Ask: e.g., 'What is ALT and why is it normal?' or 'Can I eat paneer with my cholesterol profile?'"):
            chat_history = st.session_state.get('chat_history', [])
            chat_history.append({"role": "user", "content": prompt})
            st.session_state['chat_history'] = chat_history
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                if not llm:
                    st.error("🔑 Groq API Key is required to chat with the AI assistant.")
                    st.stop()
                
                with st.spinner("Analyzing profile & medical records..."):
                    profile = st.session_state.get('patient_profile', {})
                    extracted_values = st.session_state.get('extracted_values', '')
                    full_response = st.session_state.get('full_response', '')
                    # Prepare system instruction prompt
                    system_instructions = f"""
You are a clinical health assistant. You are chatting with a patient who recently analyzed their blood work.

Patient Profile:
- Name: {profile.get('name', 'Patient')}
- Age: {profile.get('age', '')}
- Gender: {profile.get('gender', '')}
- Diet: {profile.get('diet', '')}
- Activity level: {profile.get('activity', '')}
- Goal: {profile.get('goal', '')}

Blood Work Summary:
{extracted_values}

Diet Plan & Clinical Insights:
{full_response}

Answer the patient's questions accurately, supportively, and informatively. Focus on commonly available Indian diets/foods when suggesting items. 
Always include a clear disclaimer stating you are an AI assistant and they should consult a real medical doctor for diagnosis.
"""
                    # Assemble chatbot conversation history for LLM
                    chat_context = f"{system_instructions}\n\nChat History:\n"
                    chat_history = st.session_state.get('chat_history', [])
                    for past_msg in chat_history[-8:]: # keep context short
                        chat_context += f"{past_msg['role'].upper()}: {past_msg['content']}\n"
                    chat_context += "ASSISTANT: "
                    
                    try:
                        response = llm.invoke(chat_context)
                        ai_answer = response.text
                        st.markdown(ai_answer)
                        chat_history = st.session_state.get('chat_history', [])
                        chat_history.append({"role": "assistant", "content": ai_answer})
                        st.session_state['chat_history'] = chat_history
                    except Exception as err:
                        st.error(f"Chatbot failed to respond: {err}")
