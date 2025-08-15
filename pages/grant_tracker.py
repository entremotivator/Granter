import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def show_grant_tracker():
    """Grant application tracking system"""
    st.header("Grant Application Tracker")
    
    # Sample tracking data
    if 'grant_applications' not in st.session_state:
        st.session_state.grant_applications = create_sample_applications()
    
    # Add new application
    with st.expander("➕ Add New Grant Application"):
        with st.form("new_application"):
            col1, col2 = st.columns(2)
            
            with col1:
                grant_name = st.text_input("Grant Name")
                grant_type = st.selectbox("Grant Type", 
                    ["Small Business Innovation Research", "NSF Grant", "Community Development"])
                amount_requested = st.number_input("Amount Requested ($)", min_value=0)
            
            with col2:
                application_date = st.date_input("Application Date")
                deadline = st.date_input("Deadline")
                status = st.selectbox("Status", 
                    ["Draft", "Submitted", "Under Review", "Approved", "Rejected"])
            
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Application"):
                new_app = {
                    'Grant Name': grant_name,
                    'Grant Type': grant_type,
                    'Amount Requested': amount_requested,
                    'Application Date': application_date,
                    'Deadline': deadline,
                    'Status': status,
                    'Notes': notes
                }
                st.session_state.grant_applications.append(new_app)
                st.success("Application added successfully!")
                st.rerun()
    
    # Display applications
    if st.session_state.grant_applications:
        df = pd.DataFrame(st.session_state.grant_applications)
        
        # Status filter
        status_filter = st.multiselect("Filter by Status", 
            df['Status'].unique(), default=df['Status'].unique())
        
        filtered_df = df[df['Status'].isin(status_filter)]
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Applications", len(filtered_df))
        with col2:
            approved = len(filtered_df[filtered_df['Status'] == 'Approved'])
            st.metric("Approved", approved)
        with col3:
            total_requested = filtered_df['Amount Requested'].sum()
            st.metric("Total Requested", f"${total_requested:,.0f}")
        with col4:
            success_rate = (approved / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Applications table
        st.subheader("Applications")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Status distribution chart
        col1, col2 = st.columns(2)
        with col1:
            status_counts = filtered_df['Status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                        title="Applications by Status")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            grant_type_amounts = filtered_df.groupby('Grant Type')['Amount Requested'].sum()
            fig = px.bar(x=grant_type_amounts.index, y=grant_type_amounts.values,
                        title="Requested Amount by Grant Type")
            st.plotly_chart(fig, use_container_width=True)

def create_sample_applications():
    """Create sample grant applications for demonstration"""
    return [
        {
            'Grant Name': 'Innovation Research Project',
            'Grant Type': 'Small Business Innovation Research',
            'Amount Requested': 150000,
            'Application Date': datetime.now() - timedelta(days=30),
            'Deadline': datetime.now() + timedelta(days=15),
            'Status': 'Under Review',
            'Notes': 'Submitted all required documents'
        },
        {
            'Grant Name': 'STEM Education Initiative',
            'Grant Type': 'NSF Grant',
            'Amount Requested': 250000,
            'Application Date': datetime.now() - timedelta(days=60),
            'Deadline': datetime.now() - timedelta(days=10),
            'Status': 'Approved',
            'Notes': 'Approved with full funding'
        },
        {
            'Grant Name': 'Community Center Renovation',
            'Grant Type': 'Community Development',
            'Amount Requested': 75000,
            'Application Date': datetime.now() - timedelta(days=45),
            'Deadline': datetime.now() + timedelta(days=30),
            'Status': 'Submitted',
            'Notes': 'Waiting for review'
        }
    ]
