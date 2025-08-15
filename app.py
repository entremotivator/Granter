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
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .grant-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .status-new { background-color: #e3f2fd; color: #1976d2; padding: 0.25rem 0.5rem; border-radius: 15px; }
    .status-review { background-color: #e0f2f1; color: #00796b; padding: 0.25rem 0.5rem; border-radius: 15px; }
    .status-interested { background-color: #e8f5e8; color: #2e7d32; padding: 0.25rem 0.5rem; border-radius: 15px; }
    .status-not-interested { background-color: #fafafa; color: #616161; padding: 0.25rem 0.5rem; border-radius: 15px; }
    .field-label { font-weight: bold; color: #1976d2; margin-top: 1rem; }
    .field-value { background-color: #f5f5f5; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem; }
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

def safe_date_parse(date_string, date_format="%Y-%m-%d"):
    """Safely parse date string with error handling"""
    try:
        if date_string and str(date_string).strip():
            return datetime.strptime(str(date_string), date_format)
        return None
    except (ValueError, TypeError):
        return None

def display_grant_card(grant_data):
    """Display comprehensive grant information as a card"""
    with st.container():
        st.markdown(f"""
        <div class="grant-card">
            <h3>{grant_data['Title']}</h3>
            <p><strong>Opportunity Number:</strong> {grant_data['Opportunity Number']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Basic Info", "💰 Funding", "📅 Timeline", "🏢 Agency", "👥 Client"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="field-label">Status</div>', unsafe_allow_html=True)
                status_class = f"status-{grant_data['Status'].lower().replace(' ', '-')}"
                st.markdown(f'<span class="{status_class}">{grant_data["Status"]}</span>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Grant Type</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Grant Type"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Duration</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Duration"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Eligibility</div>', unsafe_allow_html=True)
                eligibility_color = "green" if grant_data["Eligibility"] == "Yes" else "red"
                st.markdown(f'<div class="field-value" style="color: {eligibility_color};">{grant_data["Eligibility"]}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="field-label">URL</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value"><a href="{grant_data["URL"]}" target="_blank">{grant_data["URL"]}</a></div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Goal</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Goal"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Success Criteria</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Success Criteria"]}</div>', unsafe_allow_html=True)
        
        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Funding Amount", f"${grant_data['Funding']:,}")
            with col2:
                st.metric("Award Ceiling", f"${grant_data['Award Ceiling']:,}")
            with col3:
                st.metric("Award Floor", f"${grant_data['Award Floor']:,}")
            
            # Funding visualization
            funding_data = pd.DataFrame({
                'Type': ['Floor', 'Funding', 'Ceiling'],
                'Amount': [grant_data['Award Floor'], grant_data['Funding'], grant_data['Award Ceiling']]
            })
            fig = px.bar(funding_data, x='Type', y='Amount', title="Funding Structure")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="field-label">Posted Date</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Posted Date"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Created</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Created"]}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="field-label">Response Date</div>', unsafe_allow_html=True)
                response_date = safe_date_parse(grant_data["Response Date"])
                if response_date:
                    days_left = (response_date - datetime.now()).days
                    color = "red" if days_left < 30 else "orange" if days_left < 60 else "green"
                    st.markdown(f'<div class="field-value" style="color: {color};">{grant_data["Response Date"]} ({days_left} days left)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="field-value">Date not available</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Last Modified</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Last Modified"]}</div>', unsafe_allow_html=True)
        
        with tab4:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="field-label">Agency</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Agency"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Agency Email</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value"><a href="mailto:{grant_data["Agency Email"]}">{grant_data["Agency Email"]}</a></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="field-label">Agency Phone</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Agency Phone"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Notes</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Notes"]}</div>', unsafe_allow_html=True)
        
        with tab5:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="field-label">Client</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["client"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Business</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Business"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Industry</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Industry"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">NSIC Code</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["NSIC code"]}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="field-label">Email</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value"><a href="mailto:{grant_data["Email"]}">{grant_data["Email"]}</a></div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Phone</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["phone number"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Location</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Address"]}, {grant_data["State"]}, {grant_data["Country"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="field-label">Summary</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="field-value">{grant_data["Summary"]}</div>', unsafe_allow_html=True)

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
    df['Response Date'] = pd.to_datetime(df['Response Date'], errors='coerce')
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
