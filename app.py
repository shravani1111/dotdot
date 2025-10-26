import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import hashlib
import qrcode
from io import BytesIO
import base64
import json
import os

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
    .login-box {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 15px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_bookings' not in st.session_state:
    st.session_state.user_bookings = []

# Helper Functions
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from text file"""
    users = {}
    try:
        if os.path.exists('users.txt'):
            with open('users.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ',' in line:  # Check if line is valid
                        parts = line.split(',')
                        if len(parts) >= 2:
                            username = parts[0]
                            password = parts[1]
                            users[username] = password
    except Exception as e:
        st.error(f"Error loading users: {e}")
    return users

def save_user(username, password):
    """Save new user to text file"""
    try:
        with open('users.txt', 'a') as f:
            f.write(f"{username},{hash_password(password)}\n")
        return True
    except Exception as e:
        st.error(f"Error saving user: {e}")
        return False

def save_booking(booking_data):
    """Save booking to text file"""
    try:
        with open('bookings.txt', 'a') as f:
            f.write(json.dumps(booking_data) + '\n')
        return True
    except Exception as e:
        st.error(f"Error saving booking: {e}")
        return False

def load_user_bookings(username):
    """Load bookings for specific user"""
    bookings = []
    try:
        if os.path.exists('bookings.txt'):
            with open('bookings.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            booking = json.loads(line)
                            if booking.get('username') == username:
                                bookings.append(booking)
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        st.error(f"Error loading bookings: {e}")
    return bookings

def generate_qr_code(data):
    """Generate QR code for booking"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        st.error(f"Error generating QR code: {e}")
        return None

# Load actual data from CSV files
@st.cache_data
def load_data():
    try:
        museums_df = pd.read_csv('final_museums.csv', on_bad_lines='skip', encoding='utf-8')
        bookings_df = pd.read_csv('bookings_DBS.csv', on_bad_lines='skip', encoding='utf-8')
        foreign_df = pd.read_csv('foreign.csv', on_bad_lines='skip', encoding='utf-8')
        
        if 'Latitude' in museums_df.columns and 'Longitude' in museums_df.columns:
            museums_df['Latitude'] = pd.to_numeric(museums_df['Latitude'], errors='coerce')
            museums_df['Longitude'] = pd.to_numeric(museums_df['Longitude'], errors='coerce')
            museums_df = museums_df.dropna(subset=['Latitude', 'Longitude'])
        
        if 'Date' in bookings_df.columns:
            bookings_df['Date'] = pd.to_datetime(bookings_df['Date'], errors='coerce')
        
        if 'Visitors' in foreign_df.columns:
            foreign_df['Visitors'] = pd.to_numeric(foreign_df['Visitors'], errors='coerce')
            foreign_df['Visitors'] = foreign_df['Visitors'].fillna(0)
        
        if 'Year' in foreign_df.columns:
            foreign_df['Year'] = pd.to_numeric(foreign_df['Year'], errors='coerce')
        
        return museums_df, bookings_df, foreign_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# LOGIN/SIGNUP PAGE
def show_login_page():
    st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("🔐 Login")
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    users = load_users()
                    if username in users and users[username] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_bookings = load_user_bookings(username)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("📝 Create Account")
            
            new_username = st.text_input("Choose Username", key="signup_username")
            new_password = st.text_input("Choose Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True):
                if not new_username or not new_password:
                    st.error("Please fill all fields")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif new_username in load_users():
                    st.error("Username already exists")
                else:
                    if save_user(new_username, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Error creating account. Please try again.")
            
            st.markdown('</div>', unsafe_allow_html=True)

# MAIN APPLICATION
if not st.session_state.logged_in:
    show_login_page()
else:
    museums_df, bookings_df, foreign_df = load_data()
    
    # Sidebar navigation
    st.sidebar.title(f"👤 Welcome, {st.session_state.username}!")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_bookings = []
        st.rerun()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["Home", "Book Museum", "My Bookings", "Platform Statistics", "Gallery", "Museum Maps"])

    # ==================== HOME PAGE ====================
    if page == "Home":
        st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
        st.markdown("### Welcome to the Digital Museum Experience")
        
        total_museums = len(museums_df)
        total_bookings = len(bookings_df)
        total_foreign_visitors = foreign_df['Visitors'].sum() if not foreign_df.empty and 'Visitors' in foreign_df.columns else 0
        avg_people = bookings_df['People'].mean() if not bookings_df.empty and 'People' in bookings_df.columns else 0
        
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
                    <h2>{len(st.session_state.user_bookings)}</h2>
                    <p>Your Bookings</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-card">
                    <h2>{int(total_foreign_visitors):,}</h2>
                    <p>Foreign Visitors</p>
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
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Museums by Type")
            if not museums_df.empty and 'Type' in museums_df.columns:
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
            if not museums_df.empty and 'State' in museums_df.columns:
                state_counts = museums_df['State'].value_counts().head(10)
                fig = px.pie(
                    values=state_counts.values,
                    names=state_counts.index,
                    hole=0.4
                )
                fig.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🗺️ Museum Network Overview")
        if not museums_df.empty:
            fig = px.scatter_mapbox(
                museums_df.head(100),
                lat='Latitude',
                lon='Longitude',
                hover_name='Name',
                hover_data={'City': True, 'State': True, 'Type': True, 'Latitude': False, 'Longitude': False},
                color='Type',
                size_max=15,
                zoom=4,
                height=500
            )
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            st.plotly_chart(fig, use_container_width=True)

    # ==================== BOOK MUSEUM ====================
    elif page == "Book Museum":
        st.markdown('<div class="main-header">🎫 Book Museum Visit</div>', unsafe_allow_html=True)
        
        if not museums_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Select Museum")
                
                # Filters
                states_list = ['All'] + sorted(museums_df['State'].dropna().unique().tolist())
                selected_state = st.selectbox("Filter by State", states_list)
                
                filtered_museums = museums_df.copy()
                if selected_state != 'All':
                    filtered_museums = filtered_museums[filtered_museums['State'] == selected_state]
                
                if len(filtered_museums) > 0:
                    selected_museum_name = st.selectbox("Choose Museum", filtered_museums['Name'].tolist())
                    selected_museum = filtered_museums[filtered_museums['Name'] == selected_museum_name].iloc[0]
                    
                    # Display museum details
                    st.info(f"""
                    **Museum:** {selected_museum['Name']}
                    
                    **Location:** {selected_museum['City']}, {selected_museum['State']}
                    
                    **Type:** {selected_museum['Type']}
                    """)
                    
                    # Booking form
                    st.subheader("Booking Details")
                    
                    booking_date = st.date_input("Select Date", min_value=datetime.now().date())
                    booking_time = st.time_input("Select Time")
                    num_people = st.number_input("Number of People", min_value=1, max_value=50, value=1)
                    tour_type = st.selectbox("Tour Type", ["Self-Guided", "Guided Tour", "Virtual Tour", "Audio Tour"])
                    
                    contact_name = st.text_input("Contact Name", value=st.session_state.username)
                    contact_email = st.text_input("Email")
                    contact_phone = st.text_input("Phone Number")
                    
                    special_requests = st.text_area("Special Requests (Optional)")
                    
                    if st.button("🎫 Confirm Booking", use_container_width=True):
                        if contact_email and contact_phone:
                            # Generate booking ID
                            booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # Create booking data
                            booking_data = {
                                'booking_id': booking_id,
                                'username': st.session_state.username,
                                'museum_name': selected_museum['Name'],
                                'museum_city': selected_museum['City'],
                                'museum_state': selected_museum['State'],
                                'museum_type': selected_museum['Type'],
                                'date': str(booking_date),
                                'time': str(booking_time),
                                'num_people': int(num_people),
                                'tour_type': tour_type,
                                'contact_name': contact_name,
                                'contact_email': contact_email,
                                'contact_phone': contact_phone,
                                'special_requests': special_requests,
                                'booking_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Save booking
                            if save_booking(booking_data):
                                st.session_state.user_bookings = load_user_bookings(st.session_state.username)
                                
                                st.success(f"✅ Booking Confirmed! Booking ID: {booking_id}")
                                st.balloons()
                                
                                # Generate QR Code
                                qr_img = generate_qr_code(booking_data)
                                if qr_img:
                                    st.image(f"data:image/png;base64,{qr_img}", caption="Scan QR Code for Booking Details", width=300)
                                    st.info("📱 Save this QR code for museum entry")
                            else:
                                st.error("Error saving booking. Please try again.")
                        else:
                            st.error("Please fill in all required fields")
                else:
                    st.warning("No museums found in selected state")
            
            with col2:
                st.subheader("📍 Museum Location")
                if len(filtered_museums) > 0 and pd.notna(selected_museum['Latitude']) and pd.notna(selected_museum['Longitude']):
                    map_df = pd.DataFrame({
                        'lat': [selected_museum['Latitude']],
                        'lon': [selected_museum['Longitude']],
                        'name': [selected_museum['Name']]
                    })
                    
                    fig = px.scatter_mapbox(
                        map_df,
                        lat='lat',
                        lon='lon',
                        hover_name='name',
                        zoom=12,
                        height=400
                    )
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r": 0, "t": 0, "l": 0, "b": 0}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("💡 Booking Tips")
                st.info("""
                - Book at least 24 hours in advance
                - Arrive 15 minutes before your slot
                - Carry valid ID proof
                - Follow museum guidelines
                - Keep your QR code handy
                """)

    # ==================== MY BOOKINGS ====================
    elif page == "My Bookings":
        st.markdown('<div class="main-header">📋 My Bookings</div>', unsafe_allow_html=True)
        
        # Reload bookings
        st.session_state.user_bookings = load_user_bookings(st.session_state.username)
        user_bookings = st.session_state.user_bookings
        
        if len(user_bookings) == 0:
            st.info("You don't have any bookings yet. Book your first museum visit!")
            if st.button("🎫 Book Now"):
                st.info("Go to 'Book Museum' page")
        else:
            st.success(f"You have {len(user_bookings)} booking(s)")
            
            for idx, booking in enumerate(user_bookings):
                with st.expander(f"🎫 Booking #{idx+1} - {booking['museum_name']}", expanded=(idx==0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Booking Details")
                        st.write(f"**Booking ID:** {booking['booking_id']}")
                        st.write(f"**Museum:** {booking['museum_name']}")
                        st.write(f"**Location:** {booking['museum_city']}, {booking['museum_state']}")
                        st.write(f"**Type:** {booking['museum_type']}")
                        st.write(f"**Date:** {booking['date']}")
                        st.write(f"**Time:** {booking['time']}")
                        st.write(f"**Number of People:** {booking['num_people']}")
                        st.write(f"**Tour Type:** {booking['tour_type']}")
                        st.write(f"**Contact:** {booking['contact_name']}")
                        st.write(f"**Email:** {booking['contact_email']}")
                        st.write(f"**Phone:** {booking['contact_phone']}")
                        if booking.get('special_requests'):
                            st.write(f"**Special Requests:** {booking['special_requests']}")
                        st.write(f"**Booked On:** {booking['booking_timestamp']}")
                    
                    with col2:
                        st.subheader("QR Code")
                        qr_img = generate_qr_code(booking)
                        if qr_img:
                            st.image(f"data:image/png;base64,{qr_img}", caption="Show at Entry", width=250)
                            
                            st.download_button(
                                label="📥 Download QR Code",
                                data=base64.b64decode(qr_img),
                                file_name=f"booking_{booking['booking_id']}.png",
                                mime="image/png",
                                key=f"download_{idx}"
                            )

    # ==================== PLATFORM STATISTICS ====================
    elif page == "Platform Statistics":
        st.markdown('<div class="main-header">📊 Platform Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if not foreign_df.empty and 'Year' in foreign_df.columns:
                years = sorted(foreign_df['Year'].dropna().unique())
                selected_year = st.selectbox("Select Year", years, index=len(years)-1 if len(years) > 0 else 0)
            else:
                selected_year = 2024
        
        with col2:
            if not museums_df.empty and 'State' in museums_df.columns:
                states = ['All'] + sorted(museums_df['State'].dropna().unique().tolist())
                selected_state = st.selectbox("Select State", states)
            else:
                selected_state = 'All'
        
        with col3:
            if not museums_df.empty and 'Type' in museums_df.columns:
                types = ['All'] + sorted(museums_df['Type'].dropna().unique().tolist())
                selected_type = st.selectbox("Museum Type", types)
            else:
                selected_type = 'All'
        
        filtered_museums = museums_df.copy()
        if selected_state != 'All':
            filtered_museums = filtered_museums[filtered_museums['State'] == selected_state]
        if selected_type != 'All':
            filtered_museums = filtered_museums[filtered_museums['Type'] == selected_type]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            col1.metric("Total Museums", len(filtered_museums))
        
        with col2:
            if not foreign_df.empty and 'Visitors' in foreign_df.columns:
                year_visitors = foreign_df[foreign_df['Year'] == selected_year]['Visitors'].sum()
                col2.metric("Foreign Visitors", f"{int(year_visitors):,}")
            else:
                col2.metric("Foreign Visitors", "N/A")
        
        with col3:
            col3.metric("Your Bookings", len(st.session_state.user_bookings))
        
        with col4:
            if not bookings_df.empty and 'People' in bookings_df.columns:
                avg_group = bookings_df['People'].mean()
                col4.metric("Avg Group Size", f"{avg_group:.1f}")
            else:
                col4.metric("Avg Group Size", "N/A")
        
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📈 Visitor Analytics", "🗺️ Geographic Analysis"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Foreign Visitors by District")
                if not foreign_df.empty and 'District' in foreign_df.columns and selected_year in foreign_df['Year'].values:
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
            st.subheader("Museums Distribution Map")
            if not filtered_museums.empty:
                fig = px.scatter_mapbox(
                    filtered_museums,
                    lat='Latitude',
                    lon='Longitude',
                    hover_name='Name',
                    hover_data={'City': True, 'State': True, 'Type': True, 'Latitude': False, 'Longitude': False},
                    color='State',
                    size_max=20,
                    zoom=4,
                    height=600
                )
                fig.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r": 0, "t": 0, "l": 0, "b": 0}
                )
                st.plotly_chart(fig, use_container_width=True)

    # ==================== GALLERY ====================
    elif page == "Gallery":
        st.markdown('<div class="main-header">🎨 Interactive Gallery</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if not museums_df.empty and 'Type' in museums_df.columns:
                types = ['All'] + sorted(museums_df['Type'].dropna().unique().tolist()[:20])
                category_filter = st.selectbox("Category", types)
            else:
                category_filter = 'All'
        
        with col2:
            sort_by = st.selectbox("Sort By", ["Name", "City", "Type"])
        
        with col3:
            search = st.text_input("🔍 Search museums", "")
        
        filtered_museums_gallery = museums_df.copy()
        if category_filter != 'All':
            filtered_museums_gallery = filtered_museums_gallery[filtered_museums_gallery['Type'] == category_filter]
        if search:
            filtered_museums_gallery = filtered_museums_gallery[
                filtered_museums_gallery['Name'].str.contains(search, case=False, na=False) |
                filtered_museums_gallery['City'].str.contains(search, case=False, na=False)
            ]
        
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
                    
                    if st.button(f"Book Now", key=f"book_{idx}", use_container_width=True):
                        st.info("Go to 'Book Museum' page to complete booking")
                    
                    st.markdown("---")

    # ==================== MUSEUM MAPS ====================
    elif page == "Museum Maps":
        st.markdown('<div class="main-header">🗺️ Museum Locations</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Interactive Museum Map")
            
            if not museums_df.empty:
                selected_state_map = st.selectbox(
                    "Filter by State",
                    ['All States'] + sorted(museums_df['State'].dropna().unique().tolist())
                )
                
                map_museums = museums_df.copy()
                if selected_state_map != 'All States':
                    map_museums = map_museums[map_museums['State'] == selected_state_map]
                
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
            
            search_museum = st.text_input("🔍 Search museum")
            
            display_museums = museums_df.copy()
            if search_museum:
                display_museums = display_museums[
                    display_museums['Name'].str.contains(search_museum, case=False, na=False)
                ]
            
            for idx, (_, museum) in enumerate(display_museums.head(10).iterrows()):
                with st.expander(f"📍 {museum['Name']}"):
                    st.write(f"**Location:** {museum['City']}, {museum['State']}")
                    st.write(f"**Type:** {museum['Type']}")
                    est = museum['Established'] if pd.notna(museum['Established']) else 'N/A'
                    st.write(f"**Established:** {est}")
                    if pd.notna(museum['Latitude']) and pd.notna(museum['Longitude']):
                        st.write(f"**Coordinates:** {museum['Latitude']:.4f}, {museum['Longitude']:.4f}")
                    
                    if st.button("🎫 Book This Museum", key=f"book_map_{idx}"):
                        st.info("Go to 'Book Museum' page")

    # ==================== VIEWER PAGE ====================
    elif page == "Viewer Page":
        st.markdown('<div class="main-header">👁️ Virtual Museum Viewer</div>', unsafe_allow_html=True)
        
        st.markdown("""
            ### Experience Museums in 3D Virtual Reality
            Explore our curated collections from anywhere in the world.
        """)
        
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
                selected_museum = museums_df[museums_df['Name'] == museum_select].iloc[0]
            
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
            
            if st.button("🎫 Book This Museum"):
                st.info("Go to 'Book Museum' page to complete booking")
            
            st.markdown("---")
            st.subheader("🎯 Virtual Experience")
            st.write("**Immersive Tour**")
            st.progress(0.45)
        
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📚 Museum Details", "⭐ Quick Book"])
        
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
            st.subheader("Quick Book This Museum")
            
            if st.button("🎫 Book Now", use_container_width=True):
                st.success("Please go to 'Book Museum' page to complete your booking")

    # Footer
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p>Virtual Museum Management System | © 2025 | Connecting art lovers worldwide</p>
            <p>Total Museums: {len(museums_df)} | Your Bookings: {len(st.session_state.user_bookings)}</p>
        </div>
    """, unsafe_allow_html=True)