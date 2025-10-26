import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import hashlib
import os
import qrcode
from io import BytesIO
import base64

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
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# User Management Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from text file"""
    users = {}
    if os.path.exists('users.txt'):
        with open('users.txt', 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    # Safely handle older or malformed lines
                    if len(parts) >= 3:
                        username = parts[0]
                        password = parts[1]
                        email = parts[2]
                        timestamp = parts[3] if len(parts) > 3 else None
                        users[username] = {
                            'password': password,
                            'email': email,
                            'timestamp': timestamp
                        }
                    else:
                        print(f"⚠️ Skipping malformed line: {line.strip()}")
    return users


def save_user(username, password, email):
    """Save new user to text file with timestamp"""
    from datetime import datetime
    timestamp = datetime.now()
    with open('users.txt', 'a') as f:
        f.write(f"{username}|{hash_password(password)}|{email}|{timestamp}\n")

def load_bookings():
    """Load all bookings from text file"""
    bookings = []
    if os.path.exists('bookings.txt'):
        with open('bookings.txt', 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 9:
                        bookings.append({
                            'booking_id': parts[0],
                            'username': parts[1],
                            'museum': parts[2],
                            'date': parts[3],
                            'time': parts[4],
                            'people': parts[5],
                            'tour_type': parts[6],
                            'booking_date': parts[7],
                            'status': parts[8]
                        })
    return bookings

def save_booking(booking_data):
    """Save booking to text file"""
    with open('bookings.txt', 'a') as f:
        f.write(f"{booking_data['booking_id']}|{booking_data['username']}|{booking_data['museum']}|"
                f"{booking_data['date']}|{booking_data['time']}|{booking_data['people']}|"
                f"{booking_data['tour_type']}|{booking_data['booking_date']}|{booking_data['status']}\n")

def generate_qr_code(booking_data):
    """Generate QR code for booking"""
    qr_data = f"""
    Booking ID: {booking_data['booking_id']}
    Museum: {booking_data['museum']}
    Date: {booking_data['date']}
    Time: {booking_data['time']}
    People: {booking_data['people']}
    Tour Type: {booking_data['tour_type']}
    """
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

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

# Login/Register Page
def show_login_page():
    st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Login to Your Account")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            users = load_users()
            if username in users and users[username]['password'] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", use_container_width=True):
            users = load_users()
            
            if not new_username or not new_email or not new_password:
                st.error("Please fill all fields")
            elif new_username in users:
                st.error("Username already exists")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                save_user(new_username, new_password, new_email)
                st.success("Registration successful! Please login.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main App
if not st.session_state.logged_in:
    show_login_page()
else:
    museums_df, bookings_df, foreign_df = load_data()
    
    # Sidebar navigation with logout
    st.sidebar.title(f"🏛️ Welcome, {st.session_state.username}!")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Go to", ["Home", "Platform Statistics", "Gallery", "Museum Maps", "Book Ticket", "My Bookings", "Viewer Page"])

    # ==================== HOME PAGE ====================
    if page == "Home":
        st.markdown('<div class="main-header">🏛️ Virtual Museum Management System</div>', unsafe_allow_html=True)
        st.markdown("### Welcome to the Digital Museum Experience")
        
        total_museums = len(museums_df)
        total_bookings = len(bookings_df)
        total_foreign_visitors = foreign_df['Visitors'].sum() if not foreign_df.empty else 0
        avg_people = bookings_df['People'].mean() if not bookings_df.empty else 0
        
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

    # ==================== PLATFORM STATISTICS ====================
    elif page == "Platform Statistics":
        st.markdown('<div class="main-header">📊 Platform Statistics</div>', unsafe_allow_html=True)
        
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
        
        filtered_museums = museums_df.copy()
        if selected_state != 'All':
            filtered_museums = filtered_museums[filtered_museums['State'] == selected_state]
        if selected_type != 'All':
            filtered_museums = filtered_museums[filtered_museums['Type'] == selected_type]
        
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

    # ==================== GALLERY ====================
    elif page == "Gallery":
        st.markdown('<div class="main-header">🎨 Interactive Gallery</div>', unsafe_allow_html=True)
        
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
                    
                    if st.button(f"Book Now", key=f"book_{idx}"):
                        st.session_state.selected_museum = museum['Name']
                        st.session_state.current_page = 'Book Ticket'
                        st.rerun()

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
                if not search_museum or search_museum.lower() in museum['Name'].lower():
                    with st.expander(f"📍 {museum['Name']}"):
                        st.write(f"**Location:** {museum['City']}, {museum['State']}")
                        st.write(f"**Type:** {museum['Type']}")
                        est = museum['Established'] if pd.notna(museum['Established']) else 'N/A'
                        st.write(f"**Established:** {est}")

    # ==================== BOOK TICKET ====================
    elif page == "Book Ticket":
        st.markdown('<div class="main-header">🎫 Book Your Museum Visit</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Booking Details")
            
            if not museums_df.empty:
                museums_list = sorted(museums_df['Name'].dropna().unique().tolist())
                
                default_idx = 0
                if 'selected_museum' in st.session_state and st.session_state.selected_museum in museums_list:
                    default_idx = museums_list.index(st.session_state.selected_museum)
                
                selected_museum = st.selectbox("Select Museum", museums_list, index=default_idx)
                
                museum_info = museums_df[museums_df['Name'] == selected_museum].iloc[0]
                
                st.info(f"📍 Location: {museum_info['City']}, {museum_info['State']}")
                st.info(f"🎨 Type: {museum_info['Type']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                visit_date = st.date_input("Visit Date", min_value=datetime.today())
            with col_b:
                visit_time = st.time_input("Visit Time", value=datetime.strptime("10:00", "%H:%M").time())
            
            col_c, col_d = st.columns(2)
            with col_c:
                num_people = st.number_input("Number of People", min_value=1, max_value=50, value=1)
            with col_d:
                tour_type = st.selectbox("Tour Type", ["Self-Guided", "Guided Tour", "Virtual Tour", "Group Tour"])
            
            special_requests = st.text_area("Special Requests (Optional)", placeholder="Any special requirements or notes...")
            
            if st.button("Confirm Booking", use_container_width=True, type="primary"):
                booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                booking_data = {
                    'booking_id': booking_id,
                    'username': st.session_state.username,
                    'museum': selected_museum,
                    'date': visit_date.strftime('%Y-%m-%d'),
                    'time': visit_time.strftime('%H:%M'),
                    'people': str(num_people),
                    'tour_type': tour_type,
                    'booking_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'Confirmed'
                }
                
                save_booking(booking_data)
                
                st.session_state.latest_booking = booking_data
                st.success(f"🎉 Booking Confirmed! Your Booking ID: {booking_id}")
                
                qr_img = generate_qr_code(booking_data)
                
                st.markdown("### 📱 Your Booking QR Code")
                st.markdown(f'<img src="data:image/png;base64,{qr_img}" width="300">', unsafe_allow_html=True)
                st.info("💡 Save this QR code and show it at the museum entrance")
                
                st.download_button(
                    label="Download QR Code",
                    data=base64.b64decode(qr_img),
                    file_name=f"booking_{booking_id}.png",
                    mime="image/png"
                )
        
        with col2:
            st.subheader("📋 Booking Summary")
            st.markdown("---")
            
            if 'latest_booking' in st.session_state:
                booking = st.session_state.latest_booking
                st.markdown(f"""
                **Booking ID:** {booking['booking_id']}  
                **Museum:** {booking['museum']}  
                **Date:** {booking['date']}  
                **Time:** {booking['time']}  
                **People:** {booking['people']}  
                **Tour Type:** {booking['tour_type']}  
                **Status:** ✅ {booking['status']}
                """)
            else:
                st.info("Complete the form to see your booking summary")
            
            st.markdown("---")
            st.subheader("💡 Booking Tips")
            st.markdown("""
            - Arrive 15 minutes before your scheduled time
            - Carry a valid ID proof
            - Photography rules vary by museum
            - Some museums offer discounts for students
            - Check museum timings before visiting
            """)

    # ==================== MY BOOKINGS ====================
    elif page == "My Bookings":
        st.markdown('<div class="main-header">📋 My Bookings</div>', unsafe_allow_html=True)
        
        all_bookings = load_bookings()
        user_bookings = [b for b in all_bookings if b['username'] == st.session_state.username]
        
        if not user_bookings:
            st.info("You don't have any bookings yet. Start exploring and book your first museum visit!")
        else:
            st.subheader(f"Total Bookings: {len(user_bookings)}")
            
            for booking in reversed(user_bookings):
                with st.expander(f"🎫 {booking['museum']} - {booking['date']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Booking ID:** {booking['booking_id']}  
                        **Museum:** {booking['museum']}  
                        **Date:** {booking['date']}  
                        **Time:** {booking['time']}  
                        **Number of People:** {booking['people']}  
                        **Tour Type:** {booking['tour_type']}  
                        **Booked On:** {booking['booking_date']}  
                        **Status:** {booking['status']}
                        """)
                    
                    with col2:
                        qr_img = generate_qr_code(booking)
                        st.markdown(f'<img src="data:image/png;base64,{qr_img}" width="200">', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="Download QR",
                            data=base64.b64decode(qr_img),
                            file_name=f"booking_{booking['booking_id']}.png",
                            mime="image/png",
                            key=f"dl_{booking['booking_id']}"
                        )

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
            
            if st.button("👥 Invite Friends"):
                st.info("Share link copied to clipboard!")
            
            st.markdown("---")
            st.subheader("🎯 Virtual Experience")
            st.write("**Immersive Tour**")
            st.progress(0.45)
        
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
            
            if not bookings_df.empty and 'Review' in bookings_df.columns:
                reviews = bookings_df[bookings_df['Review'].notna()]['Review'].head(5)
                if len(reviews) > 0:
                    for review in reviews:
                        st.write(f"💬 *{review}*")
                else:
                    st.info("No reviews available yet. Be the first to review!")
            
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
museums_df = pd.read_csv('final_museums.csv', on_bad_lines='skip', encoding='utf-8')
bookings_df = pd.read_csv('bookings_DBS.csv', on_bad_lines='skip', encoding='utf-8')
foreign_df = pd.read_csv('foreign.csv', on_bad_lines='skip', encoding='utf-8')
st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Virtual Museum Management System | © 2025 | Connecting art lovers worldwide</p>
        <p>Total Museums: {len(museums_df) if not museums_df.empty else 0} | Total Bookings: {len(bookings_df) if not bookings_df.empty else 0}</p>
    </div>
""", unsafe_allow_html=True)