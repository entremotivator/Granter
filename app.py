import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
from io import StringIO

# Configure Streamlit page
st.set_page_config(
    page_title="Grant Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .grant-type-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #ff7f0e;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .search-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .filter-chip {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Grant types list based on the Google Sheets tabs
GRANT_TYPES = [
    "Small Business Innovation Research",
    "Small Business Technology Transfer", 
    "Minority-Owned Business Grants",
    "Women-Owned Business Grants",
    "Rural Business Development Grants",
    "Pell Grants",
    "Fulbright Program Grants",
    "National Science Foundation (NSF)",
    "Teacher Quality Partnership Grants",
    "Head Start Program Grants",
    "Community Development Block Grants",
    "Arts & Culture Grants",
    "Health & Wellness Grants",
    "Youth Development Grants",
    "Environmental Education Grants",
    "Energy Efficiency and Renewable",
    "Agricultural Research Grants",
    "STEM Education Grants",
    "Biomedical Research Grants",
    "Technology Commercialization Grants",
    "Veterans Assistance Grants",
    "Disaster Relief and Recovery Grants",
    "Housing Assistance Grants",
    "Accessibility Grants",
    "Cultural Preservation Grants"
]

# Grant categories configuration
GRANT_CATEGORIES = {
    "Business Grants": [
        "Small Business Innovation Research",
        "Small Business Technology Transfer", 
        "Minority-Owned Business Grants",
        "Women-Owned Business Grants",
        "Rural Business Development Grants"
    ],
    "Education Grants": [
        "Pell Grants",
        "Teacher Quality Partnership Grants",
        "Head Start Program Grants",
        "STEM Education Grants"
    ],
    "Health Grants": [
        "Health & Wellness Grants",
        "Biomedical Research Grants"
    ],
    "Community Grants": [
        "Community Development Block Grants",
        "Arts & Culture Grants",
        "Environmental Education Grants"
    ],
    "Other Grants": [
        "Energy Efficiency and Renewable",
        "Agricultural Research Grants",
        "Veterans Assistance Grants",
        "Disaster Relief and Recovery Grants",
        "Housing Assistance Grants",
        "Accessibility Grants",
        "Cultural Preservation Grants"
    ]
}

# Initialize session state for search and filters
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'saved_filters' not in st.session_state:
    st.session_state.saved_filters = {}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheets_data(sheet_id, sheet_name="Sheet1"):
    """Load data from Google Sheets"""
    try:
        # Convert Google Sheets URL to CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            # Read CSV data
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            return df
        else:
            st.error(f"Failed to load data from sheet: {sheet_name}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_sample_data():
    """Create sample data for demonstration"""
    import random
    
    # Sample client data
    clients_data = {
        'client': [f'Client_{i}' for i in range(1, 51)],
        'Email': [f'client{i}@example.com' for i in range(1, 51)],
        'Business': [f'Business_{i}' for i in range(1, 51)],
        'Summary': [f'Business summary for client {i}' for i in range(1, 51)],
        'Nsic code': [f'NSIC{1000+i}' for i in range(1, 51)],
        'Industry': random.choices(['Technology', 'Healthcare', 'Manufacturing', 'Agriculture', 'Education', 'Energy'], k=50),
        'phone number': [f'+1-555-{1000+i}' for i in range(1, 51)],
        'State': random.choices(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'], k=50),
        'Country': ['USA'] * 50,
        'Address': [f'{100+i} Main St, City {i}' for i in range(1, 51)]
    }
    
    return pd.DataFrame(clients_data)

def global_search_interface():
    """Global search interface in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Global Search")
    
    # Global search input
    global_search = st.sidebar.text_input(
        "Search across all data", 
        placeholder="Search grants, clients, industries...",
        key="global_search"
    )
    
    if global_search:
        # Add to search history
        if global_search not in st.session_state.search_history:
            st.session_state.search_history.insert(0, global_search)
            st.session_state.search_history = st.session_state.search_history[:10]  # Keep last 10
        
        # Show search results
        show_global_search_results(global_search)
    
    # Search history
    if st.session_state.search_history:
        st.sidebar.subheader("Recent Searches")
        for search in st.session_state.search_history[:5]:
            if st.sidebar.button(f"🔍 {search}", key=f"history_{search}"):
                st.session_state.global_search = search
                st.rerun()

def show_global_search_results(query):
    """Show global search results"""
    st.sidebar.markdown("**Search Results:**")
    
    # Search in grant types
    matching_grants = [grant for grant in GRANT_TYPES if query.lower() in grant.lower()]
    if matching_grants:
        st.sidebar.markdown("**Grant Types:**")
        for grant in matching_grants[:3]:
            st.sidebar.markdown(f"• {grant}")
    
    # Search suggestions
    suggestions = generate_search_suggestions(query)
    if suggestions:
        st.sidebar.markdown("**Suggestions:**")
        for suggestion in suggestions:
            st.sidebar.markdown(f"• {suggestion}")

def generate_search_suggestions(query):
    """Generate search suggestions based on query"""
    suggestions = []
    
    # Industry suggestions
    industries = ['Technology', 'Healthcare', 'Manufacturing', 'Agriculture', 'Education', 'Energy']
    matching_industries = [ind for ind in industries if query.lower() in ind.lower()]
    suggestions.extend([f"Filter by {ind}" for ind in matching_industries])
    
    # Grant category suggestions
    for category, grants in GRANT_CATEGORIES.items():
        if query.lower() in category.lower():
            suggestions.append(f"Browse {category}")
    
    return suggestions[:3]

def advanced_search_interface():
    """Advanced search interface"""
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.subheader("🔍 Advanced Search & Filters")
    
    # Search tabs
    search_tab1, search_tab2, search_tab3 = st.tabs(["🔍 Quick Search", "🎯 Advanced Filters", "💾 Saved Searches"])
    
    with search_tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "Search", 
                placeholder="Enter keywords, grant names, or criteria...",
                key="advanced_search_query"
            )
        
        with col2:
            search_type = st.selectbox("Search In", 
                ["All", "Grant Types", "Clients", "Industries"])
        
        with col3:
            if st.button("🔍 Search", type="primary"):
                if search_query:
                    st.session_state.current_search = {
                        'query': search_query,
                        'type': search_type,
                        'timestamp': datetime.now()
                    }
    
    with search_tab2:
        show_advanced_filters()
    
    with search_tab3:
        show_saved_searches()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show search results if available
    if hasattr(st.session_state, 'current_search'):
        show_search_results(st.session_state.current_search)

def show_advanced_filters():
    """Show advanced filtering options"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Grant Filters")
        
        # Grant category multi-select
        selected_categories = st.multiselect(
            "Grant Categories",
            list(GRANT_CATEGORIES.keys()),
            key="filter_categories"
        )
        
        # Funding range filter
        funding_range = st.select_slider(
            "Funding Range",
            options=["$0-25K", "$25K-50K", "$50K-100K", "$100K-250K", "$250K-500K", "$500K+"],
            value=("$0-25K", "$500K+"),
            key="filter_funding"
        )
        
        # Deadline filter
        deadline_filter = st.selectbox(
            "Application Deadline",
            ["All", "Rolling", "Annual", "Quarterly", "Monthly"],
            key="filter_deadline"
        )
    
    with col2:
        st.subheader("Client Filters")
        
        # Industry multi-select
        industries = ['Technology', 'Healthcare', 'Manufacturing', 'Agriculture', 'Education', 'Energy']
        selected_industries = st.multiselect(
            "Industries",
            industries,
            key="filter_industries"
        )
        
        # State multi-select
        states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        selected_states = st.multiselect(
            "States",
            states,
            key="filter_states"
        )
        
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=[datetime(2024, 1, 1), datetime.now()],
            key="filter_date_range"
        )
    
    # Apply filters button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎯 Apply Filters", type="primary"):
            apply_advanced_filters(selected_categories, selected_industries, selected_states, funding_range, deadline_filter, date_range)
    
    with col2:
        if st.button("💾 Save Filter Set"):
            save_filter_set(selected_categories, selected_industries, selected_states, funding_range, deadline_filter, date_range)
    
    with col3:
        if st.button("🔄 Clear All Filters"):
            clear_all_filters()

def apply_advanced_filters(categories, industries, states, funding_range, deadline, date_range):
    """Apply advanced filters"""
    st.session_state.active_filters = {
        'categories': categories,
        'industries': industries,
        'states': states,
        'funding_range': funding_range,
        'deadline': deadline,
        'date_range': date_range,
        'applied_at': datetime.now()
    }
    st.success("Filters applied successfully!")

def save_filter_set(categories, industries, states, funding_range, deadline, date_range):
    """Save current filter set"""
    filter_name = st.text_input("Filter Set Name", placeholder="Enter a name for this filter set")
    
    if filter_name:
        st.session_state.saved_filters[filter_name] = {
            'categories': categories,
            'industries': industries,
            'states': states,
            'funding_range': funding_range,
            'deadline': deadline,
            'date_range': date_range,
            'created_at': datetime.now()
        }
        st.success(f"Filter set '{filter_name}' saved!")

def show_saved_searches():
    """Show saved search and filter sets"""
    if st.session_state.saved_filters:
        st.subheader("Saved Filter Sets")
        
        for name, filters in st.session_state.saved_filters.items():
            with st.expander(f"📁 {name}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Created:** {filters['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    if filters['categories']:
                        st.write(f"**Categories:** {', '.join(filters['categories'])}")
                    if filters['industries']:
                        st.write(f"**Industries:** {', '.join(filters['industries'])}")
                    if filters['states']:
                        st.write(f"**States:** {', '.join(filters['states'])}")
                
                with col2:
                    if st.button(f"Apply", key=f"apply_{name}"):
                        load_saved_filter(name)
                    if st.button(f"Delete", key=f"delete_{name}"):
                        del st.session_state.saved_filters[name]
                        st.rerun()
    else:
        st.info("No saved filter sets yet. Create some using the Advanced Filters tab!")

def load_saved_filter(name):
    """Load a saved filter set"""
    filters = st.session_state.saved_filters[name]
    st.session_state.active_filters = filters
    st.success(f"Loaded filter set: {name}")

def clear_all_filters():
    """Clear all active filters"""
    if 'active_filters' in st.session_state:
        del st.session_state.active_filters
    st.success("All filters cleared!")

def show_search_results(search_info):
    """Show search results"""
    st.subheader(f"🔍 Search Results for: '{search_info['query']}'")
    
    query = search_info['query'].lower()
    search_type = search_info['type']
    
    # Search in different data types based on selection
    if search_type in ["All", "Grant Types"]:
        matching_grants = [grant for grant in GRANT_TYPES if query in grant.lower()]
        if matching_grants:
            st.write(f"**Found {len(matching_grants)} matching grant types:**")
            
            # Display as cards
            for grant in matching_grants:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{grant}**")
                        st.write(get_grant_description(grant))
                    with col2:
                        if st.button(f"View Details", key=f"search_result_{grant}"):
                            st.session_state.selected_grant = grant
                            st.rerun()
    
    # Show active filters if any
    if hasattr(st.session_state, 'active_filters'):
        show_active_filters()

def show_active_filters():
    """Display currently active filters"""
    st.subheader("🎯 Active Filters")
    
    filters = st.session_state.active_filters
    filter_chips = []
    
    if filters.get('categories'):
        for cat in filters['categories']:
            filter_chips.append(f"Category: {cat}")
    
    if filters.get('industries'):
        for ind in filters['industries']:
            filter_chips.append(f"Industry: {ind}")
    
    if filters.get('states'):
        for state in filters['states']:
            filter_chips.append(f"State: {state}")
    
    if filters.get('funding_range'):
        filter_chips.append(f"Funding: {filters['funding_range'][0]} - {filters['funding_range'][1]}")
    
    if filters.get('deadline') and filters['deadline'] != "All":
        filter_chips.append(f"Deadline: {filters['deadline']}")
    
    # Display filter chips
    if filter_chips:
        chips_html = ""
        for chip in filter_chips:
            chips_html += f'<span class="filter-chip">{chip}</span>'
        
        st.markdown(chips_html, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Filters"):
            clear_all_filters()
            st.rerun()

def main():
    # Header
    st.markdown('<h1 class="main-header">Grant Management Dashboard</h1>', unsafe_allow_html=True)
    
    # Global search in sidebar
    global_search_interface()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Grant Types", "Client Management", "Analytics", "Reports"]
    )
    
    # Load data
    sheet_id = "1xok6PwIk5Kyj78KhBFkjJYGNSdkosxeXliTy0Alt3bc"
    
    # Try to load real data, fallback to sample data
    with st.spinner("Loading data..."):
        df = load_google_sheets_data(sheet_id)
        if df.empty:
            st.warning("Using sample data for demonstration")
            df = create_sample_data()
    
    # Show advanced search interface on relevant pages
    if page in ["Grant Types", "Client Management"]:
        advanced_search_interface()
    
    if page == "Overview":
        show_overview(df)
    elif page == "Grant Types":
        show_grant_types()
    elif page == "Client Management":
        show_client_management(df)
    elif page == "Analytics":
        show_analytics(df)
    elif page == "Reports":
        show_reports(df)

def show_overview(df):
    """Display overview dashboard"""
    st.header("Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Clients", len(df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Grant Types", len(GRANT_TYPES))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        unique_industries = df['Industry'].nunique() if 'Industry' in df.columns else 0
        st.metric("Industries", unique_industries)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        unique_states = df['State'].nunique() if 'State' in df.columns else 0
        st.metric("States", unique_states)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Industry' in df.columns:
            st.subheader("Clients by Industry")
            industry_counts = df['Industry'].value_counts()
            fig = px.pie(values=industry_counts.values, names=industry_counts.index, 
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'State' in df.columns:
            st.subheader("Clients by State")
            state_counts = df['State'].value_counts().head(10)
            fig = px.bar(x=state_counts.values, y=state_counts.index, orientation='h',
                        color_discrete_sequence=['#1f77b4'])
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Client Data")
    st.dataframe(df.head(10), use_container_width=True)

def show_grant_types():
    """Display grant types information with enhanced search and filtering"""
    st.header("Grant Types Overview")
    
    # Apply active filters if any
    available_grants = GRANT_TYPES
    if hasattr(st.session_state, 'active_filters'):
        available_grants = apply_grant_filters(available_grants, st.session_state.active_filters)
    
    # Check if we should show individual grant details
    if 'selected_grant' in st.session_state and st.session_state.selected_grant:
        show_individual_grant_page(st.session_state.selected_grant)
        return
    
    # Quick filter bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        quick_search = st.text_input("🔍 Quick Search", placeholder="Search grant types...", key="grant_quick_search")
    with col2:
        sort_by = st.selectbox("Sort by", ["Name", "Category", "Funding Range"])
    with col3:
        view_mode = st.selectbox("View", ["Cards", "List", "Grid"])
    
    # Apply quick search
    if quick_search:
        available_grants = [grant for grant in available_grants if quick_search.lower() in grant.lower()]
    
    st.write(f"Showing {len(available_grants)} of {len(GRANT_TYPES)} grant types")
    
    # Display grants based on view mode
    if view_mode == "Cards":
        display_grant_cards(available_grants)
    elif view_mode == "List":
        display_grant_list(available_grants)
    else:
        display_grant_grid(available_grants)

def apply_grant_filters(grants, filters):
    """Apply filters to grant list"""
    filtered_grants = grants.copy()
    
    # Apply category filters
    if filters.get('categories'):
        category_grants = []
        for category in filters['categories']:
            if category in GRANT_CATEGORIES:
                category_grants.extend(GRANT_CATEGORIES[category])
        filtered_grants = [g for g in filtered_grants if g in category_grants]
    
    return filtered_grants

def display_grant_list(grants):
    """Display grants as a list"""
    for grant in grants:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{grant}**")
            
            with col2:
                funding_range = get_funding_range(grant)
                st.write(funding_range)
            
            with col3:
                if st.button("View", key=f"list_{grant}"):
                    st.session_state.selected_grant = grant
                    st.rerun()

def display_grant_grid(grants):
    """Display grants in a grid layout"""
    cols = st.columns(3)
    
    for i, grant in enumerate(grants):
        with cols[i % 3]:
            with st.container():
                st.subheader(grant)
                st.write(get_grant_description(grant)[:100] + "...")
                funding_range = get_funding_range(grant)
                st.metric("Funding", funding_range)
                
                if st.button("Details", key=f"grid_{grant}"):
                    st.session_state.selected_grant = grant
                    st.rerun()

def display_grant_cards(grants):
    """Display grant type cards"""
    # Group by category for better organization
    if hasattr(st.session_state, 'active_filters') and st.session_state.active_filters.get('categories'):
        # Show filtered categories
        for category in st.session_state.active_filters['categories']:
            if category in GRANT_CATEGORIES:
                category_grants = [g for g in grants if g in GRANT_CATEGORIES[category]]
                if category_grants:
                    st.subheader(f"📋 {category}")
                    display_category_cards(category_grants)
                    st.markdown("---")
    else:
        # Show all categories
        for category, category_grants in GRANT_CATEGORIES.items():
            filtered_category_grants = [g for g in category_grants if g in grants]
            if filtered_category_grants:
                st.subheader(f"📋 {category}")
                display_category_cards(filtered_category_grants)
                st.markdown("---")

def display_category_cards(grants):
    """Display cards for a specific category"""
    for grant_type in grants:
        with st.container():
            st.markdown(f'<div class="grant-type-card">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(grant_type)
                description = get_grant_description(grant_type)
                st.write(description)
            
            with col2:
                funding_range = get_funding_range(grant_type)
                st.metric("Funding Range", funding_range)
            
            with col3:
                if st.button(f"View Details", key=f"btn_{grant_type}"):
                    st.session_state.selected_grant = grant_type
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_individual_grant_page(grant_type):
    """Display detailed individual grant page"""
    # Back button
    if st.button("← Back to Grant Types"):
        st.session_state.selected_grant = None
        st.rerun()
    
    st.title(f"📄 {grant_type}")
    
    # Grant overview section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Grant Overview")
        description = get_detailed_grant_description(grant_type)
        st.write(description)
        
        st.subheader("Eligibility Requirements")
        eligibility = get_grant_eligibility(grant_type)
        for req in eligibility:
            st.write(f"• {req}")
        
        st.subheader("Application Process")
        process_steps = get_application_process(grant_type)
        for i, step in enumerate(process_steps, 1):
            st.write(f"{i}. {step}")
    
    with col2:
        st.subheader("Quick Facts")
        
        # Grant details card
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            
            funding_range = get_funding_range(grant_type)
            st.metric("💰 Funding Range", funding_range)
            
            deadline = get_application_deadline(grant_type)
            st.metric("📅 Deadline", deadline)
            
            success_rate = get_success_rate(grant_type)
            st.metric("📊 Success Rate", success_rate)
            
            processing_time = get_processing_time(grant_type)
            st.metric("⏱️ Processing Time", processing_time)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Contact information
        st.subheader("Contact Information")
        contact_info = get_contact_info(grant_type)
        st.write(f"**Agency:** {contact_info['agency']}")
        st.write(f"**Email:** {contact_info['email']}")
        st.write(f"**Phone:** {contact_info['phone']}")
        st.write(f"**Website:** {contact_info['website']}")
    
    # Tabs for additional information
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Requirements", "📈 Statistics", "📝 Resources", "🎯 Tips"])
    
    with tab1:
        st.subheader("Detailed Requirements")
        requirements = get_detailed_requirements(grant_type)
        for category, reqs in requirements.items():
            st.write(f"**{category}:**")
            for req in reqs:
                st.write(f"  • {req}")
    
    with tab2:
        st.subheader("Grant Statistics")
        show_grant_statistics(grant_type)
    
    with tab3:
        st.subheader("Helpful Resources")
        resources = get_grant_resources(grant_type)
        for resource in resources:
            st.write(f"• [{resource['title']}]({resource['url']}) - {resource['description']}")
    
    with tab4:
        st.subheader("Application Tips")
        tips = get_application_tips(grant_type)
        for tip in tips:
            st.info(f"💡 {tip}")

def show_grant_statistics(grant_type):
    """Show statistics for individual grant type"""
    import random
    
    # Sample historical data
    years = ['2020', '2021', '2022', '2023', '2024']
    applications = [random.randint(100, 1000) for _ in years]
    awards = [int(app * random.uniform(0.2, 0.4)) for app in applications]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Application Trends")
        trend_df = pd.DataFrame({
            'Year': years,
            'Applications': applications,
            'Awards': awards
        })
        
        fig = px.line(trend_df, x='Year', y=['Applications', 'Awards'], 
                     title='Applications vs Awards Over Time')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Success Rate by Year")
        success_rates = [(award/app)*100 for app, award in zip(applications, awards)]
        
        fig = px.bar(x=years, y=success_rates, 
                    title='Success Rate (%)',
                    color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Award amounts distribution
    st.subheader("Award Amount Distribution")
    amounts = [random.randint(10000, 500000) for _ in range(50)]
    fig = px.histogram(x=amounts, nbins=10, title='Distribution of Award Amounts')
    st.plotly_chart(fig, use_container_width=True)

def show_client_management(df):
    """Display enhanced client management interface with advanced search"""
    st.header("Client Management")
    
    # Enhanced search and filter interface
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_client = st.text_input("🔍 Search Clients", placeholder="Name, email, business...")
    
    with col2:
        if 'Industry' in df.columns:
            industry_filter = st.multiselect("Industries", 
                                           list(df['Industry'].unique()),
                                           key="client_industry_filter")
    
    with col3:
        if 'State' in df.columns:
            state_filter = st.multiselect("States", 
                                        list(df['State'].unique()),
                                        key="client_state_filter")
    
    with col4:
        sort_by = st.selectbox("Sort by", ["Name", "Industry", "State", "Recent"])
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_client:
        mask = (
            filtered_df['client'].str.contains(search_client, case=False, na=False) |
            filtered_df['Email'].str.contains(search_client, case=False, na=False) |
            filtered_df['Business'].str.contains(search_client, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if 'Industry' in df.columns and industry_filter:
        filtered_df = filtered_df[filtered_df['Industry'].isin(industry_filter)]
    
    if 'State' in df.columns and state_filter:
        filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]
    
    # Sort data
    if sort_by == "Name":
        filtered_df = filtered_df.sort_values('client')
    elif sort_by == "Industry" and 'Industry' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('Industry')
    elif sort_by == "State" and 'State' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('State')
    
    # Display results count and active filters
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"Showing {len(filtered_df)} of {len(df)} clients")
    
    with col2:
        if st.button("🔄 Reset Filters"):
            st.rerun()
    
    # Show active filters
    active_filters = []
    if industry_filter:
        active_filters.extend([f"Industry: {ind}" for ind in industry_filter])
    if state_filter:
        active_filters.extend([f"State: {state}" for state in state_filter])
    
    if active_filters:
        filter_html = ""
        for filter_item in active_filters:
            filter_html += f'<span class="filter-chip">{filter_item}</span>'
        st.markdown(filter_html, unsafe_allow_html=True)
    
    # Display client data with enhanced view options
    view_option = st.radio("View Mode", ["Table", "Cards"], horizontal=True)
    
    if view_option == "Table":
        st.dataframe(filtered_df, use_container_width=True)
    else:
        # Card view
        for _, client in filtered_df.iterrows():
            with st.container():
                st.markdown('<div class="grant-type-card">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader(client['client'])
                    st.write(f"**Business:** {client['Business']}")
                    st.write(f"**Email:** {client['Email']}")
                
                with col2:
                    if 'Industry' in client:
                        st.write(f"**Industry:** {client['Industry']}")
                    if 'State' in client:
                        st.write(f"**State:** {client['State']}")
                
                with col3:
                    st.write(f"**Phone:** {client['phone number']}")
                    if st.button("View Details", key=f"client_{client['client']}"):
                        st.info("Client details view would open here")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Add new client form
    with st.expander("➕ Add New Client"):
        with st.form("add_client_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_client = st.text_input("Client Name")
                new_email = st.text_input("Email")
                new_business = st.text_input("Business Name")
                new_phone = st.text_input("Phone Number")
            
            with col2:
                new_industry = st.selectbox("Industry", 
                                          ['Technology', 'Healthcare', 'Manufacturing', 
                                           'Agriculture', 'Education', 'Energy'])
                new_state = st.text_input("State")
                new_country = st.text_input("Country", value="USA")
                new_address = st.text_area("Address")
            
            new_summary = st.text_area("Business Summary")
            new_nsic = st.text_input("NSIC Code")
            
            if st.form_submit_button("Add Client"):
                st.success("Client added successfully! (Demo mode)")


def show_analytics(df):
    """Display enhanced analytics dashboard"""
    st.header("📊 Advanced Analytics Dashboard")
    
    # Analytics navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Trends", "🎯 Performance", "🗺️ Geographic", "💰 Financial", "🔍 Insights"
    ])
    
    with tab1:
        show_trend_analytics(df)
    
    with tab2:
        show_performance_analytics(df)
    
    with tab3:
        show_geographic_analytics(df)
    
    with tab4:
        show_financial_analytics(df)
    
    with tab5:
        show_insights_analytics(df)


def show_reports(df):
    """Display enhanced reports and export section"""
    st.header("📊 Reports & Export Center")
    
    # Report navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Quick Reports", "🔧 Custom Builder", "📅 Scheduled Reports", "📁 Report Library", "📤 Bulk Export"
    ])
    
    with tab1:
        show_quick_reports(df)
    
    with tab2:
        show_custom_report_builder(df)
    
    with tab3:
        show_scheduled_reports()
    
    with tab4:
        show_report_library()
    
    with tab5:
        show_bulk_export(df)

def show_quick_reports(df):
    """Show quick report generation options"""
    st.subheader("🚀 Quick Reports")
    
    # Pre-defined report templates
    report_templates = {
        "Executive Summary": {
            "description": "High-level overview with key metrics and trends",
            "includes": ["Total metrics", "Success rates", "Funding distribution", "Top performers"],
            "format": ["PDF", "PowerPoint"]
        },
        "Client Analysis Report": {
            "description": "Detailed analysis of client demographics and performance",
            "includes": ["Client distribution", "Industry analysis", "Geographic breakdown", "Growth trends"],
            "format": ["Excel", "PDF", "CSV"]
        },
        "Grant Performance Report": {
            "description": "Comprehensive grant type performance analysis",
            "includes": ["Success rates by grant", "Processing times", "Funding amounts", "Trends"],
            "format": ["PDF", "Excel", "PowerPoint"]
        },
        "Financial Summary": {
            "description": "Financial overview and budget analysis",
            "includes": ["Total funding", "Budget allocation", "ROI analysis", "Cost per application"],
            "format": ["Excel", "PDF"]
        },
        "Compliance Report": {
            "description": "Regulatory compliance and audit trail",
            "includes": ["Application status", "Documentation", "Deadlines", "Requirements"],
            "format": ["PDF", "Excel"]
        }
    }
    
    # Report template selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_template = st.selectbox(
            "Select Report Template",
            list(report_templates.keys()),
            key="quick_report_template"
        )
        
        if selected_template:
            template_info = report_templates[selected_template]
            st.write(f"**Description:** {template_info['description']}")
            st.write("**Includes:**")
            for item in template_info['includes']:
                st.write(f"• {item}")
    
    with col2:
        if selected_template:
            template_info = report_templates[selected_template]
            
            # Format selection
            export_format = st.selectbox(
                "Export Format",
                template_info['format'],
                key="quick_report_format"
            )
            
            # Date range
            date_range = st.date_input(
                "Report Period",
                value=[datetime(2024, 1, 1), datetime.now()],
                key="quick_report_dates"
            )
            
            # Generate button
            if st.button("📊 Generate Report", type="primary"):
                generate_quick_report(selected_template, export_format, date_range, df)

def generate_quick_report(template, format_type, date_range, df):
    """Generate a quick report based on template"""
    with st.spinner(f"Generating {template} report..."):
        # Simulate report generation
        import time
        time.sleep(2)
        
        # Create sample report data based on template
        if template == "Executive Summary":
            report_data = create_executive_summary(df)
        elif template == "Client Analysis Report":
            report_data = create_client_analysis(df)
        elif template == "Grant Performance Report":
            report_data = create_grant_performance_report()
        elif template == "Financial Summary":
            report_data = create_financial_summary()
        else:
            report_data = create_compliance_report()
        
        # Display report preview
        st.success(f"✅ {template} generated successfully!")
        
        with st.expander("📋 Report Preview"):
            st.json(report_data)
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if format_type in ["CSV", "Excel"]:
                # Create downloadable data
                if template == "Client Analysis Report":
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {format_type}",
                        data=csv_data,
                        file_name=f"{template.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            st.button("📧 Email Report", help="Send report via email (Demo)")
        
        with col3:
            st.button("💾 Save to Library", help="Save report to library for future access")

def show_custom_report_builder(df):
    """Show custom report builder interface"""
    st.subheader("🔧 Custom Report Builder")
    
    # Report configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Selection")
        
        # Data sources
        data_sources = st.multiselect(
            "Select Data Sources",
            ["Client Data", "Grant Types", "Applications", "Financial Data", "Performance Metrics"],
            default=["Client Data"],
            key="custom_data_sources"
        )
        
        # Metrics selection
        available_metrics = [
            "Total Count", "Success Rate", "Average Amount", "Processing Time",
            "Geographic Distribution", "Industry Breakdown", "Trend Analysis"
        ]
        
        selected_metrics = st.multiselect(
            "Select Metrics",
            available_metrics,
            key="custom_metrics"
        )
        
        # Filters
        st.subheader("🎯 Filters")
        
        if 'Industry' in df.columns:
            industry_filter = st.multiselect(
                "Industries",
                list(df['Industry'].unique()),
                key="custom_industry_filter"
            )
        
        if 'State' in df.columns:
            state_filter = st.multiselect(
                "States",
                list(df['State'].unique()),
                key="custom_state_filter"
            )
        
        date_filter = st.date_input(
            "Date Range",
            value=[datetime(2024, 1, 1), datetime.now()],
            key="custom_date_filter"
        )
    
    with col2:
        st.subheader("📋 Report Configuration")
        
        # Report details
        report_name = st.text_input("Report Name", placeholder="Enter custom report name")
        
        report_description = st.text_area(
            "Description",
            placeholder="Describe the purpose of this report..."
        )
        
        # Visualization options
        chart_types = st.multiselect(
            "Include Charts",
            ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot", "Heatmap", "Treemap"],
            key="custom_charts"
        )
        
        # Output format
        output_format = st.selectbox(
            "Output Format",
            ["PDF", "Excel", "PowerPoint", "CSV", "JSON"],
            key="custom_output_format"
        )
        
        # Layout options
        layout_style = st.selectbox(
            "Layout Style",
            ["Professional", "Executive", "Detailed", "Summary"],
            key="custom_layout"
        )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            include_raw_data = st.checkbox("Include Raw Data")
            include_methodology = st.checkbox("Include Methodology")
            auto_insights = st.checkbox("Generate AI Insights")
            watermark = st.text_input("Watermark Text", placeholder="Optional watermark")
    
    # Preview and generate
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👁️ Preview Report", type="secondary"):
            if report_name and selected_metrics:
                show_custom_report_preview(report_name, selected_metrics, chart_types, df)
            else:
                st.warning("Please enter report name and select at least one metric")
    
    with col2:
        if st.button("📊 Generate Report", type="primary"):
            if report_name and selected_metrics:
                generate_custom_report(report_name, selected_metrics, chart_types, output_format, df)
            else:
                st.warning("Please enter report name and select at least one metric")
    
    with col3:
        if st.button("💾 Save Template"):
            if report_name:
                save_report_template(report_name, selected_metrics, chart_types, output_format)
            else:
                st.warning("Please enter a report name")

def show_custom_report_preview(name, metrics, charts, df):
    """Show preview of custom report"""
    st.subheader(f"📋 Preview: {name}")
    
    # Generate preview content
    for metric in metrics:
        st.write(f"**{metric}:**")
        
        if metric == "Total Count":
            st.metric("Total Records", len(df))
        elif metric == "Industry Breakdown" and 'Industry' in df.columns:
            industry_counts = df['Industry'].value_counts()
            if "Bar Chart" in charts:
                fig = px.bar(x=industry_counts.index, y=industry_counts.values,
                           title="Industry Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(industry_counts)
        elif metric == "Geographic Distribution" and 'State' in df.columns:
            state_counts = df['State'].value_counts().head(10)
            if "Pie Chart" in charts:
                fig = px.pie(values=state_counts.values, names=state_counts.index,
                           title="Geographic Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(state_counts)

def generate_custom_report(name, metrics, charts, format_type, df):
    """Generate custom report"""
    with st.spinner(f"Generating custom report: {name}..."):
        import time
        time.sleep(3)
        
        st.success(f"✅ Custom report '{name}' generated successfully!")
        
        # Create sample report content
        report_content = {
            "report_name": name,
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "charts": charts,
            "format": format_type,
            "summary": f"Custom report with {len(metrics)} metrics and {len(charts)} visualizations"
        }
        
        # Show download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if format_type == "CSV":
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            elif format_type == "JSON":
                import json
                json_data = json.dumps(report_content, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            st.button("📧 Email Report")
        
        with col3:
            st.button("💾 Save to Library")

def show_scheduled_reports():
    """Show scheduled reports management"""
    st.subheader("📅 Scheduled Reports")
    
    # Initialize scheduled reports in session state
    if 'scheduled_reports' not in st.session_state:
        st.session_state.scheduled_reports = [
            {
                "name": "Weekly Executive Summary",
                "template": "Executive Summary",
                "frequency": "Weekly",
                "day": "Monday",
                "time": "09:00",
                "recipients": ["admin@company.com"],
                "status": "Active",
                "next_run": "2024-12-23 09:00"
            },
            {
                "name": "Monthly Client Report",
                "template": "Client Analysis Report",
                "frequency": "Monthly",
                "day": "1st",
                "time": "08:00",
                "recipients": ["manager@company.com", "analyst@company.com"],
                "status": "Active",
                "next_run": "2025-01-01 08:00"
            }
        ]
    
    # Display existing scheduled reports
    if st.session_state.scheduled_reports:
        st.subheader("📋 Current Scheduled Reports")
        
        for i, report in enumerate(st.session_state.scheduled_reports):
            with st.expander(f"📊 {report['name']} - {report['status']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Template:** {report['template']}")
                    st.write(f"**Frequency:** {report['frequency']}")
                    st.write(f"**Schedule:** {report['day']} at {report['time']}")
                
                with col2:
                    st.write(f"**Recipients:** {len(report['recipients'])}")
                    for recipient in report['recipients']:
                        st.write(f"• {recipient}")
                
                with col3:
                    st.write(f"**Next Run:** {report['next_run']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✏️ Edit", key=f"edit_scheduled_{i}"):
                            st.session_state.edit_scheduled_report = i
                    
                    with col_b:
                        if st.button("🗑️ Delete", key=f"delete_scheduled_{i}"):
                            st.session_state.scheduled_reports.pop(i)
                            st.rerun()
    
    # Add new scheduled report
    st.markdown("---")
    st.subheader("➕ Create New Scheduled Report")
    
    with st.form("new_scheduled_report"):
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_name = st.text_input("Report Name")
            schedule_template = st.selectbox("Report Template", [
                "Executive Summary", "Client Analysis Report", "Grant Performance Report",
                "Financial Summary", "Compliance Report"
            ])
            schedule_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "Quarterly"])
        
        with col2:
            if schedule_frequency == "Weekly":
                schedule_day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            elif schedule_frequency == "Monthly":
                schedule_day = st.selectbox("Day", ["1st", "15th", "Last day"])
            else:
                schedule_day = "Daily"
            
            schedule_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
            
            recipients_text = st.text_area("Recipients (one email per line)", 
                                         placeholder="admin@company.com\nmanager@company.com")
        
        if st.form_submit_button("📅 Schedule Report"):
            if schedule_name and recipients_text:
                recipients = [email.strip() for email in recipients_text.split('\n') if email.strip()]
                
                new_scheduled_report = {
                    "name": schedule_name,
                    "template": schedule_template,
                    "frequency": schedule_frequency,
                    "day": schedule_day,
                    "time": schedule_time.strftime("%H:%M"),
                    "recipients": recipients,
                    "status": "Active",
                    "next_run": "2024-12-23 09:00"  # Sample next run
                }
                
                st.session_state.scheduled_reports.append(new_scheduled_report)
                st.success(f"✅ Scheduled report '{schedule_name}' created successfully!")
                st.rerun()

def show_report_library():
    """Show report library and history"""
    st.subheader("📁 Report Library")
    
    # Initialize report library
    if 'report_library' not in st.session_state:
        st.session_state.report_library = [
            {
                "name": "Q4 2024 Executive Summary",
                "type": "Executive Summary",
                "created": "2024-12-15 14:30",
                "created_by": "Admin User",
                "size": "2.3 MB",
                "format": "PDF",
                "downloads": 15,
                "tags": ["quarterly", "executive", "summary"]
            },
            {
                "name": "November Client Analysis",
                "type": "Client Analysis Report",
                "created": "2024-12-01 09:15",
                "created_by": "Data Analyst",
                "size": "1.8 MB",
                "format": "Excel",
                "downloads": 8,
                "tags": ["monthly", "clients", "analysis"]
            },
            {
                "name": "Grant Performance Review 2024",
                "type": "Grant Performance Report",
                "created": "2024-11-28 16:45",
                "created_by": "Grant Manager",
                "size": "3.1 MB",
                "format": "PDF",
                "downloads": 22,
                "tags": ["annual", "performance", "grants"]
            }
        ]
    
    # Search and filter library
    col1, col2, col3 = st.columns(3)
    
    with col1:
        library_search = st.text_input("🔍 Search Reports", placeholder="Search by name or tags...")
    
    with col2:
        type_filter = st.selectbox("Filter by Type", 
            ["All Types", "Executive Summary", "Client Analysis Report", "Grant Performance Report", "Financial Summary"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Created Date", "Name", "Downloads", "Size"])
    
    # Display reports
    filtered_reports = st.session_state.report_library.copy()
    
    if library_search:
        filtered_reports = [r for r in filtered_reports 
                          if library_search.lower() in r['name'].lower() 
                          or any(library_search.lower() in tag for tag in r['tags'])]
    
    if type_filter != "All Types":
        filtered_reports = [r for r in filtered_reports if r['type'] == type_filter]
    
    # Sort reports
    if sort_by == "Created Date":
        filtered_reports.sort(key=lambda x: x['created'], reverse=True)
    elif sort_by == "Downloads":
        filtered_reports.sort(key=lambda x: x['downloads'], reverse=True)
    elif sort_by == "Name":
        filtered_reports.sort(key=lambda x: x['name'])
    
    st.write(f"Showing {len(filtered_reports)} reports")
    
    # Display reports in cards
    for report in filtered_reports:
        with st.container():
            st.markdown('<div class="grant-type-card">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.subheader(report['name'])
                st.write(f"**Type:** {report['type']}")
                st.write(f"**Created:** {report['created']} by {report['created_by']}")
                
                # Tags
                tags_html = ""
                for tag in report['tags']:
                    tags_html += f'<span class="filter-chip">{tag}</span>'
                st.markdown(tags_html, unsafe_allow_html=True)
            
            with col2:
                st.metric("Size", report['size'])
                st.write(f"**Format:** {report['format']}")
            
            with col3:
                st.metric("Downloads", report['downloads'])
            
            with col4:
                if st.button("📥 Download", key=f"download_{report['name']}"):
                    st.success(f"Downloading {report['name']}...")
                
                if st.button("👁️ Preview", key=f"preview_{report['name']}"):
                    st.info(f"Preview for {report['name']} would open here")
                
                if st.button("🗑️ Delete", key=f"delete_lib_{report['name']}"):
                    st.session_state.report_library = [r for r in st.session_state.report_library 
                                                     if r['name'] != report['name']]
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_bulk_export(df):
    """Show bulk export options"""
    st.subheader("📤 Bulk Export")
    
    # Export configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Selection")
        
        # Data tables to export
        export_tables = st.multiselect(
            "Select Data Tables",
            ["Client Data", "Grant Applications", "Performance Metrics", "Financial Data", "Analytics Data"],
            default=["Client Data"],
            key="bulk_export_tables"
        )
        
        # Date range for export
        export_date_range = st.date_input(
            "Date Range",
            value=[datetime(2024, 1, 1), datetime.now()],
            key="bulk_export_dates"
        )
        
        # Filters
        if 'Industry' in df.columns:
            export_industries = st.multiselect(
                "Filter by Industries",
                list(df['Industry'].unique()),
                key="bulk_export_industries"
            )
        
        if 'State' in df.columns:
            export_states = st.multiselect(
                "Filter by States",
                list(df['State'].unique()),
                key="bulk_export_states"
            )
    
    with col2:
        st.subheader("⚙️ Export Configuration")
        
        # Export format
        bulk_format = st.selectbox(
            "Export Format",
            ["Excel (Multiple Sheets)", "CSV (Zip Archive)", "JSON", "XML"],
            key="bulk_export_format"
        )
        
        # Compression
        use_compression = st.checkbox("Use Compression", value=True)
        
        # Include metadata
        include_metadata = st.checkbox("Include Metadata", value=True)
        
        # File naming
        file_prefix = st.text_input("File Prefix", value="grant_data_export")
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            include_charts = st.checkbox("Include Chart Images")
            include_summary = st.checkbox("Include Summary Statistics")
            custom_fields = st.text_area("Custom Fields (comma-separated)", 
                                       placeholder="field1, field2, field3")
    
    # Export preview
    st.markdown("---")
    st.subheader("📋 Export Preview")
    
    # Calculate export size and content
    total_records = len(df)
    if export_industries:
        total_records = len(df[df['Industry'].isin(export_industries)])
    if export_states and 'State' in df.columns:
        total_records = len(df[df['State'].isin(export_states)])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", total_records)
    
    with col2:
        st.metric("Tables", len(export_tables))
    
    with col3:
        estimated_size = total_records * 0.5  # Rough estimate in KB
        st.metric("Est. Size", f"{estimated_size:.1f} KB")
    
    with col4:
        st.metric("Format", bulk_format.split()[0])
    
    # Export buttons
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Start Export", type="primary"):
            perform_bulk_export(export_tables, bulk_format, df, total_records)
    
    with col2:
        if st.button("📧 Email Export"):
            st.info("Email export functionality would be implemented here")
    
    with col3:
        if st.button("☁️ Upload to Cloud"):
            st.info("Cloud upload functionality would be implemented here")

def perform_bulk_export(tables, format_type, df, record_count):
    """Perform bulk export operation"""
    with st.spinner("Preparing bulk export..."):
        import time
        
        # Simulate export process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
            
            if i < 30:
                status_text.text("Preparing data...")
            elif i < 60:
                status_text.text("Applying filters...")
            elif i < 90:
                status_text.text("Generating export files...")
            else:
                status_text.text("Finalizing export...")
        
        st.success(f"✅ Bulk export completed! {record_count} records exported in {format_type} format.")
        
        # Provide download options
        if format_type.startswith("CSV"):
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Archive",
                data=csv_data,
                file_name=f"bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        elif format_type.startswith("JSON"):
            import json
            json_data = json.dumps(df.to_dict('records'), indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Helper functions for report generation
def create_executive_summary(df):
    """Create executive summary report data"""
    return {
        "total_clients": len(df),
        "total_grant_types": len(GRANT_TYPES),
        "top_industry": df['Industry'].mode().iloc[0] if 'Industry' in df.columns else "N/A",
        "geographic_spread": df['State'].nunique() if 'State' in df.columns else 0,
        "summary": "Executive summary with key performance indicators and strategic insights."
    }

def create_client_analysis(df):
    """Create client analysis report data"""
    analysis = {
        "total_clients": len(df),
        "industry_distribution": df['Industry'].value_counts().to_dict() if 'Industry' in df.columns else {},
        "geographic_distribution": df['State'].value_counts().to_dict() if 'State' in df.columns else {},
        "growth_metrics": "Client base analysis and growth trends"
    }
    return analysis

def create_grant_performance_report():
    """Create grant performance report data"""
    import random
    
    performance_data = {}
    for grant in GRANT_TYPES[:10]:
        performance_data[grant] = {
            "applications": random.randint(50, 200),
            "success_rate": random.randint(20, 60),
            "avg_amount": random.randint(50000, 500000),
            "processing_days": random.randint(30, 90)
        }
    
    return performance_data

def create_financial_summary():
    """Create financial summary report data"""
    return {
        "total_funding": "$45.2M",
        "average_award": "$185K",
        "roi_percentage": "340%",
        "cost_per_application": "$2.1K",
        "budget_utilization": "87%"
    }

def create_compliance_report():
    """Create compliance report data"""
    return {
        "total_applications": 1247,
        "compliant_applications": 1189,
        "compliance_rate": "95.3%",
        "pending_reviews": 23,
        "overdue_items": 5
    }

def save_report_template(name, metrics, charts, format_type):
    """Save custom report template"""
    if 'report_templates' not in st.session_state:
        st.session_state.report_templates = {}
    
    st.session_state.report_templates[name] = {
        "metrics": metrics,
        "charts": charts,
        "format": format_type,
        "created_at": datetime.now().isoformat()
    }
    
    st.success(f"✅ Report template '{name}' saved successfully!")


if __name__ == "__main__":
    main()
