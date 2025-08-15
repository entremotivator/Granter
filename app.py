import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import urlparse
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Comprehensive Grants Management Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .grant-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .grant-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    .grant-card-header {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(5px);
    }
    .grant-card-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .grant-card-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    .metric-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        text-align: center;
        color: #2c3e50;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 1rem;
        font-weight: 500;
        color: #34495e;
    }
    .status-new { 
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white; 
        padding: 0.5rem 1rem; 
        border-radius: 25px; 
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    .status-review { 
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white; 
        padding: 0.5rem 1rem; 
        border-radius: 25px; 
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
    }
    .status-interested { 
        background: linear-gradient(45deg, #27ae60, #2ecc71);
        color: white; 
        padding: 0.5rem 1rem; 
        border-radius: 25px; 
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    }
    .status-not-interested { 
        background: linear-gradient(45deg, #95a5a6, #7f8c8d);
        color: white; 
        padding: 0.5rem 1rem; 
        border-radius: 25px; 
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3);
    }
    .field-container {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .field-label { 
        font-weight: bold; 
        color: #fff; 
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .field-value { 
        background: rgba(255,255,255,0.2);
        padding: 1rem; 
        border-radius: 10px; 
        margin-bottom: 1rem;
        color: #fff;
        font-size: 1rem;
        line-height: 1.5;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .tab-container {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .funding-highlight {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(238, 90, 36, 0.3);
    }
    .deadline-urgent {
        background: linear-gradient(45deg, #e74c3c, #c0392b);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    .deadline-warning {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .deadline-safe {
        background: linear-gradient(45deg, #27ae60, #2ecc71);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .contact-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .progress-bar {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
    }
    .progress-fill {
        background: linear-gradient(45deg, #27ae60, #2ecc71);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def load_google_sheets_data(sheet_url):
    """Load data from Google Sheets"""
    try:
        # Convert Google Sheets URL to CSV export URL
        if 'docs.google.com/spreadsheets' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            df = pd.read_csv(csv_url)
            return df
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create comprehensive sample data with all Airtable fields"""
    grant_types = [
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
    
    statuses = ["New", "Under Review", "Interested", "Not Interested"]
    agencies = ["NSF", "NIH", "DOE", "USDA", "SBA", "NEA", "HUD", "VA", "EPA", "DOD"]
    
    data = []
    for i, grant_type in enumerate(grant_types):
        for j in range(3):  # 3 grants per type
            opportunity_num = f"GRANT-{grant_type[:3].upper()}-{2024}-{j+1:03d}"
            data.append({
                'Grant Type': grant_type,
                'Opportunity Number': opportunity_num,
                'Status': np.random.choice(statuses),
                'Title': f"{grant_type} - Innovation Program {j+1}",
                'URL': f"https://grants.gov/opportunity/{opportunity_num}",
                'Goal': f"Advance research and development in {grant_type.lower()} sector through innovative approaches and collaborative partnerships.",
                'Success Criteria': f"Successful completion of project milestones, measurable impact on {grant_type.lower()}, and sustainable outcomes.",
                'Notes': f"Priority given to projects with strong community impact and innovative methodologies in {grant_type.lower()}.",
                'Eligibility': np.random.choice(["Yes", "No"]),
                'Eligibility Notes': f"Must meet specific criteria for {grant_type.lower()} including organizational capacity and prior experience.",
                'Duration': f"{np.random.randint(12, 60)} months",
                'Agency': np.random.choice(agencies),
                'Agency Email': f"grants@{np.random.choice(agencies).lower()}.gov",
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
                'State': np.random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']),
                'Country': 'USA',
                'Address': f"{np.random.randint(100, 9999)} Main St, City, State"
            })
    
    return pd.DataFrame(data)

def safe_date_parse(date_str):
    """Safely parse date strings with multiple format support"""
    if pd.isna(date_str) or date_str is None or date_str == '':
        return None
    
    date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except (ValueError, TypeError):
            continue
    
    return None

def display_grant_card(grant_data):
    """Display comprehensive grant information as an enhanced card"""
    with st.container():
        st.markdown(f"""
        <div class="grant-card">
            <div class="grant-card-header">
                <div class="grant-card-title">{grant_data['Title']}</div>
                <div class="grant-card-subtitle">Opportunity: {grant_data['Opportunity Number']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced status display
        status_class = f"status-{grant_data['Status'].lower().replace(' ', '-')}"
        st.markdown(f'<div style="text-align: center; margin: 1rem 0;"><span class="{status_class}">{grant_data["Status"]}</span></div>', unsafe_allow_html=True)
        
        # Create enhanced tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Overview", "💰 Funding Details", "📅 Timeline & Deadlines", "🏢 Agency Info", "👥 Client Details", "📊 Analytics"])
        
        with tab1:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Grant Type</div>
                    <div class="field-value">{grant_data["Grant Type"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Duration</div>
                    <div class="field-value">{grant_data["Duration"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                eligibility_color = "#27ae60" if grant_data["Eligibility"] == "Yes" else "#e74c3c"
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Eligibility Status</div>
                    <div class="field-value" style="background-color: {eligibility_color}; font-weight: bold;">
                        {grant_data["Eligibility"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Project Goal</div>
                    <div class="field-value">{grant_data["Goal"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Success Criteria</div>
                    <div class="field-value">{grant_data["Success Criteria"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # URL with enhanced styling
            st.markdown(f"""
            <div class="field-container">
                <div class="field-label">Application Portal</div>
                <div class="field-value">
                    <a href="{grant_data["URL"]}" target="_blank" style="color: #fff; text-decoration: none; font-weight: bold;">
                        🔗 {grant_data["URL"]}
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            # Enhanced funding metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${grant_data['Funding']:,}</div>
                    <div class="metric-label">Target Funding</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${grant_data['Award Ceiling']:,}</div>
                    <div class="metric-label">Maximum Award</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${grant_data['Award Floor']:,}</div>
                    <div class="metric-label">Minimum Award</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Funding range visualization
            funding_range = grant_data['Award Ceiling'] - grant_data['Award Floor']
            target_position = ((grant_data['Funding'] - grant_data['Award Floor']) / funding_range) * 100 if funding_range > 0 else 50
            
            st.markdown(f"""
            <div class="funding-highlight">
                💡 Funding Range: ${grant_data['Award Floor']:,} - ${grant_data['Award Ceiling']:,}
                <br>Target Position: {target_position:.1f}% of range
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced funding visualization
            funding_data = pd.DataFrame({
                'Type': ['Minimum', 'Target', 'Maximum'],
                'Amount': [grant_data['Award Floor'], grant_data['Funding'], grant_data['Award Ceiling']],
                'Color': ['#e74c3c', '#f39c12', '#27ae60']
            })
            fig = px.bar(funding_data, x='Type', y='Amount', color='Color', 
                        title="Funding Structure Overview",
                        color_discrete_map={'#e74c3c': '#e74c3c', '#f39c12': '#f39c12', '#27ae60': '#27ae60'})
            fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Posted Date</div>
                    <div class="field-value">📅 {grant_data["Posted Date"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Created</div>
                    <div class="field-value">🕐 {grant_data["Created"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Enhanced deadline display with urgency indicators
                response_date = safe_date_parse(grant_data["Response Date"])
                if response_date:
                    days_left = (response_date - datetime.now()).days
                    
                    if days_left < 7:
                        deadline_class = "deadline-urgent"
                        urgency_icon = "🚨"
                        urgency_text = "URGENT"
                    elif days_left < 30:
                        deadline_class = "deadline-warning"
                        urgency_icon = "⚠️"
                        urgency_text = "WARNING"
                    else:
                        deadline_class = "deadline-safe"
                        urgency_icon = "✅"
                        urgency_text = "SAFE"
                    
                    st.markdown(f"""
                    <div class="{deadline_class}">
                        {urgency_icon} {urgency_text}<br>
                        Response Due: {grant_data["Response Date"]}<br>
                        <strong>{days_left} days remaining</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="field-container">
                        <div class="field-label">Response Date</div>
                        <div class="field-value">📅 {grant_data["Response Date"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Last Modified</div>
                    <div class="field-value">🔄 {grant_data["Last Modified"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Timeline progress bar
            if response_date:
                posted_date = safe_date_parse(grant_data["Posted Date"])
                if posted_date:
                    total_days = (response_date - posted_date).days
                    elapsed_days = (datetime.now() - posted_date).days
                    progress = min((elapsed_days / total_days) * 100, 100) if total_days > 0 else 0
                    
                    st.markdown(f"""
                    <div style="margin: 2rem 0;">
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
        
        with tab4:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            # Enhanced agency contact card
            st.markdown(f"""
            <div class="contact-card">
                <h3>🏛️ {grant_data["Agency"]}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <strong>📧 Email:</strong><br>
                        <a href="mailto:{grant_data["Agency Email"]}" style="color: #fff; text-decoration: none;">
                            {grant_data["Agency Email"]}
                        </a>
                    </div>
                    <div>
                        <strong>📞 Phone:</strong><br>
                        <a href="tel:{grant_data["Agency Phone"]}" style="color: #fff; text-decoration: none;">
                            {grant_data["Agency Phone"]}
                        </a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="field-container">
                <div class="field-label">Special Notes & Requirements</div>
                <div class="field-value">{grant_data["Notes"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="field-container">
                <div class="field-label">Eligibility Details</div>
                <div class="field-value">{grant_data["Eligibility Notes"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">👤 Client Name</div>
                    <div class="field-value">{grant_data["client"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">🏢 Business</div>
                    <div class="field-value">{grant_data["Business"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">🏭 Industry</div>
                    <div class="field-value">{grant_data["Industry"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">🔢 NSIC Code</div>
                    <div class="field-value">{grant_data["NSIC code"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📧 Contact Email</div>
                    <div class="field-value">
                        <a href="mailto:{grant_data["Email"]}" style="color: #fff; text-decoration: none;">
                            {grant_data["Email"]}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📞 Phone Number</div>
                    <div class="field-value">
                        <a href="tel:{grant_data["phone number"]}" style="color: #fff; text-decoration: none;">
                            {grant_data["phone number"]}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📍 Location</div>
                    <div class="field-value">{grant_data["Address"]}<br>{grant_data["State"]}, {grant_data["Country"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📝 Business Summary</div>
                    <div class="field-value">{grant_data["Summary"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab6:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            # Enhanced analytics for individual grant
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Funding efficiency score
                efficiency = (grant_data['Funding'] / grant_data['Award Ceiling']) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{efficiency:.1f}%</div>
                    <div class="metric-label">Funding Efficiency</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Days since posted
                posted_date = safe_date_parse(grant_data["Posted Date"])
                if posted_date:
                    days_since_posted = (datetime.now() - posted_date).days
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{days_since_posted}</div>
                        <div class="metric-label">Days Since Posted</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                # Priority score (simulated)
                priority_score = hash(grant_data['Opportunity Number']) % 100
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{priority_score}</div>
                    <div class="metric-label">Priority Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Funding comparison chart
            comparison_data = pd.DataFrame({
                'Metric': ['Minimum', 'Target', 'Maximum', 'Industry Avg*'],
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

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Comprehensive Grants Management Dashboard</h1>
        <p>Live data integration with detailed grant tracking and analytics</p>
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
        
        st.header("🔍 Filters")
        status_filter = st.multiselect("Status", ["New", "Under Review", "Interested", "Not Interested"])
        grant_type_filter = st.selectbox("Grant Type", ["All"] + [
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
        ])
    
    # Load data
    df = create_sample_data()  # Using sample data for demo
    
    # Apply filters
    if status_filter:
        df = df[df['Status'].isin(status_filter)]
    if grant_type_filter != "All":
        df = df[df['Grant Type'] == grant_type_filter]
    
    # Executive Summary
    st.header("📈 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Grants</h3>
            <h2 style="color: #1976d2;">{}</h2>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        total_funding = df['Funding'].sum()
        st.markdown("""
        <div class="metric-card">
            <h3>Total Funding</h3>
            <h2 style="color: #2e7d32;">${:,}</h2>
        </div>
        """.format(total_funding), unsafe_allow_html=True)
    
    with col3:
        avg_funding = df['Funding'].mean()
        st.markdown("""
        <div class="metric-card">
            <h3>Avg Funding</h3>
            <h2 style="color: #f57c00;">${:,}</h2>
        </div>
        """.format(int(avg_funding)), unsafe_allow_html=True)
    
    with col4:
        eligible_grants = len(df[df['Eligibility'] == 'Yes'])
        st.markdown("""
        <div class="metric-card">
            <h3>Eligible Grants</h3>
            <h2 style="color: #7b1fa2;">{}</h2>
        </div>
        """.format(eligible_grants), unsafe_allow_html=True)
    
    # Analytics Section
    st.header("📊 Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = df['Status'].value_counts()
        status_df = pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values})
        fig = px.pie(status_df, values='Count', names='Status', title="Grant Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Funding by grant type
        funding_by_type = df.groupby('Grant Type')['Funding'].sum().sort_values(ascending=False).head(10)
        funding_df = pd.DataFrame({'Grant Type': funding_by_type.index, 'Total Funding': funding_by_type.values})
        fig = px.bar(funding_df, x='Total Funding', y='Grant Type', orientation='h', title="Top 10 Grant Types by Funding")
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline analysis
    st.subheader("📅 Timeline Analysis")
    df['Response Date'] = pd.to_datetime(df['Response Date'])
    df['Days Until Response'] = (df['Response Date'] - datetime.now()).dt.days
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Upcoming deadlines
        upcoming = df[df['Days Until Response'] > 0].sort_values('Days Until Response').head(10)
        fig = px.bar(upcoming, x='Days Until Response', y='Title', orientation='h', 
                     title="Upcoming Response Deadlines", color='Days Until Response',
                     color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Agency distribution
        agency_counts = df['Agency'].value_counts()
        agency_df = pd.DataFrame({'Agency': agency_counts.index, 'Count': agency_counts.values})
        fig = px.bar(agency_df, x='Agency', y='Count', title="Grants by Agency")
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic distribution
    st.subheader("🗺️ Geographic Distribution")
    state_counts = df['State'].value_counts()
    state_df = pd.DataFrame({'State': state_counts.index, 'Count': state_counts.values})
    fig = px.bar(state_df, x='State', y='Count', title="Grants by State")
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Grant Cards
    st.header("💼 Detailed Grant Information")
    st.write(f"Displaying {len(df)} grants with comprehensive details")
    
    # Group by grant type for better organization
    for grant_type in df['Grant Type'].unique():
        st.subheader(f"🎯 {grant_type}")
        grant_type_data = df[df['Grant Type'] == grant_type]
        
        for idx, grant in grant_type_data.iterrows():
            display_grant_card(grant)
            st.markdown("---")
    
    # Export functionality
    st.header("📤 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"grants_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Export Summary Report"):
            summary = f"""
            Grants Summary Report
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Total Grants: {len(df)}
            Total Funding: ${df['Funding'].sum():,}
            Average Funding: ${df['Funding'].mean():,.0f}
            Eligible Grants: {len(df[df['Eligibility'] == 'Yes'])}
            
            Status Breakdown:
            {df['Status'].value_counts().to_string()}
            
            Top Grant Types by Funding:
            {df.groupby('Grant Type')['Funding'].sum().sort_values(ascending=False).head(5).to_string()}
            """
            st.download_button(
                label="Download Report",
                data=summary,
                file_name=f"grants_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("🔄 Refresh All Data"):
            st.cache_data.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    main()

</merged_code>
