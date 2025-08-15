"""Configuration settings for the Grant Dashboard"""

# Google Sheets configuration
GOOGLE_SHEETS_ID = "1xok6PwIk5Kyj78KhBFkjJYGNSdkosxeXliTy0Alt3bc"

# Dashboard configuration
DASHBOARD_TITLE = "Grant Management Dashboard"
REFRESH_INTERVAL = 300  # 5 minutes in seconds

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# Grant categories for better organization
GRANT_CATEGORIES = {
    'Business & Innovation': [
        'Small Business Innovation Research',
        'Small Business Technology Transfer',
        'Technology Commercialization Grants',
        'Minority-Owned Business Grants',
        'Women-Owned Business Grants',
        'Rural Business Development Grants'
    ],
    'Education & Research': [
        'Pell Grants',
        'Fulbright Program Grants',
        'National Science Foundation (NSF)',
        'Teacher Quality Partnership Grants',
        'STEM Education Grants',
        'Biomedical Research Grants',
        'Agricultural Research Grants'
    ],
    'Community & Social': [
        'Head Start Program Grants',
        'Community Development Block Grants',
        'Arts & Culture Grants',
        'Health & Wellness Grants',
        'Youth Development Grants',
        'Veterans Assistance Grants',
        'Housing Assistance Grants',
        'Accessibility Grants',
        'Cultural Preservation Grants'
    ],
    'Environment & Energy': [
        'Environmental Education Grants',
        'Energy Efficiency and Renewable'
    ],
    'Emergency & Relief': [
        'Disaster Relief and Recovery Grants'
    ]
}
