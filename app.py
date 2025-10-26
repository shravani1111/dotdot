import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="PixelPast — Virtual Museums Guide",
    page_icon="🖼️",
    layout="wide",
)

# --- CSS / styling (enhanced) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .page-bg{
        background: linear-gradient(135deg, #071129 0%, #0f172a 25%, #0ea5a4 60%, #7c3aed 100%);
        padding: 36px;
        border-radius: 18px;
        color: #e6eef8;
    }
    .glass {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.06);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 8px 36px rgba(2,6,23,0.55);
        color: #e6eef8;
        transition: transform 0.18s ease;
    }
    .glass:hover { transform: translateY(-6px); }
    .muted { color: #cfeef5; opacity:0.9; }
    .small { font-size:13px; color:#dff7fb; opacity:0.9; }
    .title { font-weight:700; font-size:20px; margin-bottom:4px; color:#fff; }
    .subtitle { font-size:13px; color:#d0f7fb; opacity:0.9; }
    .hero-cta { background: linear-gradient(90deg,#7c3aed,#06b6d4); color:white; padding:8px 14px; border-radius:10px; font-weight:600; }
    .footer { font-size:13px; color:#d2eefe; opacity:0.8; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar navigation ---
page = st.sidebar.selectbox("Navigate", ["Home", "Platform Statistics", "Gallery", "Museum Map"])
st.sidebar.markdown("---")
st.sidebar.write("Made with ❤️ for curious minds")

# --- Header (reusable) ---
def render_header():
    st.markdown('<div class="page-bg">', unsafe_allow_html=True)
    cols = st.columns([1, 4, 1])
    with cols[0]:
        st.image("https://images.unsplash.com/photo-1509099836639-18ba1be8b9f8?w=800&q=80", width=70)
    with cols[1]:
        st.markdown('<div style="display:flex;align-items:center;gap:8px;">'
                    '<div style="font-size:28px;font-weight:700;color:#fff">PixelPast</div>'
                    '<div style="font-size:14px;color:#dff7fb;opacity:0.9;padding-top:6px">Virtual Museums Guide</div>'
                    '</div>', unsafe_allow_html=True)
        st.markdown('<div class="muted">Explore digitized museum experiences, featured collections and guided virtual tours — beautifully curated.</div>', unsafe_allow_html=True)
    with cols[2]:
        st.button("Sign in", key="signin", help="Sign in to save favorites")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Data for trending museums (with coords for the map) ---
museums = [
    {
        "id": "renaissance",
        "name": "Renaissance Gallery",
        "img": "https://images.unsplash.com/photo-1526318472351-c75fcf0700d0?w=1200&q=80",
        "blurb": "Curated Renaissance paintings with interactive annotations and audio guides.",
        "details": "Step into the light of the Renaissance — detailed zoomable canvases, curator notes, and guided storylines that contextualize each masterpiece.",
        "lat": 43.7696, "lon": 11.2558
    },
    {
        "id": "tech_art",
        "name": "Tech + Art Lab",
        "img": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=80",
        "blurb": "A living collection blending technology with contemporary art installations.",
        "details": "Explore AR-enabled exhibits and ephemeral installations documenting creative tech experiments across the last decade.",
        "lat": 37.7749, "lon": -122.4194
    },
    {
        "id": "ancient_world",
        "name": "Ancient Worlds",
        "img": "https://images.unsplash.com/photo-1549880338-65ddcdfd017b?w=1200&q=80",
        "blurb": "Artifacts, 3D-scans and narrated timelines from ancient civilizations.",
        "details": "High-resolution 3D models, spatial reconstructions and expert commentaries bring archaeology to your browser.",
        "lat": 30.0444, "lon": 31.2357
    },
]

# initialize session state for selection
if "selected_museum" not in st.session_state:
    st.session_state.selected_museum = None

# --- Page: Home (Hero + Trending + About) ---
if page == "Home":
    render_header()
    st.markdown("")  # spacer
    st.markdown('## Trending Museums')
    st.markdown('<div class="small muted">Handpicked virtual experiences people are loving right now</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, m in enumerate(museums):
        with cols[i]:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.image(m["img"], use_container_width=True)
            st.markdown(f'<div class="title">{m["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="subtitle">{m["blurb"]}</div>', unsafe_allow_html=True)
            if st.button("Learn More", key=f"learn_{m['id']}"):
                st.session_state.selected_museum = m["id"]
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Details panel for the selected museum ---
    if st.session_state.selected_museum:
        selected = next((x for x in museums if x["id"] == st.session_state.selected_museum), None)
        if selected:
            st.markdown("---")
            detail_cols = st.columns([2, 1])
            with detail_cols[0]:
                st.markdown(f"### {selected['name']}")
                st.write(selected["details"])
                st.markdown("**What you'll find:**")
                st.write("- High-resolution scans\n- Curated audio tours\n- Scholarly annotations\n- Interactive timelines")
                st.markdown("[Open virtual tour →](#)  ", unsafe_allow_html=True)
            with detail_cols[1]:
                st.image(selected["img"], use_container_width=True)
                if st.button("Close", key=f"close_{selected['id']}"):
                    st.session_state.selected_museum = None

    st.markdown("")  # spacer

    # --- About PixelPast Section ---
    st.markdown("## About PixelPast")
    about_cols = st.columns([2, 1])
    with about_cols[0]:
        st.markdown(
            """
            PixelPast is a curated gateway to virtual museums and digitized collections worldwide.
            We highlight immersive exhibits, educational tours and research-grade scans so anyone can
            explore cultural heritage from anywhere.
            """
        )
        st.markdown("**Our mission:** Preserve access — expand curiosity — inspire discovery.")
        st.markdown("**Features:**")
        st.write("- Curated trending exhibits\n- Deep zoom & 3D model viewers\n- Guided thematic tours\n- Educator resources and lesson plans")
        st.markdown("Want to suggest a museum or collection? Reach out at hello@pixelpast.example")
    with about_cols[1]:
        st.image("https://images.unsplash.com/photo-1513938709626-033611b8cc03?w=1200&q=80", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="footer">© PixelPast — Made for curious minds. Tip: try the trending list and click Learn More for details.</div>', unsafe_allow_html=True)

# --- Page: Platform Statistics ---
elif page == "Platform Statistics":
    render_header()
    st.markdown("## Platform Statistics")
    st.markdown('<div class="small muted">Live-ish metrics and recent trends</div>', unsafe_allow_html=True)
    # sample aggregated metrics
    total_museums = len(museums)
    total_tours = 124  # demo value
    monthly_visitors = 48520  # demo value

    mcols = st.columns(3)
    mcols[0].metric("Museums", total_museums, delta="+1 this week")
    mcols[1].metric("Virtual Tours", total_tours, delta="+8%")
    mcols[2].metric("Monthly Visitors", f"{monthly_visitors:,}", delta="+4.2%")

    st.markdown("")  # spacer
    # small trend chart (demo)
    rng = pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M')
    data = pd.DataFrame({
        "month": rng,
        "visitors": np.random.randint(30000, 60000, size=12).cumsum() / 12
    })
    data = data.set_index("month")
    st.line_chart(data["visitors"])

    st.markdown("### Engagement by Exhibit Type")
    bar_data = pd.DataFrame({
        "Exhibit Type": ["Paintings", "3D Models", "AR Installations", "Mixed Media"],
        "Views": [42000, 31000, 12000, 15000]
    }).set_index("Exhibit Type")
    st.bar_chart(bar_data)

# --- Page: Gallery ---
elif page == "Gallery":
    render_header()
    st.markdown("## Gallery")
    st.markdown('<div class="small muted">A curated selection — click to view larger</div>', unsafe_allow_html=True)
    gallery_images = [
        "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?w=1200&q=80",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200&q=80",
        "https://images.unsplash.com/photo-1526318472351-c75fcf0700d0?w=1200&q=80",
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=80",
        "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?w=1200&q=80",
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=80",
    ]
    cols = st.columns(3)
    for i, img in enumerate(gallery_images):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
    st.markdown("---")
    st.caption("Gallery images are curated for inspiration. Use the map to find museum locations.")

# --- Page: Museum Map ---
elif page == "Museum Map":
    render_header()
    st.markdown("## Museum Map")
    st.markdown('<div class="small muted">Locate trending museums across the globe</div>', unsafe_allow_html=True)
    # prepare map data
    map_df = pd.DataFrame([{"lat": m["lat"], "lon": m["lon"], "name": m["name"]} for m in museums])
    st.map(map_df[["lat", "lon"]])

    st.markdown("### Museums")
    for m in museums:
        with st.expander(m["name"]):
            st.write(m["blurb"])
            st.image(m["img"], use_container_width=True)
            if st.button("View on Home", key=f"goto_{m['id']}"):
                # navigate back to Home and open detail
                st.session_state.selected_museum = m["id"]
                # simple navigation by reloading page selection
                st.experimental_rerun()
