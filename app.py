import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
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

# Generate pseudo data
@st.cache_data
def generate_museum_data():
    # Museum locations
    museums = [
        {"name": "Metropolitan Museum", "lat": 40.7794, "lon": -73.9632, "city": "New York", "visitors": 7500000},
        {"name": "Louvre Museum", "lat": 48.8606, "lon": 2.3376, "city": "Paris", "visitors": 9600000},
        {"name": "British Museum", "lat": 51.5194, "lon": -0.1270, "city": "London", "visitors": 6800000},
        {"name": "National Museum", "lat": 28.6129, "lon": 77.2295, "city": "New Delhi", "visitors": 3200000},
        {"name": "Egyptian Museum", "lat": 30.0478, "lon": 31.2336, "city": "Cairo", "visitors": 2500000},
        {"name": "Tokyo National Museum", "lat": 35.7188, "lon": 139.7762, "city": "Tokyo", "visitors": 2900000},
        {"name": "Vatican Museums", "lat": 41.9065, "lon": 12.4536, "city": "Vatican City", "visitors": 6800000},
        {"name": "Smithsonian", "lat": 38.8913, "lon": -77.0261, "city": "Washington DC", "visitors": 5400000},
        {"name": "Rijksmuseum", "lat": 52.3600, "lon": 4.8852, "city": "Amsterdam", "visitors": 2700000},
        {"name": "Prado Museum", "lat": 40.4138, "lon": -3.6921, "city": "Madrid", "visitors": 3200000},
    ]
    
    # Daily visitors data
    dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
    daily_data = pd.DataFrame({
        'Date': dates,
        'Visitors': [random.randint(15000, 35000) for _ in range(365)],
        'Online_Visitors': [random.randint(8000, 20000) for _ in range(365)],
        'Ticket_Sales': [random.randint(200000, 500000) for _ in range(365)]
    })
    
    # Category visits
    categories = ['Ancient Art', 'Modern Art', 'Sculpture', 'Photography', 'History', 'Science']
    category_data = pd.DataFrame({
        'Category': categories,
        'Visits': [random.randint(50000, 200000) for _ in categories],
        'Avg_Duration_Min': [random.randint(20, 90) for _ in categories]
    })
    
    return pd.DataFrame(museums), daily_data, category_data

museums_df, daily_visitors, category_visits = generate_museum_data()

# Sidebar navigation
st.sidebar.title("🏛️ Navigation")
page = st.sidebar.radio("Go to", ["Home", "Platform Statistics", "Gallery", "Museum Maps", "Viewer Page"])

# ==================== HOME PAGE ====================
if page == "Home":
    st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
    st.markdown("### Welcome to the Digital Museum Experience")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <h2>7.2M</h2>
                <p>Total Visitors This Year</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <h2>156</h2>
                <p>Active Museums</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <h2>45K+</h2>
                <p>Artworks Digitized</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card">
                <h2>89%</h2>
                <p>Satisfaction Rate</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Interactive visitor trends
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Visitor Trends - Last 365 Days")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_visitors['Date'],
            y=daily_visitors['Visitors'],
            mode='lines',
            name='Physical Visitors',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            x=daily_visitors['Date'],
            y=daily_visitors['Online_Visitors'],
            mode='lines',
            name='Online Visitors',
            line=dict(color='#ff7f0e', width=2),
            fill='tozeroy'
        ))
        fig.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Category Performance")
        fig = px.pie(
            category_visits,
            values='Visits',
            names='Category',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly comparison
    st.subheader("📈 Monthly Visitor Analysis")
    monthly_data = daily_visitors.copy()
    monthly_data['Month'] = monthly_data['Date'].dt.to_period('M').astype(str)
    monthly_summary = monthly_data.groupby('Month').agg({
        'Visitors': 'sum',
        'Online_Visitors': 'sum',
        'Ticket_Sales': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_summary['Month'],
        y=monthly_summary['Visitors'],
        name='Physical',
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        x=monthly_summary['Month'],
        y=monthly_summary['Online_Visitors'],
        name='Online',
        marker_color='#ff7f0e'
    ))
    fig.update_layout(barmode='group', height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interactive heatmap
    st.subheader("🗺️ Global Museum Network")
    fig = px.scatter_geo(
        museums_df,
        lat='lat',
        lon='lon',
        hover_name='name',
        hover_data={'city': True, 'visitors': ':,', 'lat': False, 'lon': False},
        size='visitors',
        color='visitors',
        color_continuous_scale='Viridis',
        size_max=40,
        title="Museums by Annual Visitors"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ==================== PLATFORM STATISTICS ====================
elif page == "Platform Statistics":
    st.markdown('<div class="main-header">📊 Platform Statistics</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year"])
    with col2:
        metric_type = st.selectbox("Metric Type", ["Visitors", "Revenue", "Engagement"])
    with col3:
        museum_filter = st.multiselect("Filter Museums", museums_df['name'].tolist(), default=museums_df['name'].tolist()[:3])
    
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Avg Daily Visitors", "24,567", "+12.3%")
    col2.metric("Peak Day", "35,892", "Saturday")
    col3.metric("Conversion Rate", "67.8%", "+5.2%")
    col4.metric("Avg Session Time", "42 min", "+8 min")
    col5.metric("Revenue", "$4.2M", "+18%")
    
    st.markdown("---")
    
    # Detailed analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visitor Analytics", "💰 Revenue Breakdown", "⏱️ Time Analysis", "🎨 Content Performance"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            # Visitor demographics
            st.subheader("Visitor Demographics")
            demo_data = pd.DataFrame({
                'Age Group': ['18-24', '25-34', '35-44', '45-54', '55+'],
                'Percentage': [15, 28, 25, 20, 12]
            })
            fig = px.bar(demo_data, x='Age Group', y='Percentage', color='Percentage',
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Device usage
            st.subheader("Device Distribution")
            device_data = pd.DataFrame({
                'Device': ['Mobile', 'Desktop', 'Tablet'],
                'Users': [45, 38, 17]
            })
            fig = px.pie(device_data, values='Users', names='Device', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        # Hourly traffic
        st.subheader("Hourly Traffic Pattern")
        hours = list(range(24))
        traffic = [random.randint(200, 3000) for _ in hours]
        fig = go.Figure(go.Bar(x=hours, y=traffic, marker_color='lightblue'))
        fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Visitors")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Revenue by Category")
            revenue_data = pd.DataFrame({
                'Category': ['Tickets', 'Memberships', 'Gift Shop', 'Events', 'Donations'],
                'Revenue': [1200000, 850000, 450000, 380000, 320000]
            })
            fig = px.treemap(revenue_data, path=['Category'], values='Revenue',
                           color='Revenue', color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Monthly Revenue Trend")
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            revenue = [320000, 380000, 410000, 390000, 450000, 480000]
            fig = go.Figure(go.Scatter(x=months, y=revenue, mode='lines+markers',
                                      line=dict(color='green', width=3)))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Average Time Spent by Exhibit")
        exhibits = ['Ancient Egypt', 'Renaissance', 'Modern Art', 'Natural History', 'Space']
        times = [45, 38, 52, 41, 36]
        fig = go.Figure(go.Bar(x=exhibits, y=times, marker_color='coral'))
        fig.update_layout(yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Visit Duration Distribution")
        durations = np.random.normal(40, 15, 1000)
        fig = px.histogram(x=durations, nbins=30, labels={'x': 'Duration (minutes)', 'y': 'Count'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Most Popular Artworks")
        artwork_data = pd.DataFrame({
            'Artwork': ['Mona Lisa', 'Starry Night', 'The Thinker', 'David', 'The Scream'],
            'Views': [125000, 98000, 87000, 76000, 69000],
            'Likes': [45000, 38000, 32000, 28000, 25000]
        })
        fig = px.scatter(artwork_data, x='Views', y='Likes', size='Views', 
                        color='Artwork', hover_name='Artwork', size_max=50)
        st.plotly_chart(fig, use_container_width=True)

# ==================== GALLERY ====================
elif page == "Gallery":
    st.markdown('<div class="main-header">🎨 Interactive Gallery</div>', unsafe_allow_html=True)
    
    # Gallery categories
    gallery_items = [
        {
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": "1503-1519",
            "category": "Renaissance",
            "description": "The most famous portrait in the world, known for her enigmatic smile.",
            "views": "125K",
            "likes": "45K"
        },
        {
            "title": "The Starry Night",
            "artist": "Vincent van Gogh",
            "year": "1889",
            "category": "Post-Impressionism",
            "description": "A swirling night sky over a French village, painted from memory.",
            "views": "98K",
            "likes": "38K"
        },
        {
            "title": "The Thinker",
            "artist": "Auguste Rodin",
            "year": "1904",
            "category": "Sculpture",
            "description": "Bronze sculpture depicting a nude male figure in deep contemplation.",
            "views": "87K",
            "likes": "32K"
        },
        {
            "title": "Girl with a Pearl Earring",
            "artist": "Johannes Vermeer",
            "year": "1665",
            "category": "Baroque",
            "description": "Often called the 'Mona Lisa of the North', featuring exotic dress and a luminous pearl.",
            "views": "76K",
            "likes": "29K"
        },
        {
            "title": "The Scream",
            "artist": "Edvard Munch",
            "year": "1893",
            "category": "Expressionism",
            "description": "An iconic image of anxiety and existential dread in modern art.",
            "views": "69K",
            "likes": "25K"
        },
        {
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": "1485",
            "category": "Renaissance",
            "description": "Depicts the goddess Venus emerging from the sea upon a shell.",
            "views": "64K",
            "likes": "23K"
        }
    ]
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Category", ["All"] + list(set([item['category'] for item in gallery_items])))
    with col2:
        sort_by = st.selectbox("Sort By", ["Views", "Likes", "Year"])
    with col3:
        search = st.text_input("🔍 Search artworks", "")
    
    # Filter gallery items
    filtered_items = gallery_items
    if category_filter != "All":
        filtered_items = [item for item in filtered_items if item['category'] == category_filter]
    if search:
        filtered_items = [item for item in filtered_items if search.lower() in item['title'].lower() or search.lower() in item['artist'].lower()]
    
    # Display gallery in grid
    cols = st.columns(3)
    for idx, item in enumerate(filtered_items):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                    <div class="gallery-card">
                        <h3>{item['title']}</h3>
                        <p><strong>{item['artist']}</strong> • {item['year']}</p>
                        <p style="color: #666; font-size: 0.9em;">{item['category']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"👁️ {item['views']} views")
                with col2:
                    st.caption(f"❤️ {item['likes']} likes")
                
                if st.button(f"Learn More", key=f"learn_{idx}"):
                    with st.expander("ℹ️ Details", expanded=True):
                        st.write(f"**Description:** {item['description']}")
                        st.write(f"**Period:** {item['category']}")
                        st.write(f"**Created:** {item['year']}")
                        
                        # Interactive options
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("❤️ Like", key=f"like_{idx}"):
                                st.success("Added to favorites!")
                        with col2:
                            if st.button("🔗 Share", key=f"share_{idx}"):
                                st.info("Share link copied!")
                        with col3:
                            if st.button("💬 Comment", key=f"comment_{idx}"):
                                st.text_area("Your comment:", key=f"comment_area_{idx}")
                
                st.markdown("---")

# ==================== MUSEUM MAPS ====================
elif page == "Museum Maps":
    st.markdown('<div class="main-header">🗺️ Museum Locations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Global Museum Network")
        
        # Interactive map with plotly
        fig = px.scatter_geo(
            museums_df,
            lat='lat',
            lon='lon',
            hover_name='name',
            hover_data={
                'city': True,
                'visitors': ':,',
                'lat': False,
                'lon': False
            },
            size='visitors',
            color='visitors',
            color_continuous_scale='Plasma',
            size_max=50,
            projection='natural earth'
        )
        
        fig.update_layout(
            height=600,
            geo=dict(
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                projection_type='natural earth',
                showlakes=True,
                lakecolor='rgb(200, 220, 240)',
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Museum Directory")
        
        # Search and filter
        search_museum = st.text_input("🔍 Search museum")
        
        # Display museum list
        for idx, row in museums_df.iterrows():
            if not search_museum or search_museum.lower() in row['name'].lower():
                with st.expander(f"📍 {row['name']}"):
                    st.write(f"**Location:** {row['city']}")
                    st.write(f"**Annual Visitors:** {row['visitors']:,}")
                    st.write(f"**Coordinates:** {row['lat']:.4f}, {row['lon']:.4f}")
                    
                    if st.button("Get Directions", key=f"dir_{idx}"):
                        st.info(f"Opening directions to {row['name']}...")
    
    # Statistics by region
    st.markdown("---")
    st.subheader("Regional Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top museums by visitors
        fig = px.bar(
            museums_df.sort_values('visitors', ascending=False).head(10),
            x='visitors',
            y='name',
            orientation='h',
            title="Top 10 Museums by Visitors",
            color='visitors',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution by continent (simplified)
        continent_data = pd.DataFrame({
            'Continent': ['Europe', 'North America', 'Asia', 'Africa', 'South America'],
            'Museums': [35, 28, 22, 8, 7]
        })
        fig = px.pie(continent_data, values='Museums', names='Continent',
                    title="Museum Distribution by Continent")
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
        
        museum_select = st.selectbox("Choose Museum", museums_df['name'].tolist())
        
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
        
        st.info(f"""
        **Current Location:** {museum_select}
        
        **Tour Duration:** 45 minutes
        
        **Artworks:** 24 pieces
        
        **Audio:** Available
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
        st.subheader("🎯 Current Exhibit")
        st.write("**Renaissance Masters**")
        st.write("Room 3 of 8")
        st.progress(0.375)
    
    # Additional features
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📚 Exhibit Details", "💬 Live Chat", "⭐ Reviews"])
    
    with tab1:
        st.subheader("About This Exhibit")
        st.write("""
        The Renaissance Masters collection features works from the 14th to 17th century,
        showcasing the revolutionary artistic techniques that defined the era. This exhibit
        includes pieces from Leonardo da Vinci, Michelangelo, Raphael, and other influential
        artists who transformed European art.
        """)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Artworks", "24")
        col2.metric("Period", "14th-17th Century")
        col3.metric("Avg Rating", "4.8/5.0")
    
    with tab2:
        st.subheader("Live Tour Chat")
        st.text_input("Ask the curator anything...", key="chat_input")
        
        # Simulated chat
        st.markdown("""
        **Guide:** Welcome to the Renaissance exhibit! Feel free to ask questions.
        
        **Visitor123:** What technique did da Vinci use for the Mona Lisa?
        
        **Guide:** Great question! Da Vinci used sfumato, a technique of subtle gradations...
        """)
    
    with tab3:
        st.subheader("Visitor Reviews")
        
        # Rating
        rating = st.slider("Rate your experience", 1, 5, 5)
        review_text = st.text_area("Share your thoughts")
        if st.button("Submit Review"):
            st.success("Thank you for your feedback!")
        
        st.markdown("---")
        st.write("**Recent Reviews:**")
        st.write("⭐⭐⭐⭐⭐ *Amazing virtual experience! Felt like I was really there.* - User A")
        st.write("⭐⭐⭐⭐ *Great collection, easy to navigate.* - User B")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Virtual Museum Management System | © 2025 | Connecting art lovers worldwide</p>
    </div>
""", unsafe_allow_html=True)