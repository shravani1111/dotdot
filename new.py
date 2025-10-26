import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Virtual Museum Management System",
    page_icon="🏛️",
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
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .gallery-card {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: transform 0.3s;
    }
    .gallery-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Load actual data from CSV files
@st.cache_data
def load_data():
    try:
        # Load museums data with error handling
        museums_df = pd.read_csv('final_museums.csv', on_bad_lines='skip', encoding='utf-8')
        
        # Load bookings data with error handling
        bookings_df = pd.read_csv('bookings_DBS.csv', on_bad_lines='skip', encoding='utf-8')
        
        # Load foreign visitors data with error handling
        foreign_df = pd.read_csv('foreign.csv', on_bad_lines='skip', encoding='utf-8')
        
        # Clean museums data - remove rows with missing coordinates
        if 'Latitude' in museums_df.columns and 'Longitude' in museums_df.columns:
            museums_df['Latitude'] = pd.to_numeric(museums_df['Latitude'], errors='coerce')
            museums_df['Longitude'] = pd.to_numeric(museums_df['Longitude'], errors='coerce')
            museums_df = museums_df.dropna(subset=['Latitude', 'Longitude'])
        
        # Clean bookings data
        if 'Date' in bookings_df.columns:
            bookings_df['Date'] = pd.to_datetime(bookings_df['Date'], errors='coerce')
        
        # Clean foreign visitors data
        if 'Visitors' in foreign_df.columns:
            foreign_df['Visitors'] = pd.to_numeric(foreign_df['Visitors'], errors='coerce')
            foreign_df['Visitors'] = foreign_df['Visitors'].fillna(0)
        
        if 'Year' in foreign_df.columns:
            foreign_df['Year'] = pd.to_numeric(foreign_df['Year'], errors='coerce')
        
        st.success(f"✅ Data loaded successfully: {len(museums_df)} museums, {len(bookings_df)} bookings, {len(foreign_df)} foreign visitor records")
        
        return museums_df, bookings_df, foreign_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure CSV files are in the same directory as the script")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

museums_df, bookings_df, foreign_df = load_data()

# Sidebar navigation
st.sidebar.title("🏛️ Navigation")
page = st.sidebar.radio("Go to", ["Home", "Platform Statistics", "Gallery", "Museum Maps", "Viewer Page"])

# ==================== HOME PAGE ====================
if page == "Home":
    st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
    st.markdown("### Welcome to the Digital Museum Experience")
    
    # Calculate real metrics from data
    total_museums = len(museums_df)
    total_bookings = len(bookings_df)
    total_foreign_visitors = foreign_df['Visitors'].sum() if not foreign_df.empty else 0
    avg_people = bookings_df['People'].mean() if not bookings_df.empty else 0
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <h2>{total_museums:,}</h2>
                <p>Total Museums</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <h2>{total_bookings:,}</h2>
                <p>Total Bookings</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <h2>{int(total_foreign_visitors):,}</h2>
                <p>Foreign Visitors (2014-2024)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <h2>{avg_people:.1f}</h2>
                <p>Avg Group Size</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Museums by Type
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Museums by Type")
        if not museums_df.empty:
            type_counts = museums_df['Type'].value_counts().head(15)
            fig = px.bar(
                x=type_counts.values,
                y=type_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Museum Type'},
                color=type_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top States")
        if not museums_df.empty:
            state_counts = museums_df['State'].value_counts().head(10)
            fig = px.pie(
                values=state_counts.values,
                names=state_counts.index,
                hole=0.4
            )
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # Foreign Visitors Trend
    st.subheader("📈 Foreign Visitors Trend (2014-2024)")
    if not foreign_df.empty and 'Year' in foreign_df.columns:
        yearly_visitors = foreign_df.groupby('Year')['Visitors'].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_visitors['Year'],
            y=yearly_visitors['Visitors'],
            mode='lines+markers',
            name='Foreign Visitors',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            height=400,
            xaxis_title="Year",
            yaxis_title="Total Visitors",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly Distribution
    st.subheader("📅 Booking Distribution by Month")
    if not bookings_df.empty and 'Date' in bookings_df.columns:
        bookings_df['Month'] = bookings_df['Date'].dt.month_name()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_counts = bookings_df['Month'].value_counts().reindex(month_order, fill_value=0)
        
        fig = go.Figure(go.Bar(
            x=month_counts.index,
            y=month_counts.values,
            marker_color='lightblue'
        ))
        fig.update_layout(height=350, xaxis_title="Month", yaxis_title="Bookings")
        st.plotly_chart(fig, use_container_width=True)
    
    # Interactive museum map preview
    st.subheader("🗺️ Museum Network Overview")
    if not museums_df.empty:
        fig = px.scatter_geo(
            museums_df.head(100),  # Show first 100 for performance
            lat='Latitude',
            lon='Longitude',
            hover_name='Name',
            hover_data={'City': True, 'State': True, 'Type': True, 'Latitude': False, 'Longitude': False},
            color='Type',
            size_max=15,
            title="Sample of Museum Locations Across India"
        )
        fig.update_geos(
            center=dict(lat=20.5937, lon=78.9629),
            projection_scale=3.5,
            visible=True,
            resolution=50,
            showcountries=True,
            countrycolor="lightgray"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==================== PLATFORM STATISTICS ====================
elif page == "Platform Statistics":
    st.markdown('<div class="main-header">📊 Platform Statistics</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        if not foreign_df.empty and 'Year' in foreign_df.columns:
            years = sorted(foreign_df['Year'].unique())
            selected_year = st.selectbox("Select Year", years, index=len(years)-1)
        else:
            selected_year = 2024
    
    with col2:
        if not museums_df.empty:
            states = ['All'] + sorted(museums_df['State'].dropna().unique().tolist())
            selected_state = st.selectbox("Select State", states)
        else:
            selected_state = 'All'
    
    with col3:
        if not museums_df.empty:
            types = ['All'] + sorted(museums_df['Type'].dropna().unique().tolist())
            selected_type = st.selectbox("Museum Type", types)
        else:
            selected_type = 'All'
    
    # Filter data
    filtered_museums = museums_df.copy()
    if selected_state != 'All':
        filtered_museums = filtered_museums[filtered_museums['State'] == selected_state]
    if selected_type != 'All':
        filtered_museums = filtered_museums[filtered_museums['Type'] == selected_type]
    
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        col1.metric("Total Museums", len(filtered_museums))
    
    with col2:
        if not foreign_df.empty:
            year_visitors = foreign_df[foreign_df['Year'] == selected_year]['Visitors'].sum()
            col2.metric("Foreign Visitors", f"{int(year_visitors):,}")
        else:
            col2.metric("Foreign Visitors", "N/A")
    
    with col3:
        if not bookings_df.empty:
            attended = bookings_df[bookings_df['Attended'] == 'Yes'].shape[0] if 'Attended' in bookings_df.columns else 0
            total = bookings_df.shape[0]
            rate = (attended / total * 100) if total > 0 else 0
            col3.metric("Attendance Rate", f"{rate:.1f}%")
        else:
            col3.metric("Attendance Rate", "N/A")
    
    with col4:
        if not bookings_df.empty and 'People' in bookings_df.columns:
            avg_group = bookings_df['People'].mean()
            col4.metric("Avg Group Size", f"{avg_group:.1f}")
        else:
            col4.metric("Avg Group Size", "N/A")
    
    with col5:
        if not bookings_df.empty and 'Rating' in bookings_df.columns:
            avg_rating = bookings_df['Rating'].dropna().mean()
            col5.metric("Avg Rating", f"{avg_rating:.1f}⭐" if not pd.isna(avg_rating) else "N/A")
        else:
            col5.metric("Avg Rating", "N/A")
    
    st.markdown("---")
    
    # Detailed analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visitor Analytics", "🗺️ Geographic Analysis", "⏱️ Booking Patterns", "🎨 Museum Types"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Foreign Visitors by District")
            if not foreign_df.empty and selected_year in foreign_df['Year'].values:
                year_data = foreign_df[foreign_df['Year'] == selected_year]
                district_visitors = year_data.groupby('District')['Visitors'].sum().sort_values(ascending=False).head(15)
                
                fig = px.bar(
                    x=district_visitors.values,
                    y=district_visitors.index,
                    orientation='h',
                    labels={'x': 'Total Visitors', 'y': 'District'},
                    color=district_visitors.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Monthly Visitor Pattern")
            if not foreign_df.empty and 'Month' in foreign_df.columns:
                year_data = foreign_df[foreign_df['Year'] == selected_year]
                month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                              'July', 'August', 'September', 'October', 'November', 'December']
                monthly_visitors = year_data.groupby('Month')['Visitors'].sum().reindex(month_order, fill_value=0)
                
                fig = go.Figure(go.Scatter(
                    x=monthly_visitors.index,
                    y=monthly_visitors.values,
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='coral', width=3)
                ))
                fig.update_layout(xaxis_title="Month", yaxis_title="Visitors")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Museums Distribution Across India")
        if not filtered_museums.empty:
            fig = px.scatter_geo(
                filtered_museums,
                lat='Latitude',
                lon='Longitude',
                hover_name='Name',
                hover_data={'City': True, 'State': True, 'Type': True, 'Latitude': False, 'Longitude': False},
                color='State',
                size_max=20,
                title=f"Museums in {selected_state if selected_state != 'All' else 'India'}"
            )
            fig.update_geos(
                center=dict(lat=20.5937, lon=78.9629),
                projection_scale=3.5,
                visible=True,
                resolution=50,
                showcountries=True,
                countrycolor="lightgray"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Cities by Museums")
            city_counts = filtered_museums['City'].value_counts().head(10)
            fig = px.bar(city_counts, orientation='h', color=city_counts.values, 
                        color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Museums by State")
            state_counts = filtered_museums['State'].value_counts().head(10)
            fig = px.pie(values=state_counts.values, names=state_counts.index, hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Booking Patterns Analysis")
        if not bookings_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'TourType' in bookings_df.columns:
                    tour_type_counts = bookings_df['TourType'].value_counts()
                    fig = px.pie(values=tour_type_counts.values, names=tour_type_counts.index,
                                title="Tour Type Distribution", hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'People' in bookings_df.columns:
                    fig = px.histogram(bookings_df, x='People', nbins=20,
                                      title="Group Size Distribution",
                                      labels={'People': 'Number of People', 'count': 'Frequency'})
                    st.plotly_chart(fig, use_container_width=True)
            
            if 'Museum' in bookings_df.columns:
                st.subheader("Most Booked Museums")
                museum_bookings = bookings_df['Museum'].value_counts().head(15)
                fig = go.Figure(go.Bar(
                    x=museum_bookings.values,
                    y=museum_bookings.index,
                    orientation='h',
                    marker_color='lightblue'
                ))
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Museum Types Analysis")
        if not filtered_museums.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                type_counts = filtered_museums['Type'].value_counts().head(15)
                fig = px.treemap(
                    names=type_counts.index,
                    parents=["" for _ in type_counts.index],
                    values=type_counts.values,
                    title="Museum Types Treemap"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=type_counts.values,
                    y=type_counts.index,
                    orientation='h',
                    labels={'x': 'Count', 'y': 'Type'},
                    color=type_counts.values,
                    color_continuous_scale='Rainbow'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

# ==================== GALLERY ====================
elif page == "Gallery":
    st.markdown('<div class="main-header">🎨 Interactive Gallery</div>', unsafe_allow_html=True)
    
    # Get unique museums with bookings
    if not bookings_df.empty and 'Museum' in bookings_df.columns:
        gallery_museums = bookings_df['Museum'].dropna().unique()[:20]
    else:
        gallery_museums = museums_df['Name'].head(20).tolist() if not museums_df.empty else []
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        if not museums_df.empty:
            types = ['All'] + sorted(museums_df['Type'].dropna().unique().tolist()[:20])
            category_filter = st.selectbox("Category", types)
        else:
            category_filter = 'All'
    
    with col2:
        sort_by = st.selectbox("Sort By", ["Name", "City", "Type"])
    
    with col3:
        search = st.text_input("🔍 Search museums", "")
    
    # Filter gallery items
    filtered_museums_gallery = museums_df.copy()
    if category_filter != 'All':
        filtered_museums_gallery = filtered_museums_gallery[filtered_museums_gallery['Type'] == category_filter]
    if search:
        filtered_museums_gallery = filtered_museums_gallery[
            filtered_museums_gallery['Name'].str.contains(search, case=False, na=False) |
            filtered_museums_gallery['City'].str.contains(search, case=False, na=False)
        ]
    
    # Display gallery in grid
    cols = st.columns(3)
    for idx, (_, museum) in enumerate(filtered_museums_gallery.head(18).iterrows()):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                    <div class="gallery-card">
                        <h3>{museum['Name']}</h3>
                        <p><strong>{museum['City']}, {museum['State']}</strong></p>
                        <p style="color: #666; font-size: 0.9em;">{museum['Type']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    est_year = museum['Established'] if pd.notna(museum['Established']) else 'N/A'
                    st.caption(f"📅 Est: {est_year}")
                with col2:
                    st.caption(f"📍 {museum['City']}")
                
                if st.button(f"Learn More", key=f"learn_{idx}"):
                    with st.expander("ℹ️ Details", expanded=True):
                        st.write(f"**Name:** {museum['Name']}")
                        st.write(f"**Location:** {museum['City']}, {museum['State']}")
                        st.write(f"**Type:** {museum['Type']}")
                        st.write(f"**Established:** {est_year}")
                        if pd.notna(museum['Latitude']) and pd.notna(museum['Longitude']):
                            st.write(f"**Coordinates:** {museum['Latitude']:.4f}, {museum['Longitude']:.4f}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("❤️ Like", key=f"like_{idx}"):
                                st.success("Added to favorites!")
                        with col2:
                            if st.button("🔗 Share", key=f"share_{idx}"):
                                st.info("Share link copied!")
                        with col3:
                            if st.button("📍 Map", key=f"map_{idx}"):
                                st.success("Opening map view...")
                
                st.markdown("---")

# ==================== MUSEUM MAPS ====================
elif page == "Museum Maps":
    st.markdown('<div class="main-header">🗺️ Museum Locations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Museum Map")
        
        # State filter for map
        if not museums_df.empty:
            selected_state_map = st.selectbox(
                "Filter by State",
                ['All States'] + sorted(museums_df['State'].dropna().unique().tolist())
            )
            
            map_museums = museums_df.copy()
            if selected_state_map != 'All States':
                map_museums = map_museums[map_museums['State'] == selected_state_map]
            
            # Create interactive map with OpenStreetMap
            fig = px.scatter_mapbox(
                map_museums,
                lat='Latitude',
                lon='Longitude',
                hover_name='Name',
                hover_data={
                    'City': True,
                    'State': True,
                    'Type': True,
                    'Established': True,
                    'Latitude': False,
                    'Longitude': False
                },
                color='Type',
                size_max=15,
                zoom=4,
                height=600
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(
                    center=dict(lat=20.5937, lon=78.9629)
                ),
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Museum Directory")
        
        # Search museums
        search_museum = st.text_input("🔍 Search museum")
        
        # Display museum list
        display_museums = museums_df.copy()
        if search_museum:
            display_museums = display_museums[
                display_museums['Name'].str.contains(search_museum, case=False, na=False)
            ]
        
        for idx, (_, museum) in enumerate(display_museums.head(10).iterrows()):
            if not search_museum or search_museum.lower() in museum['Name'].lower():
                with st.expander(f"📍 {museum['Name']}"):
                    st.write(f"**Location:** {museum['City']}, {museum['State']}")
                    st.write(f"**Type:** {museum['Type']}")
                    est = museum['Established'] if pd.notna(museum['Established']) else 'N/A'
                    st.write(f"**Established:** {est}")
                    if pd.notna(museum['Latitude']) and pd.notna(museum['Longitude']):
                        st.write(f"**Coordinates:** {museum['Latitude']:.4f}, {museum['Longitude']:.4f}")
                    
                    if st.button("View on Map", key=f"dir_{idx}"):
                        st.info(f"Centered map on {museum['Name']}")
    
    # Statistics by region
    st.markdown("---")
    st.subheader("Regional Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top cities by museums
        st.subheader("Top 15 Cities by Museum Count")
        city_counts = museums_df['City'].value_counts().head(15)
        fig = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            labels={'x': 'Number of Museums', 'y': 'City'},
            color=city_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution by state
        st.subheader("Museums by State (Top 15)")
        state_counts = museums_df['State'].value_counts().head(15)
        fig = px.pie(
            values=state_counts.values,
            names=state_counts.index,
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Density heatmap
    st.subheader("Museum Density Heatmap")
    fig = px.density_mapbox(
        museums_df,
        lat='Latitude',
        lon='Longitude',
        radius=10,
        zoom=4,
        mapbox_style="open-street-map",
        height=500
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

# ==================== VIEWER PAGE ====================
elif page == "Viewer Page":
    st.markdown('<div class="main-header">👁️ Virtual Museum Viewer</div>', unsafe_allow_html=True)
    
    st.markdown("""
        ### Experience Museums in 3D Virtual Reality
        Explore our curated collections from anywhere in the world.
    """)
    
    # Virtual tour options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎮 Virtual Tour Controls")
        
        tour_type = st.radio(
            "Select Tour Type",
            ["Guided Tour", "Free Exploration", "Audio Tour", "Educational Tour"],
            horizontal=True
        )
        
        if not museums_df.empty:
            museum_select = st.selectbox("Choose Museum", museums_df['Name'].head(50).tolist())
            
            # Get museum details
            selected_museum = museums_df[museums_df['Name'] == museum_select].iloc[0]
        
        # Simulation of 3D viewer
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        height: 400px; border-radius: 15px; display: flex; 
                        align-items: center; justify-content: center; color: white;">
                <div style="text-align: center;">
                    <h2>🎨 360° Virtual Gallery View</h2>
                    <p style="font-size: 1.2em;">Interactive 3D Experience</p>
                    <p>Use mouse to navigate • Click artworks for details</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Controls
        st.markdown("### Navigation Controls")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("⬅️ Rotate Left")
        with col2:
            st.button("➡️ Rotate Right")
        with col3:
            st.button("⬆️ Zoom In")
        with col4:
            st.button("⬇️ Zoom Out")
    
    with col2:
        st.subheader("📋 Tour Information")
        
        if not museums_df.empty:
            st.info(f"""
            **Current Location:** {selected_museum['Name']}
            
            **City:** {selected_museum['City']}
            
            **State:** {selected_museum['State']}
            
            **Type:** {selected_museum['Type']}
            """)
        
        st.markdown("### Quick Actions")
        if st.button("🎧 Enable Audio Guide"):
            st.success("Audio guide activated!")
        
        if st.button("📷 Take Screenshot"):
            st.success("Screenshot saved to gallery!")
        
        if st.button("🔖 Bookmark This View"):
            st.success("View bookmarked!")
        
        if st.button("👥 Invite Friends"):
            st.info("Share link copied to clipboard!")
        
        st.markdown("---")
        st.subheader("🎯 Virtual Experience")
        st.write("**Immersive Tour**")
        st.progress(0.45)
    
    # Additional features
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📚 Museum Details", "💬 Visitor Reviews", "⭐ Ratings"])
    
    with tab1:
        if not museums_df.empty:
            st.subheader("About This Museum")
            st.write(f"""
            **{selected_museum['Name']}** is located in {selected_museum['City']}, {selected_museum['State']}.
            This {selected_museum['Type']} museum offers a unique cultural experience.
            """)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Type", selected_museum['Type'])
            col2.metric("Location", selected_museum['City'])
            est = selected_museum['Established'] if pd.notna(selected_museum['Established']) else 'N/A'
            col3.metric("Established", est)
    
    with tab2:
        st.subheader("Visitor Reviews")
        
        # Show real reviews from bookings
        if not bookings_df.empty and 'Review' in bookings_df.columns:
            reviews = bookings_df[bookings_df['Review'].notna()]['Review'].head(5)
            if len(reviews) > 0:
                for review in reviews:
                    st.write(f"💬 *{review}*")
            else:
                st.info("No reviews available yet. Be the first to review!")
        
        # Rating input
        rating = st.slider("Rate your virtual experience", 1, 5, 5)
        review_text = st.text_area("Share your thoughts")
        if st.button("Submit Review"):
            st.success("Thank you for your feedback!")
    
    with tab3:
        st.subheader("Museum Ratings")
        
        if not bookings_df.empty and 'Rating' in bookings_df.columns:
            ratings = bookings_df['Rating'].dropna()
            if len(ratings) > 0:
                avg_rating = ratings.mean()
                rating_counts = ratings.value_counts().sort_index()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Rating", f"{avg_rating:.1f}⭐")
                    st.metric("Total Reviews", len(ratings))
                
                with col2:
                    fig = px.bar(
                        x=rating_counts.index,
                        y=rating_counts.values,
                        labels={'x': 'Rating', 'y': 'Count'},
                        title="Rating Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ratings available yet.")

# Footer
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Virtual Museum Management System | © 2025 | Connecting art lovers worldwide</p>
        <p>Total Museums: {len(museums_df)} | Total Bookings: {len(bookings_df)}</p>
    </div>
""", unsafe_allow_html=True)