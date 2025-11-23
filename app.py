import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import urlparse
import numpy as np
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Advanced Grants Management Intelligence Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for premium styling
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
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
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
    .filter-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
    }
    .insight-card {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .recommendation-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .alert-box {
        background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%, #2BFF88 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
    .stats-container {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    .search-box {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_google_sheets_data(sheet_url):
    """Load data from Google Sheets with enhanced error handling"""
    try:
        if 'docs.google.com/spreadsheets' in sheet_url:
            # Extract sheet ID from URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            # Load data with error handling
            df = pd.read_csv(csv_url)
            
            # Data validation
            if df.empty:
                st.warning("Google Sheet is empty. Loading sample data instead.")
                return create_sample_data()
            
            st.success(f"✅ Successfully loaded {len(df)} grants from Google Sheets!")
            return df
        else:
            st.error("Invalid Google Sheets URL format")
            return create_sample_data()
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {e}")
        st.info("Loading comprehensive sample data for demonstration...")
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

def calculate_grant_score(grant_data):
    """Calculate a comprehensive grant opportunity score"""
    score = 0
    max_score = 100
    
    # Eligibility (30 points)
    if grant_data['Eligibility'] == 'Yes':
        score += 30
    
    # Status (20 points)
    status_scores = {'Interested': 20, 'Under Review': 15, 'New': 10, 'Not Interested': 0}
    score += status_scores.get(grant_data['Status'], 0)
    
    # Deadline urgency (20 points)
    response_date = safe_date_parse(grant_data['Response Date'])
    if response_date:
        days_left = (response_date - datetime.now()).days
        if days_left > 90:
            score += 20
        elif days_left > 30:
            score += 15
        elif days_left > 7:
            score += 10
        else:
            score += 5
    
    # Funding amount (30 points)
    funding = grant_data['Funding']
    if funding >= 1000000:
        score += 30
    elif funding >= 500000:
        score += 25
    elif funding >= 250000:
        score += 20
    elif funding >= 100000:
        score += 15
    else:
        score += 10
    
    return min(score, max_score)

def generate_insights(df):
    """Generate intelligent insights from the data"""
    insights = []
    
    # Funding insights
    total_funding = df['Funding'].sum()
    avg_funding = df['Funding'].mean()
    insights.append(f"💰 Total available funding across all grants: ${total_funding:,.0f}")
    insights.append(f"📊 Average grant size: ${avg_funding:,.0f}")
    
    # Eligibility insights
    eligible_count = len(df[df['Eligibility'] == 'Yes'])
    eligibility_rate = (eligible_count / len(df)) * 100
    insights.append(f"✅ {eligible_count} grants ({eligibility_rate:.1f}%) match your eligibility criteria")
    
    # Urgency insights
    urgent_grants = []
    for _, grant in df.iterrows():
        response_date = safe_date_parse(grant['Response Date'])
        if response_date:
            days_left = (response_date - datetime.now()).days
            if days_left < 14:
                urgent_grants.append(grant['Title'])
    
    if urgent_grants:
        insights.append(f"🚨 {len(urgent_grants)} grants have deadlines within 2 weeks!")
    
    # Status insights
    interested_count = len(df[df['Status'] == 'Interested'])
    insights.append(f"⭐ {interested_count} grants marked as 'Interested' - high priority opportunities")
    
    # Agency insights
    top_agency = df['Agency'].value_counts().head(1)
    if not top_agency.empty:
        insights.append(f"🏛️ Most active agency: {top_agency.index[0]} with {top_agency.values[0]} grant opportunities")
    
    return insights

def create_excel_download(df):
    """Create downloadable Excel file with formatted data"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All Grants', index=False)
        
        # Create summary sheet
        summary_data = {
            'Metric': ['Total Grants', 'Total Funding', 'Average Funding', 'Eligible Grants', 'Interested Grants'],
            'Value': [
                len(df),
                f"${df['Funding'].sum():,.0f}",
                f"${df['Funding'].mean():,.0f}",
                len(df[df['Eligibility'] == 'Yes']),
                len(df[df['Status'] == 'Interested'])
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    return output

def display_grant_card(grant_data):
    """Display comprehensive grant information as an enhanced card"""
    with st.container():
        # Calculate grant score
        grant_score = calculate_grant_score(grant_data)
        
        st.markdown(f"""
        <div class="grant-card">
            <div class="grant-card-header">
                <div class="grant-card-title">{grant_data['Title']}</div>
                <div class="grant-card-subtitle">Opportunity: {grant_data['Opportunity Number']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display grant score
        score_color = "#27ae60" if grant_score >= 70 else "#f39c12" if grant_score >= 40 else "#e74c3c"
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <div style="background: {score_color}; color: white; padding: 1rem; border-radius: 15px; display: inline-block;">
                <div style="font-size: 2rem; font-weight: bold;">{grant_score}/100</div>
                <div style="font-size: 0.9rem;">Opportunity Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced status display
        status_class = f"status-{grant_data['Status'].lower().replace(' ', '-')}"
        st.markdown(f'<div style="text-align: center; margin: 1rem 0;"><span class="{status_class}">{grant_data["Status"]}</span></div>', unsafe_allow_html=True)
        
        # Create enhanced tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📋 Overview", 
            "💰 Funding Details", 
            "📅 Timeline & Deadlines", 
            "🏢 Agency Info", 
            "👥 Client Details", 
            "📊 Analytics",
            "💡 Recommendations"
        ])
        
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
                eligibility_icon = "✅" if grant_data["Eligibility"] == "Yes" else "❌"
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Eligibility Status</div>
                    <div class="field-value" style="background-color: {eligibility_color}; font-weight: bold;">
                        {eligibility_icon} {grant_data["Eligibility"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if grant_data["Eligibility Notes"]:
                    st.markdown(f"""
                    <div class="field-container">
                        <div class="field-label">Eligibility Requirements</div>
                        <div class="field-value">{grant_data["Eligibility Notes"]}</div>
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
                
                if grant_data["Notes"]:
                    st.markdown(f"""
                    <div class="field-container">
                        <div class="field-label">Additional Notes</div>
                        <div class="field-value">{grant_data["Notes"]}</div>
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
                <br>Potential ROI: High Value Opportunity
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced funding visualization
            funding_data = pd.DataFrame({
                'Type': ['Minimum Award', 'Target Funding', 'Maximum Award'],
                'Amount': [grant_data['Award Floor'], grant_data['Funding'], grant_data['Award Ceiling']],
            })
            fig = px.bar(funding_data, x='Type', y='Amount', 
                        title="Funding Structure Breakdown",
                        color='Type',
                        color_discrete_map={
                            'Minimum Award': '#e74c3c',
                            'Target Funding': '#f39c12',
                            'Maximum Award': '#27ae60'
                        })
            fig.update_layout(
                showlegend=False, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Funding distribution gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=grant_data['Funding'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Target Funding Position"},
                delta={'reference': grant_data['Award Floor']},
                gauge={
                    'axis': {'range': [None, grant_data['Award Ceiling']]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [grant_data['Award Floor'], grant_data['Funding']], 'color': "lightgray"},
                        {'range': [grant_data['Funding'], grant_data['Award Ceiling']], 'color': "white"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': grant_data['Award Ceiling'] * 0.9
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
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
                        urgency_text = "URGENT - IMMEDIATE ACTION REQUIRED"
                    elif days_left < 30:
                        deadline_class = "deadline-warning"
                        urgency_icon = "⚠️"
                        urgency_text = "WARNING - DEADLINE APPROACHING"
                    else:
                        deadline_class = "deadline-safe"
                        urgency_icon = "✅"
                        urgency_text = "AMPLE TIME AVAILABLE"
                    
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
            
            # Timeline visualization
            if response_date:
                posted_date = safe_date_parse(grant_data["Posted Date"])
                if posted_date:
                    total_days = (response_date - posted_date).days
                    elapsed_days = (datetime.now() - posted_date).days
                    progress_percentage = (elapsed_days / total_days * 100) if total_days > 0 else 0
                    
                    st.markdown(f"""
                    <div class="field-container">
                        <div class="field-label">Application Window Progress</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress_percentage}%"></div>
                        </div>
                        <div style="text-align: center; color: white; margin-top: 0.5rem;">
                            {progress_percentage:.1f}% of application period elapsed
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Timeline visualization
                    timeline_data = pd.DataFrame({
                        'Stage': ['Posted', 'Current', 'Deadline'],
                        'Date': [posted_date, datetime.now(), response_date],
                        'Days': [0, elapsed_days, total_days]
                    })
                    
                    fig_timeline = px.scatter(timeline_data, x='Days', y=[1, 1, 1], 
                                             size=[15, 15, 15], 
                                             color='Stage',
                                             title="Grant Application Timeline",
                                             text='Stage',
                                             color_discrete_map={
                                                 'Posted': '#3498db',
                                                 'Current': '#f39c12',
                                                 'Deadline': '#e74c3c'
                                             })
                    fig_timeline.update_traces(textposition='top center')
                    fig_timeline.update_layout(
                        showlegend=False,
                        yaxis={'visible': False},
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=200
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="contact-card">
                <h3 style="margin-bottom: 1rem;">🏛️ Granting Agency Information</h3>
                <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">{grant_data["Agency"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📧 Email Contact</div>
                    <div class="field-value">
                        <a href="mailto:{grant_data['Agency Email']}" style="color: white; text-decoration: none;">
                            {grant_data['Agency Email']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">📞 Phone Number</div>
                    <div class="field-value">{grant_data["Agency Phone"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="recommendation-card">
                <strong>💡 Best Practices for Agency Contact:</strong><br>
                • Prepare specific questions before reaching out<br>
                • Reference the opportunity number in all communications<br>
                • Keep a log of all interactions<br>
                • Follow up within 48 hours of initial contact<br>
                • Request clarification on eligibility criteria if needed
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="contact-card">
                <h3 style="margin-bottom: 1rem;">👥 Client & Business Information</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Client Name</div>
                    <div class="field-value">{grant_data["client"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Business Name</div>
                    <div class="field-value">{grant_data["Business"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Email</div>
                    <div class="field-value">
                        <a href="mailto:{grant_data['Email']}" style="color: white; text-decoration: none;">
                            {grant_data['Email']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Phone</div>
                    <div class="field-value">{grant_data["phone number"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Industry</div>
                    <div class="field-value">{grant_data["Industry"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">NAICS Code</div>
                    <div class="field-value">{grant_data["NSIC code"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Location</div>
                    <div class="field-value">{grant_data["State"]}, {grant_data["Country"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="field-container">
                    <div class="field-label">Address</div>
                    <div class="field-value">{grant_data["Address"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="field-container">
                <div class="field-label">Business Summary</div>
                <div class="field-value">{grant_data["Summary"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab6:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            st.subheader("📊 Grant Opportunity Analytics")
            
            # Competitive analysis
            col1, col2 = st.columns(2)
            with col1:
                # Score breakdown
                score_breakdown = {
                    'Eligibility': 30 if grant_data['Eligibility'] == 'Yes' else 0,
                    'Status Priority': 20 if grant_data['Status'] == 'Interested' else 10,
                    'Deadline Factor': 15,
                    'Funding Level': 25
                }
                
                fig_breakdown = px.pie(
                    values=list(score_breakdown.values()),
                    names=list(score_breakdown.keys()),
                    title="Opportunity Score Breakdown"
                )
                fig_breakdown.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_breakdown, use_container_width=True)
            
            with col2:
                # Funding comparison
                funding_comparison = pd.DataFrame({
                    'Metric': ['Floor', 'Target', 'Ceiling', 'Median'],
                    'Value': [
                        grant_data['Award Floor'],
                        grant_data['Funding'],
                        grant_data['Award Ceiling'],
                        (grant_data['Award Floor'] + grant_data['Award Ceiling']) / 2
                    ]
                })
                
                fig_comp = px.bar(funding_comparison, x='Metric', y='Value',
                                 title="Funding Metrics Comparison",
                                 color='Metric')
                fig_comp.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            
            # Success probability indicator
            success_prob = min((grant_score / 100) * 100, 95)
            st.markdown(f"""
            <div class="insight-card">
                <h3>🎯 Success Probability Analysis</h3>
                <div style="font-size: 3rem; font-weight: bold; text-align: center; margin: 1rem 0;">
                    {success_prob:.1f}%
                </div>
                <div style="text-align: center;">
                    Based on eligibility, timing, funding level, and strategic fit
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab7:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            
            st.subheader("💡 Strategic Recommendations")
            
            # Generate personalized recommendations
            recommendations = []
            
            if grant_data['Eligibility'] == 'Yes':
                recommendations.append("✅ <strong>Eligibility Confirmed:</strong> You meet the basic requirements. Priority: HIGH")
            else:
                recommendations.append("⚠️ <strong>Eligibility Issue:</strong> Review requirements carefully or consider partnership opportunities")
            
            response_date = safe_date_parse(grant_data['Response Date'])
            if response_date:
                days_left = (response_date - datetime.now()).days
                if days_left < 14:
                    recommendations.append(f"🚨 <strong>Urgent Action Required:</strong> Only {days_left} days until deadline - start application immediately")
                elif days_left < 30:
                    recommendations.append(f"⚠️ <strong>Time Sensitive:</strong> {days_left} days remaining - begin preparation this week")
                else:
                    recommendations.append(f"✅ <strong>Good Timeline:</strong> {days_left} days available - plan thoroughly")
            
            if grant_data['Funding'] >= 1000000:
                recommendations.append("💰 <strong>High-Value Opportunity:</strong> Significant funding available - consider assembling a strong team")
            elif grant_data['Funding'] >= 500000:
                recommendations.append("💵 <strong>Substantial Funding:</strong> Mid-tier opportunity with good potential ROI")
            
            if grant_data['Status'] == 'Interested':
                recommendations.append("⭐ <strong>Previously Flagged:</strong> This grant is marked as interested - review and take action")
            elif grant_data['Status'] == 'New':
                recommendations.append("🆕 <strong>New Opportunity:</strong> Recently discovered - evaluate fit and update status")
            
            # Display recommendations
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="font-size: 1.2rem; margin-bottom: 0.5rem;"><strong>Recommendation #{i}</strong></div>
                    <div>{rec}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Action checklist
            st.markdown("""
            <div class="insight-card">
                <h3>📋 Pre-Application Checklist</h3>
                <ul style="text-align: left; margin: 1rem 0;">
                    <li>Review full RFP and eligibility requirements</li>
                    <li>Assess organizational capacity and resources</li>
                    <li>Identify potential partners or collaborators</li>
                    <li>Draft preliminary project narrative</li>
                    <li>Prepare required documentation</li>
                    <li>Review budget requirements and constraints</li>
                    <li>Contact agency for clarification if needed</li>
                    <li>Set internal deadlines (1-2 weeks before submission)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function with enhanced features"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🌟 Advanced Grants Management Intelligence Platform</div>
        <div class="main-subtitle">Comprehensive Grant Discovery, Analysis & Strategic Planning</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google Sheets URL input
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL here. Make sure the sheet is shared publicly or with link access."
        )
        
        if st.button("🔄 Load Data", type="primary"):
            if sheet_url:
                st.session_state['df'] = load_google_sheets_data(sheet_url)
            else:
                st.warning("Please enter a Google Sheets URL")
        
        if st.button("📊 Load Sample Data"):
            st.session_state['df'] = create_sample_data()
            st.success(f"✅ Loaded {len(st.session_state['df'])} sample grants!")
        
        st.divider()
        
        # Display mode
        st.header("📱 Display Options")
        view_mode = st.radio(
            "View Mode",
            ["Dashboard Overview", "Detailed Grant Cards", "Data Table", "Analytics Hub"],
            help="Choose how you want to view your grants data"
        )
        
        st.divider()
        
        # Quick stats in sidebar
        if 'df' in st.session_state and not st.session_state['df'].empty:
            df = st.session_state['df']
            st.header("📊 Quick Stats")
            st.metric("Total Grants", len(df))
            st.metric("Total Funding", f"${df['Funding'].sum():,.0f}")
            st.metric("Avg Grant Size", f"${df['Funding'].mean():,.0f}")
            eligible = len(df[df['Eligibility'] == 'Yes'])
            st.metric("Eligible Grants", f"{eligible} ({(eligible/len(df)*100):.1f}%)")
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state['df'] = create_sample_data()
    
    df = st.session_state['df']
    
    if df.empty:
        st.warning("No data available. Please load data from Google Sheets or use sample data.")
        return
    
    # Main content based on view mode
    if view_mode == "Dashboard Overview":
        display_dashboard_overview(df)
    elif view_mode == "Detailed Grant Cards":
        display_grant_cards(df)
    elif view_mode == "Data Table":
        display_data_table(df)
    elif view_mode == "Analytics Hub":
        display_analytics_hub(df)

def display_dashboard_overview(df):
    """Display comprehensive dashboard overview"""
    st.header("📊 Executive Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Total Grants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${df['Funding'].sum()/1000000:.1f}M</div>
            <div class="metric-label">Total Funding</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        eligible_count = len(df[df['Eligibility'] == 'Yes'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{eligible_count}</div>
            <div class="metric-label">Eligible Grants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        interested_count = len(df[df['Status'] == 'Interested'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{interested_count}</div>
            <div class="metric-label">Interested</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_funding = df['Funding'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_funding/1000:.0f}K</div>
            <div class="metric-label">Avg Grant Size</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Insights section
    st.markdown("---")
    st.subheader("🔍 Intelligent Insights")
    
    insights = generate_insights(df)
    col1, col2 = st.columns(2)
    
    for i, insight in enumerate(insights):
        if i % 2 == 0:
            with col1:
                st.markdown(f"""
                <div class="insight-card">
                    {insight}
                </div>
                """, unsafe_allow_html=True)
        else:
            with col2:
                st.markdown(f"""
                <div class="insight-card">
                    {insight}
                </div>
                """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("---")
    st.subheader("📈 Visual Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = df['Status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Grant Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_status.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Funding by agency
        agency_funding = df.groupby('Agency')['Funding'].sum().sort_values(ascending=False).head(10)
        fig_agency = px.bar(
            x=agency_funding.index,
            y=agency_funding.values,
            title="Top 10 Agencies by Total Funding",
            labels={'x': 'Agency', 'y': 'Total Funding ($)'},
            color=agency_funding.values,
            color_continuous_scale='Viridis'
        )
        fig_agency.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_agency, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Eligibility breakdown
        eligibility_counts = df['Eligibility'].value_counts()
        fig_elig = px.bar(
            x=eligibility_counts.index,
            y=eligibility_counts.values,
            title="Eligibility Status Overview",
            labels={'x': 'Eligibility', 'y': 'Count'},
            color=eligibility_counts.index,
            color_discrete_map={'Yes': '#27ae60', 'No': '#e74c3c'}
        )
        fig_elig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_elig, use_container_width=True)
    
    with col2:
        # Grant types distribution
        grant_type_counts = df['Grant Type'].value_counts().head(10)
        fig_types = px.bar(
            x=grant_type_counts.values,
            y=grant_type_counts.index,
            orientation='h',
            title="Top 10 Grant Types",
            labels={'x': 'Count', 'y': 'Grant Type'},
            color=grant_type_counts.values,
            color_continuous_scale='Blues'
        )
        fig_types.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_types, use_container_width=True)
    
    # Timeline analysis
    st.markdown("---")
    st.subheader("📅 Timeline Analysis")
    
    # Calculate urgency metrics
    urgent_grants = []
    warning_grants = []
    safe_grants = []
    
    for _, grant in df.iterrows():
        response_date = safe_date_parse(grant['Response Date'])
        if response_date:
            days_left = (response_date - datetime.now()).days
            if days_left < 14:
                urgent_grants.append(grant)
            elif days_left < 30:
                warning_grants.append(grant)
            else:
                safe_grants.append(grant)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="deadline-urgent">
            🚨 URGENT<br>
            <div style="font-size: 2rem; font-weight: bold;">{len(urgent_grants)}</div>
            Grants due within 14 days
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="deadline-warning">
            ⚠️ WARNING<br>
            <div style="font-size: 2rem; font-weight: bold;">{len(warning_grants)}</div>
            Grants due within 30 days
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="deadline-safe">
            ✅ SAFE<br>
            <div style="font-size: 2rem; font-weight: bold;">{len(safe_grants)}</div>
            Grants due after 30 days
        </div>
        """, unsafe_allow_html=True)
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name="grants_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export
        excel_data = create_excel_download(df)
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name="grants_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        # JSON export
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="🔧 Download JSON",
            data=json_data,
            file_name="grants_data.json",
            mime="application/json",
            use_container_width=True
        )

def display_grant_cards(df):
    """Display detailed grant cards with advanced filtering"""
    st.header("🎯 Detailed Grant Explorer")
    
    # Advanced filtering section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("🔍 Advanced Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=df['Status'].unique().tolist(),
            default=df['Status'].unique().tolist()
        )
    
    with col2:
        eligibility_filter = st.multiselect(
            "Eligibility",
            options=df['Eligibility'].unique().tolist(),
            default=df['Eligibility'].unique().tolist()
        )
    
    with col3:
        agency_filter = st.multiselect(
            "Agency",
            options=df['Agency'].unique().tolist(),
            default=df['Agency'].unique().tolist()
        )
    
    with col4:
        grant_type_filter = st.multiselect(
            "Grant Type",
            options=df['Grant Type'].unique().tolist(),
            default=df['Grant Type'].unique().tolist()
        )
    
    # Funding range filter
    col1, col2 = st.columns(2)
    with col1:
        min_funding = st.number_input(
            "Minimum Funding ($)",
            min_value=0,
            max_value=int(df['Funding'].max()),
            value=0,
            step=10000
        )
    
    with col2:
        max_funding = st.number_input(
            "Maximum Funding ($)",
            min_value=0,
            max_value=int(df['Funding'].max()),
            value=int(df['Funding'].max()),
            step=10000
        )
    
    # Search box
    search_term = st.text_input(
        "🔍 Search grants by title, goal, or notes",
        placeholder="Enter keywords..."
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df[
        (df['Status'].isin(status_filter)) &
        (df['Eligibility'].isin(eligibility_filter)) &
        (df['Agency'].isin(agency_filter)) &
        (df['Grant Type'].isin(grant_type_filter)) &
        (df['Funding'] >= min_funding) &
        (df['Funding'] <= max_funding)
    ]
    
    # Apply search
    if search_term:
        search_mask = (
            filtered_df['Title'].str.contains(search_term, case=False, na=False) |
            filtered_df['Goal'].str.contains(search_term, case=False, na=False) |
            filtered_df['Notes'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Display results count
    st.markdown(f"""
    <div class="alert-box">
        Found {len(filtered_df)} grants matching your criteria
    </div>
    """, unsafe_allow_html=True)
    
    # Sorting options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Funding (High to Low)", "Funding (Low to High)", "Deadline (Soonest)", "Recently Posted", "Grant Score"]
        )
    
    # Apply sorting
    if sort_by == "Funding (High to Low)":
        filtered_df = filtered_df.sort_values('Funding', ascending=False)
    elif sort_by == "Funding (Low to High)":
        filtered_df = filtered_df.sort_values('Funding', ascending=True)
    elif sort_by == "Deadline (Soonest)":
        filtered_df['Response Date Parsed'] = filtered_df['Response Date'].apply(safe_date_parse)
        filtered_df = filtered_df.sort_values('Response Date Parsed', ascending=True)
    elif sort_by == "Recently Posted":
        filtered_df['Posted Date Parsed'] = filtered_df['Posted Date'].apply(safe_date_parse)
        filtered_df = filtered_df.sort_values('Posted Date Parsed', ascending=False)
    elif sort_by == "Grant Score":
        filtered_df['Score'] = filtered_df.apply(calculate_grant_score, axis=1)
        filtered_df = filtered_df.sort_values('Score', ascending=False)
    
    # Pagination
    items_per_page = 5
    total_pages = (len(filtered_df) - 1) // items_per_page + 1
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state['page'] > 0:
            st.session_state['page'] -= 1
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; font-size: 1.2rem; font-weight: bold;">
            Page {st.session_state['page'] + 1} of {total_pages}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️") and st.session_state['page'] < total_pages - 1:
            st.session_state['page'] += 1
    
    # Display grants for current page
    start_idx = st.session_state['page'] * items_per_page
    end_idx = start_idx + items_per_page
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    for _, grant in page_df.iterrows():
        display_grant_card(grant)

def display_data_table(df):
    """Display interactive data table with export options"""
    st.header("📊 Interactive Data Table")
    
    # Column selector
    st.subheader("🔧 Customize Columns")
    all_columns = df.columns.tolist()
    default_columns = ['Title', 'Grant Type', 'Status', 'Eligibility', 'Funding', 'Response Date', 'Agency']
    selected_columns = st.multiselect(
        "Select columns to display",
        options=all_columns,
        default=[col for col in default_columns if col in all_columns]
    )
    
    if not selected_columns:
        st.warning("Please select at least one column to display")
        return
    
    # Display table
    st.dataframe(
        df[selected_columns],
        use_container_width=True,
        height=600
    )
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Column Statistics")
    
    # Numeric columns statistics
    numeric_cols = df[selected_columns].select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        stats_df = df[numeric_cols].describe()
        st.dataframe(stats_df, use_container_width=True)
    
    # Export section
    st.markdown("---")
    st.subheader("📥 Export Filtered Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df[selected_columns].to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name="filtered_grants.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = df[selected_columns].to_json(orient='records', indent=2)
        st.download_button(
            label="🔧 Download as JSON",
            data=json_data,
            file_name="filtered_grants.json",
            mime="application/json",
            use_container_width=True
        )

def display_analytics_hub(df):
    """Display advanced analytics and insights"""
    st.header("📈 Analytics Intelligence Hub")
    
    # Create tabs for different analytics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Funding Analysis",
        "📅 Timeline Analytics",
        "🏢 Agency Insights",
        "📊 Performance Metrics",
        "🔮 Predictive Insights"
    ])
    
    with tab1:
        st.subheader("💰 Comprehensive Funding Analysis")
        
        # Funding distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${df['Funding'].sum():,.0f}</div>
                <div class="metric-label">Total Available Funding</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${df['Funding'].median():,.0f}</div>
                <div class="metric-label">Median Grant Size</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${df['Funding'].std():,.0f}</div>
                <div class="metric-label">Funding Std Dev</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Funding distribution histogram
        fig_dist = px.histogram(
            df,
            x='Funding',
            nbins=30,
            title="Funding Amount Distribution",
            labels={'Funding': 'Grant Amount ($)', 'count': 'Number of Grants'},
            color_discrete_sequence=['#667eea']
        )
        fig_dist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Funding by grant type
        grant_type_funding = df.groupby('Grant Type')['Funding'].agg(['sum', 'mean', 'count']).sort_values('sum', ascending=False).head(15)
        
        fig_type_funding = go.Figure()
        fig_type_funding.add_trace(go.Bar(
            x=grant_type_funding.index,
            y=grant_type_funding['sum'],
            name='Total Funding',
            marker_color='#667eea'
        ))
        fig_type_funding.update_layout(
            title="Top 15 Grant Types by Total Funding",
            xaxis_title="Grant Type",
            yaxis_title="Total Funding ($)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_type_funding, use_container_width=True)
        
        # Funding range analysis
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ceiling = px.box(
                df,
                y='Award Ceiling',
                title="Award Ceiling Distribution",
                color_discrete_sequence=['#27ae60']
            )
            fig_ceiling.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ceiling, use_container_width=True)
        
        with col2:
            fig_floor = px.box(
                df,
                y='Award Floor',
                title="Award Floor Distribution",
                color_discrete_sequence=['#e74c3c']
            )
            fig_floor.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_floor, use_container_width=True)
    
    with tab2:
        st.subheader("📅 Timeline and Deadline Analytics")
        
        # Deadline analysis
        deadline_data = []
        for _, grant in df.iterrows():
            response_date = safe_date_parse(grant['Response Date'])
            if response_date:
                days_left = (response_date - datetime.now()).days
                deadline_data.append({
                    'Title': grant['Title'],
                    'Days Left': days_left,
                    'Response Date': response_date,
                    'Urgency': 'Urgent' if days_left < 14 else 'Warning' if days_left < 30 else 'Safe'
                })
        
        if deadline_data:
            deadline_df = pd.DataFrame(deadline_data)
            
            # Urgency distribution
            urgency_counts = deadline_df['Urgency'].value_counts()
            fig_urgency = px.pie(
                values=urgency_counts.values,
                names=urgency_counts.index,
                title="Deadline Urgency Distribution",
                color=urgency_counts.index,
                color_discrete_map={'Urgent': '#e74c3c', 'Warning': '#f39c12', 'Safe': '#27ae60'}
            )
            fig_urgency.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_urgency, use_container_width=True)
            
            # Timeline scatter
            fig_timeline = px.scatter(
                deadline_df,
                x='Response Date',
                y='Days Left',
                color='Urgency',
                title="Grant Deadlines Timeline",
                hover_data=['Title'],
                color_discrete_map={'Urgent': '#e74c3c', 'Warning': '#f39c12', 'Safe': '#27ae60'}
            )
            fig_timeline.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Top 10 most urgent grants
            st.subheader("🚨 Top 10 Most Urgent Grants")
            urgent_df = deadline_df.sort_values('Days Left').head(10)
            
            for _, grant in urgent_df.iterrows():
                urgency_color = '#e74c3c' if grant['Urgency'] == 'Urgent' else '#f39c12'
                st.markdown(f"""
                <div style="background: {urgency_color}; color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <strong>{grant['Title']}</strong><br>
                    <small>Due in {grant['Days Left']} days - {grant['Response Date'].strftime('%Y-%m-%d')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("🏢 Agency Intelligence")
        
        # Agency statistics
        agency_stats = df.groupby('Agency').agg({
            'Funding': ['sum', 'mean', 'count'],
            'Opportunity Number': 'count'
        }).round(0)
        agency_stats.columns = ['Total Funding', 'Avg Funding', 'Grant Count', 'Opportunities']
        agency_stats = agency_stats.sort_values('Total Funding', ascending=False)
        
        # Top agencies by funding
        fig_agency_funding = px.bar(
            x=agency_stats.head(10).index,
            y=agency_stats.head(10)['Total Funding'],
            title="Top 10 Agencies by Total Funding",
            labels={'x': 'Agency', 'y': 'Total Funding ($)'},
            color=agency_stats.head(10)['Total Funding'],
            color_continuous_scale='Viridis'
        )
        fig_agency_funding.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_agency_funding, use_container_width=True)
        
        # Agency comparison
        col1, col2 = st.columns(2)
        
        with col1:
            fig_agency_count = px.pie(
                values=agency_stats['Grant Count'].head(8),
                names=agency_stats['Grant Count'].head(8).index,
                title="Top 8 Agencies by Grant Count"
            )
            fig_agency_count.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_agency_count, use_container_width=True)
        
        with col2:
            fig_agency_avg = px.bar(
                x=agency_stats.head(8).index,
                y=agency_stats.head(8)['Avg Funding'],
                title="Top 8 Agencies by Average Grant Size",
                color=agency_stats.head(8)['Avg Funding'],
                color_continuous_scale='Blues'
            )
            fig_agency_avg.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_agency_avg, use_container_width=True)
        
        # Agency details table
        st.subheader("📋 Detailed Agency Statistics")
        st.dataframe(agency_stats, use_container_width=True)
    
    with tab4:
        st.subheader("📊 Performance Metrics & KPIs")
        
        # Calculate opportunity scores for all grants
        df['Opportunity Score'] = df.apply(calculate_grant_score, axis=1)
        
        # Score distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_score = len(df[df['Opportunity Score'] >= 70])
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
                <div class="metric-value">{high_score}</div>
                <div class="metric-label">High Priority (70+)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            med_score = len(df[(df['Opportunity Score'] >= 40) & (df['Opportunity Score'] < 70)])
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
                <div class="metric-value">{med_score}</div>
                <div class="metric-label">Medium Priority (40-69)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            low_score = len(df[df['Opportunity Score'] < 40])
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
                <div class="metric-value">{low_score}</div>
                <div class="metric-label">Low Priority (<40)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Score distribution histogram
        fig_scores = px.histogram(
            df,
            x='Opportunity Score',
            nbins=20,
            title="Opportunity Score Distribution",
            color_discrete_sequence=['#667eea']
        )
        fig_scores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scores, use_container_width=True)
        
        # Top opportunities
        st.subheader("⭐ Top 10 Opportunities by Score")
        top_opportunities = df.nlargest(10, 'Opportunity Score')[['Title', 'Grant Type', 'Funding', 'Opportunity Score', 'Status', 'Eligibility']]
        
        for idx, (_, grant) in enumerate(top_opportunities.iterrows(), 1):
            score_color = "#27ae60" if grant['Opportunity Score'] >= 70 else "#f39c12"
            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>#{idx} - {grant['Title']}</strong><br>
                        <small>{grant['Grant Type']} | ${grant['Funding']:,} | {grant['Status']} | {grant['Eligibility']}</small>
                    </div>
                    <div style="background: {score_color}; padding: 1rem; border-radius: 10px; text-align: center; min-width: 80px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{grant['Opportunity Score']}</div>
                        <div style="font-size: 0.8rem;">Score</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Status vs Eligibility matrix
        status_eligibility = pd.crosstab(df['Status'], df['Eligibility'])
        fig_matrix = px.imshow(
            status_eligibility,
            title="Status vs Eligibility Matrix",
            labels=dict(x="Eligibility", y="Status", color="Count"),
            color_continuous_scale='Viridis'
        )
        fig_matrix.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    with tab5:
        st.subheader("🔮 Predictive Insights & Recommendations")
        
        # Success probability analysis
        st.markdown("""
        <div class="insight-card">
            <h3>🎯 Strategic Opportunity Analysis</h3>
            <p>Based on comprehensive analysis of funding patterns, eligibility criteria, and deadline urgency.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate weighted metrics
        eligible_grants = df[df['Eligibility'] == 'Yes']
        eligible_funding = eligible_grants['Funding'].sum()
        total_funding = df['Funding'].sum()
        eligible_percentage = (eligible_funding / total_funding) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>💰 Funding Accessibility</h4>
                <div style="font-size: 2rem; font-weight: bold; text-align: center; margin: 1rem 0;">
                    {eligible_percentage:.1f}%
                </div>
                <p>Of total funding is from eligible grants</p>
                <p><strong>${eligible_funding:,.0f}</strong> accessible funding</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            interested_eligible = len(df[(df['Status'] == 'Interested') & (df['Eligibility'] == 'Yes')])
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>⭐ Priority Opportunities</h4>
                <div style="font-size: 2rem; font-weight: bold; text-align: center; margin: 1rem 0;">
                    {interested_eligible}
                </div>
                <p>Grants marked as interested AND eligible</p>
                <p><strong>High-value targets for immediate action</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommended actions
        st.markdown("""
        <div class="alert-box">
            <h3>🎯 Strategic Recommendations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        recommendations = [
            {
                'title': 'Focus on High-Priority Grants',
                'description': f'Prioritize the {high_score} grants with scores above 70. These offer the best combination of eligibility, funding, and timing.',
                'action': 'Review and begin applications for top-scored opportunities'
            },
            {
                'title': 'Address Urgent Deadlines',
                'description': f'{len([g for g in deadline_data if g["Urgency"] == "Urgent"])} grants have deadlines within 2 weeks.',
                'action': 'Immediate action required - allocate resources to urgent applications'
            },
            {
                'title': 'Leverage Agency Relationships',
                'description': f'Top agency "{agency_stats.index[0]}" has {int(agency_stats.iloc[0]["Grant Count"])} opportunities.',
                'action': 'Build relationships with program officers at high-volume agencies'
            },
            {
                'title': 'Optimize Resource Allocation',
                'description': f'Average grant size is ${df["Funding"].mean():,.0f} with significant variation.',
                'action': 'Balance portfolio between high-value and quick-win opportunities'
            }
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>📌 Recommendation #{i}: {rec['title']}</h4>
                <p><strong>Insight:</strong> {rec['description']}</p>
                <p><strong>Action:</strong> {rec['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Funding opportunity heatmap by grant type and status
        heatmap_data = df.groupby(['Grant Type', 'Status'])['Funding'].sum().unstack(fill_value=0)
        
        if not heatmap_data.empty:
            fig_heatmap = px.imshow(
                heatmap_data.head(15),
                title="Funding Distribution Heatmap: Top 15 Grant Types vs Status",
                labels=dict(x="Status", y="Grant Type", color="Total Funding"),
                color_continuous_scale='RdYlGn',
                aspect='auto'
            )
            fig_heatmap.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heatmap, use_container_width=True)

# Run the application
if __name__ == "__main__":
    main()
