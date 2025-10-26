import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import hashlib
import json
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
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .booking-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
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
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = None

# File paths
USERS_FILE = 'users.txt'
BOOKINGS_FILE = 'bookings.txt'

# Utility Functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password, email):
    """Save user credentials to file"""
    with open(USERS_FILE, 'a') as f:
        f.write(f"{username}|{hash_password(password)}|{email}|{datetime.now()}\n")

def verify_user(username, password):
    """Verify user credentials"""
    if not os.path.exists(USERS_FILE):
        return False
    
    with open(USERS_FILE, 'r') as f:
        for line in f:
            stored_user, stored_pass, stored_email, _ = line.strip().split('|')
            if stored_user == username and stored_pass == hash_password(password):
                return True
    return False

def user_exists(username):
    """Check if username already exists"""
    if not os.path.exists(USERS_FILE):
        return False
    
    with open(USERS_FILE, 'r') as f:
        for line in f:
            stored_user = line.strip().split('|')[0]
            if stored_user == username:
                return True
    return False

def save_booking(booking_data):
    """Save booking details to file"""
    booking_id = hashlib.md5(f"{booking_data['username']}{datetime.now()}".encode()).hexdigest()[:8]
    booking_data['booking_id'] = booking_id
    
    with open(BOOKINGS_FILE, 'a') as f:
        f.write(json.dumps(booking_data) + '\n')
    
    return booking_id

def get_user_bookings(username):
    """Retrieve all bookings for a user"""
    if not os.path.exists(BOOKINGS_FILE):
        return []
    
    bookings = []
    with open(BOOKINGS_FILE, 'r') as f:
        for line in f:
            booking = json.loads(line.strip())
            if booking['username'] == username:
                bookings.append(booking)
    return bookings

def generate_qr_code(data):
    """Generate QR code from booking data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return buf

def get_base64_image(buf):
    """Convert image buffer to base64 string"""
    return base64.b64encode(buf.getvalue()).decode()

# Load data
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

museums_df, bookings_df, foreign_df = load_data()

# Login/Register Page
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("## 🏛️ Museum Management System")
        st.markdown("### Welcome! Please login or register")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown("#### Login to Your Account")
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔐 Login", use_container_width=True):
                    if login_username and login_password:
                        if verify_user(login_username, login_password):
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials!")
                    else:
                        st.warning("Please fill all fields")
            
            with col2:
                if st.button("👤 Guest Login", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.username = "Guest"
                    st.info("Logged in as Guest")
                    st.rerun()
        
        with tab2:
            st.markdown("#### Create New Account")
            reg_username = st.text_input("Username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("📝 Register", use_container_width=True):
                if reg_username and reg_email and reg_password and reg_confirm:
                    if reg_password != reg_confirm:
                        st.error("Passwords don't match!")
                    elif user_exists(reg_username):
                        st.error("Username already exists!")
                    else:
                        save_user(reg_username, reg_password, reg_email)
                        st.success("Registration successful! Please login.")
                else:
                    st.warning("Please fill all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Booking Page
def show_booking_page():
    st.markdown('<div class="main-header">🎫 Museum Booking</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📅 Book Your Museum Visit")
        
        # Museum selection
        if not museums_df.empty:
            museum_names = museums_df['Name'].dropna().unique().tolist()
            selected_museum = st.selectbox("🏛️ Select Museum", museum_names)
            
            # Get museum details
            museum_info = museums_df[museums_df['Name'] == selected_museum].iloc[0]
            
            # Display museum info
            st.info(f"""
            **Location:** {museum_info['City']}, {museum_info['State']}  
            **Type:** {museum_info['Type']}  
            **Established:** {museum_info['Established'] if pd.notna(museum_info['Established']) else 'N/A'}
            """)
            
            # Booking form
            col1a, col1b = st.columns(2)
            with col1a:
                visit_date = st.date_input("📆 Visit Date", min_value=datetime.now())
            with col1b:
                visit_time = st.time_input("🕐 Visit Time")
            
            col2a, col2b = st.columns(2)
            with col2a:
                num_people = st.number_input("👥 Number of People", min_value=1, max_value=50, value=1)
            with col2b:
                tour_type = st.selectbox("🎯 Tour Type", ["Self-Guided", "Guided", "Virtual", "Group"])
            
            visitor_name = st.text_input("👤 Visitor Name", value=st.session_state.username)
            visitor_email = st.text_input("📧 Email")
            visitor_phone = st.text_input("📱 Phone Number")
            
            col3a, col3b = st.columns(2)
            with col3a:
                age_group = st.selectbox("🎂 Age Group", ["Child", "Teen", "Adult", "Senior"])
            with col3b:
                emergency_contact = st.text_input("🚨 Emergency Contact")
            
            special_requests = st.text_area("📝 Special Requests")
            
            # Terms and conditions
            agree_terms = st.checkbox("I agree to the terms and conditions")
            
            # Submit booking
            if st.button("🎫 Confirm Booking", type="primary", use_container_width=True):
                if not visitor_email or not visitor_phone:
                    st.error("Please fill all required fields!")
                elif not agree_terms:
                    st.warning("Please agree to terms and conditions")
                else:
                    # Create booking data
                    booking_data = {
                        'username': st.session_state.username,
                        'museum': selected_museum,
                        'city': museum_info['City'],
                        'state': museum_info['State'],
                        'date': str(visit_date),
                        'time': str(visit_time),
                        'people': num_people,
                        'tour_type': tour_type,
                        'visitor_name': visitor_name,
                        'visitor_email': visitor_email,
                        'visitor_phone': visitor_phone,
                        'age_group': age_group,
                        'emergency_contact': emergency_contact,
                        'special_requests': special_requests,
                        'booking_timestamp': str(datetime.now()),
                        'status': 'Confirmed'
                    }
                    
                    # Save booking
                    booking_id = save_booking(booking_data)
                    st.session_state.booking_data = booking_data
                    
                    st.success(f"✅ Booking Confirmed! Booking ID: {booking_id}")
                    st.balloons()
    
    with col2:
        st.subheader("📋 Booking Summary")
        
        if st.session_state.booking_data:
            booking = st.session_state.booking_data
            
            st.markdown(f"""
            <div class="booking-card">
                <h3>🎫 Booking #{booking['booking_id']}</h3>
                <hr>
                <p><strong>Museum:</strong> {booking['museum']}</p>
                <p><strong>Date:</strong> {booking['date']}</p>
                <p><strong>Time:</strong> {booking['time']}</p>
                <p><strong>People:</strong> {booking['people']}</p>
                <p><strong>Tour Type:</strong> {booking['tour_type']}</p>
                <p><strong>Status:</strong> <span style="color: green;">{booking['status']}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate QR Code
            qr_buf = generate_qr_code(booking)
            qr_base64 = get_base64_image(qr_buf)
            
            st.markdown("### 📱 Your Booking QR Code")
            st.markdown(f'<img src="data:image/png;base64,{qr_base64}" width="250">', unsafe_allow_html=True)
            
            st.download_button(
                label="💾 Download QR Code",
                data=qr_buf.getvalue(),
                file_name=f"booking_{booking['booking_id']}.png",
                mime="image/png"
            )
            
            # Download booking details
            booking_text = f"""
            ========================================
            MUSEUM BOOKING CONFIRMATION
            ========================================
            
            Booking ID: {booking['booking_id']}
            
            MUSEUM DETAILS:
            Name: {booking['museum']}
            Location: {booking['city']}, {booking['state']}
            
            VISIT DETAILS:
            Date: {booking['date']}
            Time: {booking['time']}
            Number of People: {booking['people']}
            Tour Type: {booking['tour_type']}
            
            VISITOR INFORMATION:
            Name: {booking['visitor_name']}
            Email: {booking['visitor_email']}
            Phone: {booking['visitor_phone']}
            Age Group: {booking['age_group']}
            Emergency Contact: {booking['emergency_contact']}
            
            Special Requests: {booking['special_requests']}
            
            Booking Status: {booking['status']}
            Booked On: {booking['booking_timestamp']}
            
            ========================================
            Please present this confirmation at the museum
            ========================================
            """
            
            st.download_button(
                label="📄 Download Booking Details",
                data=booking_text,
                file_name=f"booking_{booking['booking_id']}.txt",
                mime="text/plain"
            )
        else:
            st.info("Complete the booking form to see your booking summary and QR code")
        
        # Show user's previous bookings
        st.markdown("---")
        st.subheader("📚 Your Previous Bookings")
        user_bookings = get_user_bookings(st.session_state.username)
        
        if user_bookings:
            for booking in reversed(user_bookings[-5:]):  # Show last 5 bookings
                with st.expander(f"🎫 {booking['museum']} - {booking['date']}"):
                    st.write(f"**Booking ID:** {booking['booking_id']}")
                    st.write(f"**Time:** {booking['time']}")
                    st.write(f"**People:** {booking['people']}")
                    st.write(f"**Status:** {booking['status']}")
        else:
            st.info("No previous bookings found")

# Main App with Navigation
def show_main_app():
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.username}!")
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.booking_data = None
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.title("🏛️ Navigation")
        page = st.radio("Go to", ["Home", "Book Museum", "Platform Statistics", "Gallery", "Museum Maps", "Viewer Page"])
    
    # Route to appropriate page
    if page == "Book Museum":
        show_booking_page()
    elif page == "Home":
        show_home_page()
    elif page == "Platform Statistics":
        show_statistics_page()
    elif page == "Gallery":
        show_gallery_page()
    elif page == "Museum Maps":
        show_maps_page()
    elif page == "Viewer Page":
        show_viewer_page()

# Home Page (from original code)
def show_home_page():
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
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# Statistics Page (simplified from original)
def show_statistics_page():
    st.markdown('<div class="main-header">📊 Platform Statistics</div>', unsafe_allow_html=True)
    st.info("Detailed analytics about museum visitors and bookings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Museums", len(museums_df))
    with col2:
        st.metric("Total Bookings", len(bookings_df))
    with col3:
        if not foreign_df.empty:
            st.metric("Foreign Visitors", f"{int(foreign_df['Visitors'].sum()):,}")

# Gallery Page (simplified)
def show_gallery_page():
    st.markdown('<div class="main-header">🎨 Interactive Gallery</div>', unsafe_allow_html=True)
    
    if not museums_df.empty:
        search = st.text_input("🔍 Search museums", "")
        
        filtered = museums_df.copy()
        if search:
            filtered = filtered[filtered['Name'].str.contains(search, case=False, na=False)]
        
        cols = st.columns(3)
        for idx, (_, museum) in enumerate(filtered.head(12).iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="gallery-card">
                        <h3>{museum['Name']}</h3>
                        <p><strong>{museum['City']}, {museum['State']}</strong></p>
                        <p style="color: #666;">{museum['Type']}</p>
                    </div>
                """, unsafe_allow_html=True)

# Maps Page (simplified)
def show_maps_page():
    st.markdown('<div class="main-header">🗺️ Museum Locations</div>', unsafe_allow_html=True)
    
    if not museums_df.empty:
        fig = px.scatter_mapbox(
            museums_df.head(200),
            lat='Latitude',
            lon='Longitude',
            hover_name='Name',
            hover_data={'City': True, 'State': True, 'Type': True},
            color='Type',
            zoom=4,
            height=600
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)

# Viewer Page (simplified)
def show_viewer_page():
    st.markdown('<div class="main-header">👁️ Virtual Museum Viewer</div>', unsafe_allow_html=True)
    st.markdown("### Experience Museums in Virtual Reality")
    
    if not museums_df.empty:
        museum_select = st.selectbox("Choose Museum", museums_df['Name'].head(50))
        
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        height: 400px; border-radius: 15px; display: flex; 
                        align-items: center; justify-content: center; color: white;">
                <div style="text-align: center;">
                    <h2>🎨 360° Virtual Gallery View</h2>
                    <p>Interactive 3D Experience</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Main execution
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Virtual Museum Management System | © 2025 | Connecting art lovers worldwide</p>
    </div>
""", unsafe_allow_html=True)