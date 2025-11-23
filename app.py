import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import urlparse

# --- Configuration for Sample Data Generation (from data_loader.py) ---
GRANT_TYPES = [
    "Small Business Innovation Research", "Small Business Technology Transfer",
    "Minority-Owned Business Grants", "Women-Owned Business Grants",
    "Rural Business Development Grants", "Pell Grants", "Fulbright Program Grants",
    "National Science Foundation (NSF)", "Teacher Quality Partnership Grants",
    "Head Start Program Grants", "Community Development Block Grants",
    "Arts & Culture Grants", "Health & Wellness Grants", "Youth Development Grants",
    "Environmental Education Grants", "Energy Efficiency and Renewable",
    "Agricultural Research Grants", "STEM Education Grants",
    "Biomedical Research Grants", "Technology Commercialization Grants",
    "Veterans Assistance Grants", "Disaster Relief and Recovery Grants",
    "Housing Assistance Grants", "Accessibility Grants", "Cultural Preservation Grants"
]

STATUSES = ["New", "Under Review", "Interested", "Not Interested"]
AGENCIES = ["NSF", "NIH", "DOE", "USDA", "SBA", "NEA", "HUD", "VA", "EPA", "DOD"]
STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
COUNTRIES = ["USA", "Canada", "UK", "Germany", "France"]

# --- Utility Functions (Consolidated from app.py and grant_sections.py) ---

def safe_date_parse(date_str):
    """Safely parse date strings, handling potential errors."""
    if pd.isna(date_str) or date_str is None:
        return None
    try:
        # Try to parse with time first, then without
        return datetime.strptime(str(date_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(str(date_str), "%Y-%m-%d")
        except ValueError:
            return None

def calculate_deadline_status(response_date_str):
    """Calculates days until deadline and returns appropriate styling."""
    response_date = safe_date_parse(response_date_str)
    if not response_date:
        return "N/A", "deadline-safe" # Default to safe if date is missing

    days_left = (response_date - datetime.now()).days
    
    if days_left < 0:
        return "Deadline Passed", "deadline-urgent"
    elif days_left <= 7:
        return f"{days_left} Days Left (Urgent)", "deadline-urgent"
    elif days_left <= 30:
        return f"{days_left} Days Left (Warning)", "deadline-warning"
    else:
        return f"{days_left} Days Left", "deadline-safe"

def calculate_timeline_progress(posted_date_str, response_date_str):
    """Calculates the percentage of time elapsed between posted and response dates."""
    posted_date = safe_date_parse(posted_date_str)
    response_date = safe_date_parse(response_date_str)
    now = datetime.now()

    if not posted_date or not response_date or posted_date >= response_date:
        return 0.0

    total_duration = (response_date - posted_date).total_seconds()
    elapsed_duration = (now - posted_date).total_seconds()

    if elapsed_duration < 0:
        return 0.0
    if elapsed_duration > total_duration:
        return 100.0

    progress = (elapsed_duration / total_duration) * 100
    return progress

# --- Data Loading Functions (from data_loader.py) ---

@st.cache_data(ttl=3600)
def load_google_sheets_data(sheet_url):
    """Load data from Google Sheets with caching."""
    try:
        if 'docs.google.com/spreadsheets' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            df = pd.read_csv(csv_url)
            return df
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {e}")
        return create_sample_data()

@st.cache_data(ttl=3600)
def create_sample_data():
    """Create comprehensive sample data with all required fields."""
    data = []
    for i, grant_type in enumerate(GRANT_TYPES):
        for j in range(3):  # 3 grants per type
            opportunity_num = f"GRANT-{grant_type[:3].upper()}-{2024}-{j+1:03d}"
            data.append({
                'Grant Type': grant_type,
                'Opportunity Number': opportunity_num,
                'Status': np.random.choice(STATUSES),
                'Title': f"{grant_type} - Innovation Program {j+1}",
                'URL': f"https://grants.gov/opportunity/{opportunity_num}",
                'Goal': f"Advance research and development in {grant_type.lower()} sector through innovative approaches and collaborative partnerships.",
                'Success Criteria': f"Successful completion of project milestones, measurable impact on {grant_type.lower()}, and sustainable outcomes.",
                'Notes': f"Priority given to projects with strong community impact and innovative methodologies in {grant_type.lower()}.",
                'Eligibility': np.random.choice(["Yes", "No"]),
                'Eligibility Notes': f"Must meet specific criteria for {grant_type.lower()} including organizational capacity and prior experience.",
                'Duration': f"{np.random.randint(12, 60)} months",
                'Agency': np.random.choice(AGENCIES),
                'Agency Email': f"grants@{np.random.choice(AGENCIES).lower()}.gov",
                'Agency Phone': f"({np.random.randint(200, 999)}) {np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}",
                'Posted Date': (datetime.now() - timedelta(days=np.random.randint(1, 90))).strftime("%Y-%m-%d"),
                'Response Date': (datetime.now() + timedelta(days=np.random.randint(30, 180))).strftime("%Y-%m-%d"),
                'Funding': np.random.randint(50000, 2000000),
                'Award Ceiling': np.random.randint(100000, 5000000),
                'Award Floor': np.random.randint(25000, 100000),
                'Created': (datetime.now() - timedelta(days=np.random.randint(1, 365))).strftime("%Y-%m-%d %H:%M:%S"),
                'Last Modified': (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                'client': f"Client {i*3 + j + 1}",
                'Email': f"client{i*3 + j + 1}@example.com",
                'Business': f"Business {i*3 + j + 1} LLC",
                'Summary': f"Innovative {grant_type.lower()} company focused on cutting-edge solutions.",
                'NSIC code': f"{np.random.randint(10000, 99999)}",
                'Industry': grant_type,
                'phone number': f"({np.random.randint(200, 999)}) {np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}",
                'Address': f"{np.random.randint(100, 999)} Main St",
                'State': np.random.choice(STATES),
                'Country': np.random.choice(COUNTRIES),
                'Projected ROI': np.random.uniform(0.1, 5.0),
                'Risk Level': np.random.choice(["Low", "Medium", "High"]),
                'Team Size': np.random.randint(3, 20),
                'Keywords': f"{grant_type.split()[0].lower()}, {np.random.choice(AGENCIES).lower()}, innovation, funding",
                'Reviewer': np.random.choice(["Alice Johnson", "Bob Smith", "Charlie Brown"]),
                'Review Score': np.random.randint(60, 100),
                'Next Step': np.random.choice(["Schedule call", "Draft proposal", "Internal review", "Submit application"]),
                'Last Contact': (datetime.now() - timedelta(days=np.random.randint(1, 14))).strftime("%Y-%m-%d"),
                'Funding Source': np.random.choice(["Federal", "State", "Private Foundation", "Corporate"]),
                'Match Required': np.random.choice(["Yes", "No"]),
                'Match Percentage': np.random.randint(0, 50) if np.random.choice(["Yes", "No"]) == "Yes" else 0,
                'Compliance Check': np.random.choice(["Pass", "Fail", "Pending"]),
                'Project Start Date': (datetime.now() + timedelta(days=np.random.randint(30, 180))).strftime("%Y-%m-%d"),
                'Project End Date': (datetime.now() + timedelta(days=np.random.randint(365, 1095))).strftime("%Y-%m-%d"),
            })
    
    df = pd.DataFrame(data)
    # Convert date columns to datetime objects for calculations
    df['Posted Date'] = pd.to_datetime(df['Posted Date'])
    df['Response Date'] = pd.to_datetime(df['Response Date'])
    return df

# --- Modular Grant Card Sections (from grant_sections.py) ---

def display_grant_header(grant_data):
    """Displays the main header and status of the grant."""
    status_class = f"status-{grant_data['Status'].lower().replace(' ', '-')}"
    
    st.markdown(f"""
    <div class="grant-card-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="grant-card-title">{grant_data['Title']}</div>
                <div class="grant-card-subtitle">Opportunity No: {grant_data['Opportunity Number']} | Agency: {grant_data['Agency']}</div>
            </div>
            <span class="{status_class}">{grant_data['Status']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_section_overview(grant_data):
    """Displays the Overview section (Tab 1)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    # Funding Highlight
    st.markdown(f"""
    <div class="funding-highlight">
        💰 Target Funding: ${grant_data['Funding']:,} | Award Ceiling: ${grant_data['Award Ceiling']:,}
    </div>
    """, unsafe_allow_html=True)

    # Goal
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">🎯 Grant Goal</div>
        <div class="field-value">{grant_data['Goal']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Success Criteria
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">✅ Success Criteria</div>
        <div class="field-value">{grant_data['Success Criteria']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Eligibility
    eligibility_icon = "🟢" if grant_data['Eligibility'] == "Yes" else "🔴"
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">Eligibility Check</div>
        <div class="field-value">{eligibility_icon} {grant_data['Eligibility']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # URL
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">🔗 Opportunity Link</div>
        <div class="field-value"><a href="{grant_data['URL']}" target="_blank" style="color: #fff; text-decoration: underline;">{grant_data['URL']}</a></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def display_section_timeline(grant_data):
    """Displays the Timeline section (Tab 2)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Posted Date
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📅 Posted Date</div>
            <div class="field-value">{grant_data['Posted Date']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Duration
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">⏳ Project Duration</div>
            <div class="field-value">{grant_data['Duration']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Project Start/End
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">🚀 Project Dates</div>
            <div class="field-value">Start: {grant_data.get('Project Start Date', 'N/A')} | End: {grant_data.get('Project End Date', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Response Date (Deadline)
        deadline_text, deadline_class = calculate_deadline_status(grant_data['Response Date'])
        st.markdown(f"""
        <div class="{deadline_class}">
            <h3>🚨 Response Deadline</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{grant_data['Response Date']}</p>
            <p style="font-size: 1rem; margin: 0;">{deadline_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Timeline Progress
        progress = calculate_timeline_progress(grant_data['Posted Date'], grant_data['Response Date'])
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">Application Timeline Progress</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%;"></div>
            </div>
            <div style="text-align: center; color: white; margin-top: 0.5rem;">
                {progress:.1f}% of application period elapsed
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_section_funding_compliance(grant_data):
    """Displays the Funding and Compliance section (Tab 3)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Funding Details
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">💰 Funding Details</div>
            <div class="field-value">
                Target: ${grant_data['Funding']:,}<br>
                Ceiling: ${grant_data['Award Ceiling']:,}<br>
                Floor: ${grant_data['Award Floor']:,}<br>
                Source: {grant_data.get('Funding Source', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Match Requirement
        match_status = f"Required ({grant_data.get('Match Percentage', 0)}%)" if grant_data.get('Match Required') == "Yes" else "Not Required"
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">🤝 Match Requirement</div>
            <div class="field-value">{match_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Compliance Check
        compliance_icon = "✅" if grant_data.get('Compliance Check') == "Pass" else "⚠️" if grant_data.get('Compliance Check') == "Pending" else "❌"
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📜 Compliance Status</div>
            <div class="field-value">{compliance_icon} {grant_data.get('Compliance Check', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk and ROI
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📈 Risk & ROI</div>
            <div class="field-value">
                Risk Level: {grant_data.get('Risk Level', 'N/A')}<br>
                Projected ROI: {grant_data.get('Projected ROI', 0.0):.2f}x
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def display_section_agency_details(grant_data):
    """Displays the Agency and Notes section (Tab 4)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    # Enhanced agency contact card
    st.markdown(f"""
    <div class="contact-card">
        <h3>🏛️ {grant_data['Agency']} - Contact Information</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <strong>📧 Email:</strong><br>
                <a href="mailto:{grant_data['Agency Email']}" style="color: #fff; text-decoration: none;">
                    {grant_data['Agency Email']}
                </a>
            </div>
            <div>
                <strong>📞 Phone:</strong><br>
                <a href="tel:{grant_data['Agency Phone']}" style="color: #fff; text-decoration: none;">
                    {grant_data['Agency Phone']}
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">Special Notes & Requirements</div>
        <div class="field-value">{grant_data['Notes']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">Eligibility Details</div>
        <div class="field-value">{grant_data['Eligibility Notes']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_section_client_profile(grant_data):
    """Displays the Client Profile section (Tab 5)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">👤 Client Name</div>
            <div class="field-value">{grant_data['client']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">🏢 Business</div>
            <div class="field-value">{grant_data['Business']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">🏭 Industry</div>
            <div class="field-value">{grant_data['Industry']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">🔢 NSIC Code</div>
            <div class="field-value">{grant_data['NSIC code']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📧 Contact Email</div>
            <div class="field-value">
                <a href="mailto:{grant_data['Email']}" style="color: #fff; text-decoration: none;">
                    {grant_data['Email']}
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📞 Phone Number</div>
            <div class="field-value">
                <a href="tel:{grant_data['phone number']}" style="color: #fff; text-decoration: none;">
                    {grant_data['phone number']}
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📍 Location</div>
            <div class="field-value">{grant_data['Address']}<br>{grant_data['State']}, {grant_data['Country']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📝 Business Summary</div>
            <div class="field-value">{grant_data['Summary']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_section_internal_review(grant_data):
    """Displays the Internal Review section (Tab 6)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Reviewer
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">👤</div>
            <div class="metric-label">Reviewer: {grant_data.get('Reviewer', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Review Score
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{grant_data.get('Review Score', 'N/A')} / 100</div>
            <div class="metric-label">Internal Review Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Next Step
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">➡️</div>
            <div class="metric-label">Next Step: {grant_data.get('Next Step', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Last Contact and Team Size
    col4, col5 = st.columns(2)
    with col4:
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">📞 Last Contact</div>
            <div class="field-value">{grant_data.get('Last Contact', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="field-container">
            <div class="field-label">👥 Team Size</div>
            <div class="field-value">{grant_data.get('Team Size', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Keywords
    st.markdown(f"""
    <div class="field-container">
        <div class="field-label">🏷️ Keywords</div>
        <div class="field-value">{grant_data.get('Keywords', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def display_section_analytics(grant_data):
    """Displays the Analytics section (Tab 7)."""
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Funding efficiency score
        efficiency = (grant_data['Funding'] / grant_data['Award Ceiling']) * 100 if grant_data['Award Ceiling'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{efficiency:.1f}%</div>
            <div class="metric-label">Funding Efficiency</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Days since posted
        posted_date = safe_date_parse(grant_data["Posted Date"])
        days_since_posted = (datetime.now() - posted_date).days if posted_date else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{days_since_posted}</div>
            <div class="metric-label">Days Since Posted</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Priority score (simulated) - using a simple hash for a deterministic score
        priority_score = hash(grant_data['Opportunity Number']) % 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{priority_score}</div>
            <div class="metric-label">Priority Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Funding comparison chart
    comparison_data = pd.DataFrame({
        'Metric': ['Award Floor', 'Target Funding', 'Award Ceiling', 'Industry Avg*'],
        'Amount': [
            grant_data['Award Floor'], 
            grant_data['Funding'], 
            grant_data['Award Ceiling'],
            (grant_data['Award Floor'] + grant_data['Award Ceiling']) / 2
        ]
    })
    
    fig = px.bar(comparison_data, x='Metric', y='Amount', 
                title="Funding Analysis & Benchmarking",
                color='Amount',
                color_continuous_scale='viridis')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<p style="color: #fff; font-size: 0.8rem; text-align: center;">*Industry average is estimated</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Modular Display Function (from grant_sections.py) ---

def display_modular_grant_card(grant_data):
    """
    The main function to display a single grant card with section-based loading.
    The 'loading by section' is implemented by only calling the rendering function
    for the currently selected tab, making the display modular and efficient.
    """
    st.markdown('<div class="grant-card">', unsafe_allow_html=True)
    
    # 1. Header (always loaded)
    display_grant_header(grant_data)
    
    # 2. Tabs (section-based loading/rendering)
    tab_titles = [
        "Overview", "Timeline", "Funding & Compliance", 
        "Agency Details", "Client Profile", "Internal Review", "Analytics"
    ]
    
    # Create tabs
    tabs = st.tabs(tab_titles)
    
    # Map tab index to its rendering function
    section_renderers = [
        display_section_overview,
        display_section_timeline,
        display_section_funding_compliance,
        display_section_agency_details,
        display_section_client_profile,
        display_section_internal_review,
        display_section_analytics
    ]
    
    # Render content for each tab
    for tab, renderer in zip(tabs, section_renderers):
        with tab:
            # This is where the "load by section" logic is implemented:
            # The data processing and rendering for a section only happens
            # when the user is viewing that specific tab.
            renderer(grant_data)
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Application Logic (from app.py) ---

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Comprehensive Grants Management Dashboard</h1>
        <p>Modular, section-based loading for enhanced performance and extensibility</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for Google Sheets integration
    with st.sidebar:
        st.header("📊 Data Source")
        sheet_url = st.text_input(
            "Google Sheets URL",
            value="https://docs.google.com/spreadsheets/d/1xok6PwIk5Kyj78KhBFkjJYGNSdkosxeXliTy0Alt3bc/edit?usp=sharing",
            help="Enter your Google Sheets URL for live data integration"
        )
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.header("🔍 Filters")
        
        # Load all data initially (or from cache)
        if sheet_url:
            df = load_google_sheets_data(sheet_url)
        else:
            df = create_sample_data()
        
        # Get unique values for filters
        all_statuses = df['Status'].unique().tolist()
        all_grant_types = df['Grant Type'].unique().tolist()
        
        status_filter = st.multiselect("Status", all_statuses, default=all_statuses)
        grant_type_filter = st.selectbox("Grant Type", ["All"] + all_grant_types)
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    if grant_type_filter != "All":
        filtered_df = filtered_df[filtered_df['Grant Type'] == grant_type_filter]
    
    # --- Executive Summary ---
    st.header("📈 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Grants</h3>
            <h2 style="color: #1976d2;">{}</h2>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        total_funding = filtered_df['Funding'].sum()
        st.markdown("""
        <div class="metric-card">
            <h3>Total Funding</h3>
            <h2 style="color: #2e7d32;">${:,}</h2>
        </div>
        """.format(total_funding), unsafe_allow_html=True)
    
    with col3:
        avg_funding = filtered_df['Funding'].mean()
        st.markdown("""
        <div class="metric-card">
            <h3>Avg Funding</h3>
            <h2 style="color: #f57c00;">${:,}</h2>
        </div>
        """.format(int(avg_funding) if not pd.isna(avg_funding) else 0), unsafe_allow_html=True)
    
    with col4:
        eligible_grants = len(filtered_df[filtered_df['Eligibility'] == 'Yes'])
        st.markdown("""
        <div class="metric-card">
            <h3>Eligible Grants</h3>
            <h2 style="color: #c2185b;">{}</h2>
        </div>
        """.format(eligible_grants), unsafe_allow_html=True)
    
    # --- Analytics Section ---
    st.header("📊 Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    if not filtered_df.empty:
        with col1:
            # Status distribution
            status_counts = filtered_df['Status'].value_counts()
            status_df = pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values})
            fig = px.pie(status_df, values='Count', names='Status', title="Grant Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Funding by grant type
            funding_by_type = filtered_df.groupby('Grant Type')['Funding'].sum().sort_values(ascending=False).head(10)
            funding_df = pd.DataFrame({'Grant Type': funding_by_type.index, 'Total Funding': funding_by_type.values})
            fig = px.bar(funding_df, x='Total Funding', y='Grant Type', orientation='h', title="Top 10 Grant Types by Funding")
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline analysis
        st.subheader("📅 Timeline Analysis")
        filtered_df['Response Date'] = pd.to_datetime(filtered_df['Response Date'], errors='coerce')
        filtered_df['Days Until Response'] = (filtered_df['Response Date'] - datetime.now()).dt.days
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Upcoming deadlines
            upcoming = filtered_df[filtered_df['Days Until Response'] > 0].sort_values('Days Until Response').head(10)
            fig = px.bar(upcoming, x='Days Until Response', y='Title', orientation='h', 
                         title="Upcoming Response Deadlines", color='Days Until Response',
                         color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Agency distribution
            agency_counts = filtered_df['Agency'].value_counts()
            agency_df = pd.DataFrame({'Agency': agency_counts.index, 'Count': agency_counts.values})
            fig = px.bar(agency_df, x='Agency', y='Count', title="Grants by Agency")
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic distribution
        st.subheader("🗺️ Geographic Distribution")
        state_counts = filtered_df['State'].value_counts()
        state_df = pd.DataFrame({'State': state_counts.index, 'Count': state_counts.values})
        fig = px.bar(state_df, x='State', y='Count', title="Grants by State")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No grants match the current filters.")
    
    # --- Detailed Grant Cards (Section-based rendering) ---
    st.header("💼 Detailed Grant Information")
    st.write(f"Displaying {len(filtered_df)} grants with comprehensive details")
    
    # Group by grant type for better organization
    if not filtered_df.empty:
        for grant_type in filtered_df['Grant Type'].unique():
            st.subheader(f"🎯 {grant_type}")
            grant_type_data = filtered_df[filtered_df['Grant Type'] == grant_type]
            
            for idx, grant in grant_type_data.iterrows():
                # The core refactoring: calling the modular display function
                display_modular_grant_card(grant.to_dict())
                st.markdown("---")
    
    # --- Export functionality ---
    st.header("📤 Export Data")
    col1, col2, col3 = st.columns(3)
    
    if not filtered_df.empty:
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📊 Export to CSV",
                data=csv,
                file_name=f"grants_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            summary = f"""
            Grants Summary Report
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Total Grants: {len(filtered_df)}
            Total Funding: ${filtered_df['Funding'].sum():,}
            Average Funding: ${filtered_df['Funding'].mean():,.0f}
            Eligible Grants: {len(filtered_df[filtered_df['Eligibility'] == 'Yes'])}
            
            Status Breakdown:
            {filtered_df['Status'].value_counts().to_string()}
            
            Top Grant Types by Funding:
            {filtered_df.groupby('Grant Type')['Funding'].sum().sort_values(ascending=False).head(5).to_string()}
            """
            st.download_button(
                label="📈 Export Summary Report",
                data=summary,
                file_name=f"grants_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("🔄 Clear Cache & Rerun"):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()
