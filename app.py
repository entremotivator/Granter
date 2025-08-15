import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import numpy as np
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Grant Management Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    .grant-type-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Grant types data
GRANT_TYPES = {
    "Small Business Innovation Research": {
        "description": "Federal funding for small businesses to engage in R&D",
        "max_amount": "$1,750,000",
        "deadline": "Varies by agency",
        "eligibility": "Small businesses with <500 employees"
    },
    "Small Business Technology Transfer": {
        "description": "Collaborative R&D between small businesses and research institutions",
        "max_amount": "$1,750,000", 
        "deadline": "Varies by agency",
        "eligibility": "Small businesses partnered with research institutions"
    },
    "Minority-Owned Business Grants": {
        "description": "Support for minority-owned business development",
        "max_amount": "$500,000",
        "deadline": "Rolling basis",
        "eligibility": "51% minority-owned businesses"
    },
    "Women-Owned Business Grants": {
        "description": "Funding for women entrepreneurs and business owners",
        "max_amount": "$350,000",
        "deadline": "Quarterly",
        "eligibility": "51% women-owned businesses"
    },
    "Rural Business Development Grants": {
        "description": "Economic development in rural communities",
        "max_amount": "$500,000",
        "deadline": "Annual",
        "eligibility": "Businesses in rural areas <50,000 population"
    },
    "Pell Grants": {
        "description": "Federal financial aid for undergraduate students",
        "max_amount": "$7,395",
        "deadline": "June 30",
        "eligibility": "Undergraduate students with financial need"
    },
    "Fulbright Program Grants": {
        "description": "International educational exchange program",
        "max_amount": "Varies",
        "deadline": "October 15",
        "eligibility": "U.S. citizens with bachelor's degree"
    },
    "National Science Foundation (NSF)": {
        "description": "Research funding across all fields of science and engineering",
        "max_amount": "$2,000,000+",
        "deadline": "Varies by program",
        "eligibility": "Universities, colleges, non-profit organizations"
    },
    "Teacher Quality Partnership Grants": {
        "description": "Improve teacher preparation programs",
        "max_amount": "$3,000,000",
        "deadline": "Annual",
        "eligibility": "Higher education institutions"
    },
    "Head Start Program Grants": {
        "description": "Early childhood education and development",
        "max_amount": "Varies",
        "deadline": "Annual",
        "eligibility": "Non-profit organizations, school districts"
    },
    "Community Development Block Grants": {
        "description": "Community development activities in low-income areas",
        "max_amount": "Varies",
        "deadline": "Annual",
        "eligibility": "Local governments, states"
    },
    "Arts & Culture Grants": {
        "description": "Support for arts organizations and cultural programs",
        "max_amount": "$100,000",
        "deadline": "Varies",
        "eligibility": "Arts organizations, cultural institutions"
    },
    "Health & Wellness Grants": {
        "description": "Public health initiatives and wellness programs",
        "max_amount": "$750,000",
        "deadline": "Quarterly",
        "eligibility": "Healthcare organizations, non-profits"
    },
    "Youth Development Grants": {
        "description": "Programs supporting youth development and education",
        "max_amount": "$250,000",
        "deadline": "Semi-annual",
        "eligibility": "Youth-serving organizations"
    },
    "Environmental Education Grants": {
        "description": "Environmental education and awareness programs",
        "max_amount": "$200,000",
        "deadline": "Annual",
        "eligibility": "Educational institutions, non-profits"
    },
    "Energy Efficiency and Renewable": {
        "description": "Clean energy and efficiency projects",
        "max_amount": "$5,000,000",
        "deadline": "Varies",
        "eligibility": "Businesses, organizations, governments"
    },
    "Agricultural Research Grants": {
        "description": "Research in agriculture and food systems",
        "max_amount": "$1,000,000",
        "deadline": "Annual",
        "eligibility": "Universities, research institutions"
    },
    "STEM Education Grants": {
        "description": "Science, technology, engineering, and math education",
        "max_amount": "$500,000",
        "deadline": "Annual",
        "eligibility": "Educational institutions"
    },
    "Biomedical Research Grants": {
        "description": "Medical and health research funding",
        "max_amount": "$2,500,000",
        "deadline": "Multiple deadlines",
        "eligibility": "Research institutions, universities"
    },
    "Technology Commercialization Grants": {
        "description": "Bringing research innovations to market",
        "max_amount": "$1,500,000",
        "deadline": "Quarterly",
        "eligibility": "Universities, research organizations"
    },
    "Veterans Assistance Grants": {
        "description": "Support services for veterans",
        "max_amount": "$300,000",
        "deadline": "Annual",
        "eligibility": "Veteran service organizations"
    },
    "Disaster Relief and Recovery Grants": {
        "description": "Emergency response and recovery assistance",
        "max_amount": "Varies",
        "deadline": "As needed",
        "eligibility": "Affected communities, organizations"
    },
    "Housing Assistance Grants": {
        "description": "Affordable housing development and assistance",
        "max_amount": "$2,000,000",
        "deadline": "Annual",
        "eligibility": "Housing authorities, non-profits"
    },
    "Accessibility Grants": {
        "description": "Improving accessibility for people with disabilities",
        "max_amount": "$150,000",
        "deadline": "Semi-annual",
        "eligibility": "Organizations serving disabled individuals"
    },
    "Cultural Preservation Grants": {
        "description": "Preserving cultural heritage and traditions",
        "max_amount": "$100,000",
        "deadline": "Annual",
        "eligibility": "Cultural organizations, museums"
    }
}

@st.cache_data
def load_google_sheets_data():
    """Load data from Google Sheets with error handling"""
    try:
        # Convert Google Sheets URL to CSV export URL
        sheet_id = "1xok6PwIk5Kyj78KhBFkjJYGNSdkosxeXliTy0Alt3bc"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        
        response = requests.get(csv_url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            st.warning("Could not load live data. Using sample data.")
            return generate_sample_data()
    except Exception as e:
        st.warning(f"Error loading data: {str(e)}. Using sample data.")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    states = ['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    industries = ['Technology', 'Healthcare', 'Manufacturing', 'Education', 'Agriculture', 
                 'Energy', 'Arts', 'Research', 'Non-profit', 'Government']
    
    data = []
    for i in range(200):
        data.append({
            'client': f'Client_{i+1}',
            'Email': f'client{i+1}@example.com',
            'Business': f'Business {i+1}',
            'Summary': f'Business summary for client {i+1}',
            'NSIC code': f'{np.random.randint(1000, 9999)}',
            'Industry': np.random.choice(industries),
            'phone number': f'+1-{np.random.randint(100,999)}-{np.random.randint(100,999)}-{np.random.randint(1000,9999)}',
            'State': np.random.choice(states),
            'Country': 'USA',
            'Address': f'{np.random.randint(100,9999)} Main St',
            'Grant_Type': np.random.choice(list(GRANT_TYPES.keys())),
            'Amount_Requested': np.random.randint(10000, 1000000),
            'Status': np.random.choice(['Pending', 'Approved', 'Rejected', 'Under Review']),
            'Application_Date': datetime.now() - timedelta(days=np.random.randint(1, 365))
        })
    
    return pd.DataFrame(data)

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Comprehensive Grant Management Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading grant data..."):
        df = load_google_sheets_data()
    
    # Dashboard Overview Section
    show_dashboard_overview(df)
    
    st.markdown("---")
    
    # Grant Types Section  
    show_grant_types(df)
    
    st.markdown("---")
    
    # Client Management Section
    show_client_management(df)
    
    st.markdown("---")
    
    # Analytics Section
    show_analytics(df)
    
    st.markdown("---")
    
    # Reports Section
    show_reports(df)
    
    # Comprehensive Footer with Additional Information
    st.markdown("---")
    st.markdown("### 📋 Grant Application Tips & Resources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📝 Application Best Practices:**
        - Start early and plan ahead
        - Read guidelines carefully
        - Provide clear, concise descriptions
        - Include all required documentation
        - Follow formatting requirements
        - Proofread before submission
        """)
    
    with col2:
        st.markdown("""
        **🔍 Research Tips:**
        - Identify funding priorities
        - Match your project to funder goals
        - Review successful applications
        - Network with program officers
        - Attend grant writing workshops
        - Join professional associations
        """)
    
    with col3:
        st.markdown("""
        **📊 Success Metrics:**
        - Track application deadlines
        - Monitor approval rates
        - Analyze feedback patterns
        - Build relationships with funders
        - Maintain detailed records
        - Plan for sustainability
        """)
    
    # Detailed Grant Calendar and Upcoming Deadlines
    st.markdown("---")
    st.markdown("### 📅 Upcoming Grant Deadlines")
    
    # Create sample upcoming deadlines
    upcoming_deadlines = pd.DataFrame({
        'Grant Type': [
            'NSF Research Grants', 'SBIR Phase I', 'Arts Council Grants',
            'Environmental Education', 'Youth Development', 'Healthcare Innovation',
            'Technology Transfer', 'Rural Development', 'Veterans Assistance'
        ],
        'Deadline': [
            '2025-09-15', '2025-09-30', '2025-10-15',
            '2025-10-31', '2025-11-15', '2025-11-30',
            '2025-12-15', '2025-12-31', '2026-01-15'
        ],
        'Max Amount': [
            '$2,000,000', '$1,750,000', '$100,000',
            '$200,000', '$250,000', '$750,000',
            '$1,500,000', '$500,000', '$300,000'
        ],
        'Days Until Deadline': [31, 46, 61, 77, 92, 107, 122, 138, 153]
    })
    
    # Color code by urgency
    def highlight_urgency(row):
        if row['Days Until Deadline'] <= 30:
            return ['background-color: #ffebee'] * len(row)
        elif row['Days Until Deadline'] <= 60:
            return ['background-color: #fff3e0'] * len(row)
        else:
            return ['background-color: #e8f5e8'] * len(row)
    
    styled_deadlines = upcoming_deadlines.style.apply(highlight_urgency, axis=1)
    st.dataframe(styled_deadlines, use_container_width=True, key="upcoming_deadlines_table")
    
    # Comprehensive Resource Links and Contact Information
    st.markdown("---")
    st.markdown("### 🔗 Additional Resources & Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🌐 Useful Websites:**
        - [Grants.gov](https://grants.gov) - Federal grant opportunities
        - [Foundation Directory](https://fconline.foundationcenter.org) - Private foundation grants
        - [SBIR.gov](https://sbir.gov) - Small business innovation research
        - [NSF.gov](https://nsf.gov) - National Science Foundation
        - [NIH.gov](https://nih.gov) - National Institutes of Health
        - [Arts.gov](https://arts.gov) - National Endowment for the Arts
        """)
        
        st.markdown("""
        **📚 Grant Writing Resources:**
        - Grant writing workshops and webinars
        - Professional grant writing associations
        - University research offices
        - Consultant directories
        - Template libraries
        - Peer review networks
        """)
    
    with col2:
        st.markdown("""
        **📞 Support Contacts:**
        - **Technical Support:** support@grantdashboard.com
        - **Grant Consultation:** consulting@grantdashboard.com  
        - **Training & Workshops:** training@grantdashboard.com
        - **Partnership Inquiries:** partnerships@grantdashboard.com
        - **Emergency Support:** 1-800-GRANTS-1
        """)
        
        st.markdown("""
        **🕒 Office Hours:**
        - Monday - Friday: 8:00 AM - 6:00 PM EST
        - Saturday: 10:00 AM - 2:00 PM EST
        - Sunday: Closed
        - Emergency support available 24/7
        """)

def show_dashboard_overview(df):
    """Display main dashboard overview"""
    st.header("📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_clients = len(df) if 'client' in df.columns else 0
        st.metric("Total Clients", total_clients)
    
    with col2:
        if 'Amount_Requested' in df.columns:
            total_amount = df['Amount_Requested'].sum()
            st.metric("Total Amount Requested", f"${total_amount:,.0f}")
        else:
            st.metric("Total Amount Requested", "$0")
    
    with col3:
        if 'Status' in df.columns:
            approved = len(df[df['Status'] == 'Approved'])
            st.metric("Approved Grants", approved)
        else:
            st.metric("Approved Grants", "0")
    
    with col4:
        if 'Status' in df.columns and len(df) > 0:
            approval_rate = (len(df[df['Status'] == 'Approved']) / len(df)) * 100
            st.metric("Approval Rate", f"{approval_rate:.1f}%")
        else:
            st.metric("Approval Rate", "0%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Industry' in df.columns:
            st.subheader("Clients by Industry")
            industry_counts = df['Industry'].value_counts()
            fig = px.pie(values=industry_counts.values, names=industry_counts.index)
            st.plotly_chart(fig, use_container_width=True, key="industry_pie_chart")
    
    with col2:
        if 'State' in df.columns:
            st.subheader("Clients by State")
            state_counts = df['State'].value_counts().head(10)
            fig = px.bar(x=state_counts.index, y=state_counts.values)
            fig.update_layout(xaxis_title="State", yaxis_title="Number of Clients")
            st.plotly_chart(fig, use_container_width=True, key="state_bar_chart")
    
    # Recent activity
    st.subheader("Recent Applications")
    if 'Application_Date' in df.columns:
        recent_df = df.nlargest(10, 'Application_Date')[['client', 'Business', 'Grant_Type', 'Status', 'Application_Date']]
        st.dataframe(recent_df, use_container_width=True, key="recent_applications_table")
    else:
        st.info("No recent application data available")

def show_grant_types(df):
    """Display grant types information"""
    st.header("📋 Grant Types")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("Search Grant Types", key="grant_search")
    with col2:
        show_all = st.checkbox("Show All Details", key="show_all_details")
    
    # Filter grant types based on search
    filtered_grants = GRANT_TYPES
    if search_term:
        filtered_grants = {k: v for k, v in GRANT_TYPES.items() 
                          if search_term.lower() in k.lower() or 
                          search_term.lower() in v['description'].lower()}
    
    # Display grant types
    for grant_name, grant_info in filtered_grants.items():
        with st.expander(f"💼 {grant_name}", expanded=show_all):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {grant_info['description']}")
                st.write(f"**Maximum Amount:** {grant_info['max_amount']}")
            
            with col2:
                st.write(f"**Deadline:** {grant_info['deadline']}")
                st.write(f"**Eligibility:** {grant_info['eligibility']}")
            
            # Show statistics if data available
            if 'Grant_Type' in df.columns:
                grant_data = df[df['Grant_Type'] == grant_name]
                if not grant_data.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Applications", len(grant_data))
                    with col2:
                        if 'Status' in df.columns:
                            approved = len(grant_data[grant_data['Status'] == 'Approved'])
                            st.metric("Approved", approved)
                    with col3:
                        if 'Amount_Requested' in df.columns:
                            avg_amount = grant_data['Amount_Requested'].mean()
                            st.metric("Avg. Amount", f"${avg_amount:,.0f}")

def show_client_management(df):
    """Display client management interface"""
    st.header("👥 Client Management")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_client = st.text_input("Search Clients", key="client_search")
    with col2:
        if 'Industry' in df.columns:
            industry_filter = st.selectbox("Filter by Industry", 
                                         ['All'] + list(df['Industry'].unique()), 
                                         key="industry_filter")
    with col3:
        if 'State' in df.columns:
            state_filter = st.selectbox("Filter by State", 
                                      ['All'] + list(df['State'].unique()), 
                                      key="state_filter")
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_client:
        filtered_df = filtered_df[
            filtered_df['client'].str.contains(search_client, case=False, na=False) |
            filtered_df['Business'].str.contains(search_client, case=False, na=False)
        ]
    
    if 'Industry' in df.columns and industry_filter != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == industry_filter]
    
    if 'State' in df.columns and state_filter != 'All':
        filtered_df = filtered_df[filtered_df['State'] == state_filter]
    
    # Display results
    st.write(f"Showing {len(filtered_df)} clients")
    
    if not filtered_df.empty:
        # Display client data
        display_columns = ['client', 'Business', 'Industry', 'State', 'Email']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_columns], 
            use_container_width=True,
            key="client_management_table"
        )
        
        # Export option
        if st.button("Export Client Data", key="export_clients"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"clients_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_clients_csv"
            )

def show_analytics(df):
    """Display analytics and insights"""
    st.header("📈 Analytics & Insights")
    
    if df.empty:
        st.warning("No data available for analytics")
        return
    
    # Time series analysis
    if 'Application_Date' in df.columns:
        st.subheader("Application Trends")
        df['Application_Date'] = pd.to_datetime(df['Application_Date'])
        daily_apps = df.groupby(df['Application_Date'].dt.date).size().reset_index()
        daily_apps.columns = ['Date', 'Applications']
        
        fig = px.line(daily_apps, x='Date', y='Applications', title="Daily Applications")
        st.plotly_chart(fig, use_container_width=True, key="daily_applications_chart")
    
    # Status analysis
    if 'Status' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Application Status Distribution")
            status_counts = df['Status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index)
            st.plotly_chart(fig, use_container_width=True, key="status_pie_chart")
        
        with col2:
            st.subheader("Success Rate by Grant Type")
            if 'Grant_Type' in df.columns:
                success_rate = df.groupby('Grant_Type')['Status'].apply(
                    lambda x: (x == 'Approved').sum() / len(x) * 100
                ).sort_values(ascending=False)
                
                fig = px.bar(x=success_rate.index, y=success_rate.values)
                fig.update_layout(xaxis_title="Grant Type", yaxis_title="Success Rate (%)")
                st.plotly_chart(fig, use_container_width=True, key="success_rate_chart")
    
    # Amount analysis
    if 'Amount_Requested' in df.columns:
        st.subheader("Funding Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Request", f"${df['Amount_Requested'].mean():,.0f}")
            st.metric("Median Request", f"${df['Amount_Requested'].median():,.0f}")
        
        with col2:
            st.metric("Total Requested", f"${df['Amount_Requested'].sum():,.0f}")
            if 'Status' in df.columns:
                approved_amount = df[df['Status'] == 'Approved']['Amount_Requested'].sum()
                st.metric("Total Approved", f"${approved_amount:,.0f}")

def show_reports(df):
    """Display reporting interface"""
    st.header("📊 Reports & Export")
    
    # Report options
    report_type = st.selectbox(
        "Select Report Type",
        ["Summary Report", "Client Report", "Grant Type Report", "Financial Report"],
        key="report_type_select"
    )
    
    if report_type == "Summary Report":
        st.subheader("Summary Report")
        
        # Generate summary statistics
        summary_data = {
            "Metric": ["Total Clients", "Total Applications", "Approved Applications", "Approval Rate"],
            "Value": [
                len(df),
                len(df) if 'Status' in df.columns else 0,
                len(df[df['Status'] == 'Approved']) if 'Status' in df.columns else 0,
                f"{(len(df[df['Status'] == 'Approved']) / len(df) * 100):.1f}%" if 'Status' in df.columns and len(df) > 0 else "0%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
    elif report_type == "Client Report":
        st.subheader("Client Report")
        if not df.empty:
            client_columns = ['client', 'Business', 'Industry', 'State', 'Email']
            available_columns = [col for col in client_columns if col in df.columns]
            st.dataframe(df[available_columns], use_container_width=True, key="client_report_table")
    
    # Export functionality
    st.subheader("Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Full Dataset", key="export_full"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Dataset (CSV)",
                data=csv,
                file_name=f"grant_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_full_csv"
            )
    
    with col2:
        if 'Status' in df.columns and st.button("Export Approved Only", key="export_approved"):
            approved_df = df[df['Status'] == 'Approved']
            csv = approved_df.to_csv(index=False)
            st.download_button(
                label="Download Approved Grants (CSV)",
                data=csv,
                file_name=f"approved_grants_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_approved_csv"
            )

if __name__ == "__main__":
    main()
