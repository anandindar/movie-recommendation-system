import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path
import base64
import math

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# Load and encode images from frontend folder
def load_frontend_images():
    frontend_path = Path("frontend")
    images_data = []
    
    if frontend_path.exists():
        for img_file in sorted(frontend_path.glob("*")):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    with open(img_file, 'rb') as f:
                        img_base64 = base64.b64encode(f.read()).decode()
                        # Determine mime type
                        mime_type = 'image/jpeg' if img_file.suffix.lower() in ['.jpg', '.jpeg'] else f'image/{img_file.suffix.lower().strip(".")}'
                        images_data.append({
                            'name': img_file.stem,
                            'data': img_base64,
                            'mime': mime_type
                        })
                except Exception as e:
                    print(f"Error loading {img_file}: {e}")
    
    return images_data

# Load all images
movie_images = load_frontend_images()

# Build full-page background grid config from all frontend images
background_grid_html = ""
grid_layout_css = "--bg-cols: 1; --bg-rows: 1; --bg-cols-md: 1; --bg-rows-md: 1; --bg-cols-sm: 1; --bg-rows-sm: 1;"
if movie_images:
    total_images = len(movie_images)
    grid_cols = math.ceil(math.sqrt(total_images))
    grid_rows = math.ceil(total_images / grid_cols)
    grid_cols_md = max(2, min(grid_cols, 4))
    grid_rows_md = math.ceil(total_images / grid_cols_md)
    grid_cols_sm = max(2, min(grid_cols, 3))
    grid_rows_sm = math.ceil(total_images / grid_cols_sm)

    grid_layout_css = (
        f"--bg-cols: {grid_cols}; --bg-rows: {grid_rows}; "
        f"--bg-cols-md: {grid_cols_md}; --bg-rows-md: {grid_rows_md}; "
        f"--bg-cols-sm: {grid_cols_sm}; --bg-rows-sm: {grid_rows_sm};"
    )

    total_slots = grid_cols * grid_rows
    tiled_images = [movie_images[i % total_images] for i in range(total_slots)]

    grid_cells = []
    for img in tiled_images:
        grid_cells.append(
            f"<div class='bg-cell'><img src='data:{img['mime']};base64,{img['data']}' alt='{img['name']}'/></div>"
        )

    background_grid_html = (
        "<div class='page-bg-grid'>"
        + "".join(grid_cells)
        + "</div><div class='page-bg-overlay'></div>"
    )

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {{
    --primary-red: #e50914;
    --soft-red: #ff6b6b;
    --card-bg: rgba(8, 10, 18, 0.86);
    --text-main: #f3f6ff;
    --text-sub: #d3dae8;
}}

/* Professional Movie Background with Poster Images */
.stApp {{
    position: relative;
    background: transparent !important;
    color: var(--text-main);
    min-height: 100vh;
    font-family: 'Poppins', sans-serif;
}}

.page-bg-grid {{
    position: fixed;
    inset: 0;
    z-index: 0;
    display: grid;
    {grid_layout_css}
    grid-template-columns: repeat(var(--bg-cols), 1fr);
    grid-template-rows: repeat(var(--bg-rows), 1fr);
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    pointer-events: none;
    gap: 0;
    align-items: stretch;
    justify-items: stretch;
}}

.bg-cell {{
    overflow: hidden;
    background: #050814;
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.bg-cell img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center center;
    transform: none;
    display: block;
    filter: saturate(1.04) contrast(1.03);
}}

.page-bg-overlay {{
    position: fixed;
    inset: 0;
    z-index: 1;
    background:
        radial-gradient(circle at 50% 20%, rgba(229, 9, 20, 0.06), transparent 46%),
        linear-gradient(rgba(3, 5, 12, 0.52), rgba(3, 5, 12, 0.60));
    pointer-events: none;
}}

@media (max-width: 1000px) {{
    .page-bg-grid {{
        grid-template-columns: repeat(var(--bg-cols-md), 1fr);
        grid-template-rows: repeat(var(--bg-rows-md), 1fr);
    }}
}}

@media (max-width: 640px) {{
    .page-bg-grid {{
        grid-template-columns: repeat(var(--bg-cols-sm), 1fr);
        grid-template-rows: repeat(var(--bg-rows-sm), 1fr);
    }}
}}

header[data-testid="stHeader"] {{
    background: transparent;
}}

section.main > div {{
    position: relative;
    z-index: 2;
}}

/* Top header banner */
.header-banner {{
    background: linear-gradient(105deg, rgba(0, 0, 0, 0.80) 0%, rgba(12, 9, 11, 0.82) 45%, rgba(0, 0, 0, 0.80) 100%) !important;
    padding: 20px 20px;
    margin-top: 14px;
    margin-bottom: 32px;
    text-align: center;
    box-shadow: 0 10px 34px rgba(229, 9, 20, 0.35), 
                0 0 50px rgba(3, 4, 8, 0.65);
    border: 1px solid rgba(229, 9, 20, 0.45);
    border-radius: 14px;
    backdrop-filter: blur(2px);
}}

.header-title {{
    font-size: clamp(34px, 4.6vw, 54px);
    font-weight: 700;
    margin: 0;
    letter-spacing: 1px;
    line-height: 1;
    font-family: 'Poppins', sans-serif;
    color: #ffffff !important;
    -webkit-text-stroke: 0.5px rgba(0, 0, 0, 0.55);
    text-shadow:
        0 2px 14px rgba(0, 0, 0, 1),
        0 0 14px rgba(255, 255, 255, 0.25),
        0 0 30px rgba(229, 9, 20, 0.45),
        0 0 48px rgba(229, 9, 20, 0.3);
    animation: titleGlow 2.2s ease-in-out infinite alternate;
}}

@keyframes titleGlow {{
    from {{
        text-shadow:
            0 2px 14px rgba(0, 0, 0, 1),
            0 0 10px rgba(255, 255, 255, 0.22),
            0 0 22px rgba(229, 9, 20, 0.35);
    }}
    to {{
        text-shadow:
            0 2px 14px rgba(0, 0, 0, 1),
            0 0 18px rgba(255, 255, 255, 0.35),
            0 0 40px rgba(229, 9, 20, 0.6),
            0 0 58px rgba(229, 9, 20, 0.4);
    }}
}}

.header-subtitle {{
    font-size: clamp(14px, 1.7vw, 19px);
    color: #ffd7db;
    margin-top: 8px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.65);
    font-weight: 500;
    letter-spacing: 0.4px;
}}

/* Center Login */
.login-box {{
    background: transparent !important;
    padding: 0 0 6px 0;
    border-radius: 0;
    box-shadow: none !important;
    border: none !important;
    backdrop-filter: none;
}}

.login-title {{
    font-size: clamp(36px, 5.2vw, 52px);
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.4px;
    font-weight: 700;
    text-shadow: 0 2px 18px rgba(0, 0, 0, 1), 0 0 8px rgba(255, 255, 255, 0.1);
    color: #ffffff !important;
}}

.header-banner, .login-box {{
    position: relative;
    z-index: 4;
}}

.welcome-box {{
    background: linear-gradient(150deg, rgba(6, 9, 18, 0.78) 0%, rgba(9, 12, 24, 0.82) 100%) !important;
    border: 1px solid rgba(229, 9, 20, 0.55);
    border-radius: 18px;
    padding: 20px 20px 14px 20px;
    margin-bottom: 14px;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.68);
}}

/* Remove input wrapper styling */
div[data-testid="stTextInput"] {{
    background: transparent !important;
}}

/* Input fields */
div[data-testid="stTextInput"] > div > div > input {{
    background-color: rgba(10, 14, 28, 0.82) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid rgba(255, 120, 130, 0.75) !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 16px !important;
    font-family: 'Poppins', sans-serif !important;
    box-shadow: 0 0 14px rgba(229, 9, 20, 0.16) !important;
}}

div[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: #ffd1d5 !important;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.35), 
                0 0 36px rgba(229, 9, 20, 0.16) !important;
}}

div[data-testid="stTextInput"] > label {{
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    font-family: 'Poppins', sans-serif !important;
    letter-spacing: 0.3px !important;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.9);
    background: rgba(0, 0, 0, 0.40) !important;
    padding: 4px 8px !important;
    border-radius: 8px !important;
    display: inline-block !important;
    margin-bottom: 6px !important;
}}

/* Hide native Streamlit labels to avoid duplicate Username/Password */
div[data-testid="stTextInput"] > label,
div[data-testid="stTextInput"] label {{
    display: none !important;
}}

div[data-testid="stTextInput"] input {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}}

div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span {{
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.95) !important;
}}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
.stTextInput label,
.stTextInput label p,
.stTextInput label span {{
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.95) !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: #dfe8ff !important;
    opacity: 1 !important;
}}

/* Button */
.stButton>button {{
    background: linear-gradient(90deg, #df0b16 0%, #ff6b74 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    width: 100% !important;
    padding: 13px 14px !important;
    font-weight: 900 !important;
    border: 2px solid rgba(255, 209, 213, 0.6) !important;
    font-size: 17px !important;
    font-family: 'Poppins', sans-serif !important;
    letter-spacing: 0.6px !important;
    box-shadow: 0 6px 24px rgba(229, 9, 20, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    text-transform: uppercase;
    position: relative;
    z-index: 5;
}}

.stButton>button::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}}

.stButton>button:hover {{
    background: linear-gradient(90deg, #ff5160 0%, #ff8994 100%) !important;
    box-shadow: 0 9px 28px rgba(229, 9, 20, 0.62), 0 0 16px rgba(255, 209, 213, 0.3) !important;
    transform: translateY(-2px) !important;
    border-color: rgba(255, 209, 213, 0.9) !important;
}}

/* Login subtitle */
.login-subtitle {{
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.3px;
    text-shadow: 0 1px 10px rgba(0, 0, 0, 1);
}}

.login-title,
.login-subtitle,
.header-title {{
    opacity: 1 !important;
    color: #ffffff !important;
}}

.welcome-box h1,
.welcome-box p {{
    color: #ffffff !important;
    opacity: 1 !important;
    text-shadow: 0 1px 10px rgba(0, 0, 0, 1) !important;
}}

.welcome-box .login-title {{
    font-size: clamp(46px, 6vw, 64px) !important;
    letter-spacing: 1.6px !important;
}}

.welcome-box .login-subtitle {{
    font-size: clamp(20px, 2.4vw, 26px) !important;
}}

div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span {{
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 800 !important;
    font-size: 18px !important;
}}

.stButton>button,
.stButton>button span,
.stButton>button div {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.9) !important;
}}

.field-label {{
    color: #ffffff !important;
    font-size: 22px;
    font-weight: 900;
    margin: 8px 0 6px 0;
    text-shadow:
        0 1px 10px rgba(0, 0, 0, 1),
        0 0 12px rgba(255, 255, 255, 0.30),
        0 0 20px rgba(229, 9, 20, 0.35);
}}

.stButton>button * {{
    color: #ffffff !important;
}}

.welcome-box *,
.login-box *,
div[data-testid="stTextInput"] *,
div[data-testid="stButton"] * {{
    color: #ffffff !important;
    opacity: 1 !important;
}}

.welcome-box .login-title,
.welcome-box .login-subtitle,
.login-box .login-title,
.login-box .login-subtitle {{
    color: #ffffff !important;
    opacity: 1 !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 1) !important;
}}

.login-subtitle,
div[data-testid="stTextInput"] > label,
div[data-testid="stTextInput"] > label p {{
    opacity: 1 !important;
    color: #ffffff !important;
}}

/* Remove column padding */
[data-testid="column"] {{
    padding: 0 !important;
}}

/* Final readability override */
.welcome-box {{
    background: linear-gradient(150deg, rgba(6, 9, 18, 0.88) 0%, rgba(9, 12, 24, 0.90) 100%) !important;
}}

.welcome-box .login-title,
.welcome-box .login-subtitle,
.field-label,
.header-title,
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
.stButton>button,
.stButton>button *,
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input::placeholder {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
    text-shadow: none !important;
    font-weight: 900 !important;
    mix-blend-mode: normal !important;
    filter: none !important;
}}

.welcome-box .login-title,
.welcome-box .login-subtitle,
.field-label {{
    animation: none !important;
}}

.header-title,
.welcome-box .login-title,
.welcome-box .login-subtitle,
.field-label,
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input::placeholder,
.stButton > button,
.stButton > button * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: none !important;
    background-image: none !important;
    filter: none !important;
}}

@keyframes textPulse {{
    from {{
        text-shadow:
            0 1px 8px rgba(0, 0, 0, 1),
            0 0 10px rgba(255, 255, 255, 0.2),
            0 0 14px rgba(229, 9, 20, 0.18);
    }}
    to {{
        text-shadow:
            0 1px 8px rgba(0, 0, 0, 1),
            0 0 16px rgba(255, 255, 255, 0.35),
            0 0 26px rgba(229, 9, 20, 0.35);
    }}
}}

/* Absolute white text enforcement on login page */
.header-title,
.welcome-box .login-title,
.welcome-box .login-subtitle,
.field-label,
[data-testid="stWidgetLabel"] *,
div[data-testid="stTextInput"] *,
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stButton"] *,
.stButton > button,
.stButton > button * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}}

/* Highest-priority white lock for login-page text */
html body .stApp .header-title,
html body .stApp .welcome-box .login-title,
html body .stApp .welcome-box .login-subtitle,
html body .stApp .field-label,
html body .stApp [data-testid="stWidgetLabel"] *,
html body .stApp div[data-testid="stTextInput"] *,
html body .stApp div[data-testid="stTextInput"] input,
html body .stApp div[data-testid="stTextInput"] input::placeholder,
html body .stApp .stButton > button,
html body .stApp .stButton > button * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: none !important;
    -webkit-text-stroke: 0 !important;
    filter: none !important;
    mix-blend-mode: normal !important;
    opacity: 1 !important;
}}
</style>
""", unsafe_allow_html=True)

OMDB_API_KEY =("e09f8ad5")

# -------- LOGIN SYSTEM --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    if background_grid_html:
        st.markdown(background_grid_html, unsafe_allow_html=True)

    st.markdown(
        "<h1 class='header-title' style='text-align:center; margin: 14px 0 18px 0; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;'><span style='background: linear-gradient(90deg, #e50914 0%, #ff6b6b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 900; text-shadow: 0 2px 20px rgba(229, 9, 20, 0.8); color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;'>🎬 MOVIES RECOMMENDATION SYSTEM 🎬</span></h1>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='welcome-box'>
            <h1 class='login-title' style='text-align:center; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; background: linear-gradient(90deg, #ffffff 0%, #ffd1d5 50%, #e50914 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; filter: drop-shadow(0 2px 10px rgba(229, 9, 20, 0.8));'>🎬 LOGIN 🎬</h1>
            <p class='login-subtitle' style='text-align:center; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size: 18px; font-weight: 700; text-shadow: 0 2px 12px rgba(229, 9, 20, 0.6);'>Enter your credentials to access the system</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='field-label' style='color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size: 18px; font-weight: 900; letter-spacing: 0.5px; text-shadow: 0 2px 8px rgba(0, 0, 0, 1), 0 0 10px rgba(229, 9, 20, 0.4); margin-bottom: 8px;'>👤 USERNAME</div>", unsafe_allow_html=True)
        username = st.text_input("", key="login_username", label_visibility="collapsed")
        st.markdown("<div class='field-label' style='color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size: 18px; font-weight: 900; letter-spacing: 0.5px; text-shadow: 0 2px 8px rgba(0, 0, 0, 1), 0 0 10px rgba(229, 9, 20, 0.4); margin-bottom: 8px; margin-top: 14px;'>🔑 PASSWORD</div>", unsafe_allow_html=True)
        password = st.text_input("", key="login_password", type="password", label_visibility="collapsed")

        if st.button("Login"):
            if username == "anand@0814" and password == "Tamkuhi@274407":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

st.markdown("<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)

# Load data
ratings = pd.read_csv("Database/ratings.csv")
movies = pd.read_csv("Database/movies.csv")
links = pd.read_csv("Database/links.csv")

st.write(f"👤 Logged in as: **{st.session_state.username}**")
# Create matrix
matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
).fillna(0)

movie_similarity = cosine_similarity(matrix.T)

similarity_df = pd.DataFrame(
    movie_similarity,
    index=matrix.columns,
    columns=matrix.columns
)

def fetch_poster(imdb_id):
    try:
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Response") == "True":
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster

    except Exception as e:
        print("Error fetching poster:", e)

    return None

# Recommendation function
def recommend(movie_id, top_n=5):
    similar_scores = similarity_df[movie_id].sort_values(ascending=False)
    top_movies = similar_scores.iloc[1:top_n+1].index
    return movies[movies["movieId"].isin(top_movies)][["title", "genres"]]


# Dropdown for movie selection
movie_dict = dict(zip(movies["title"], movies["movieId"]))
selected_movie = st.selectbox(
    "🔎 Search and Select a Movie",
    sorted(movie_dict.keys())
)
num_recommendations = st.slider(
    "Select number of recommendations",
    min_value=3,
    max_value=15,
    value=5
)
if st.button("Recommend"):
    movie_id = movie_dict[selected_movie]
    recs = recommend(movie_id, top_n=num_recommendations)

    st.subheader("Recommended Movies:")

    DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Poster"

    for index, row in recs.iterrows():
        movie_title = row["title"]

        movie_id_row = movies[movies["title"] == movie_title]["movieId"].values[0]
        imdb_row = links[links["movieId"] == movie_id_row]

        if not imdb_row.empty:
            imdb_value = str(imdb_row["imdbId"].values[0]).strip()

            if not imdb_value.startswith("tt"):
                imdb_id = "tt" + imdb_value.zfill(7)
            else:
                imdb_id = imdb_value

            poster_url = fetch_poster(imdb_id)

        else:
            poster_url = None

        st.markdown(f"### {movie_title}")

        if poster_url:
            st.image(poster_url, use_column_width=True)
        else:
            st.image(DEFAULT_POSTER, use_column_width=True)
    

st.divider()
st.header("📊 Movie Analytics Dashboard")

# -------- Top Rated Movies --------
avg_rating = ratings.groupby("movieId")["rating"].mean().reset_index()
avg_rating = avg_rating.merge(movies, on="movieId")

top_rated = avg_rating.sort_values("rating", ascending=False).head(10)

st.subheader("⭐ Top Rated Movies")

fig, ax = plt.subplots()
ax.barh(top_rated["title"], top_rated["rating"])
ax.invert_yaxis()
st.pyplot(fig)


# -------- Most Rated Movies --------
count_rating = ratings.groupby("movieId").size().reset_index(name="count")
count_rating = count_rating.merge(movies, on="movieId")

most_rated = count_rating.sort_values("count", ascending=False).head(10)

st.subheader("🔥 Most Watched Movies")

fig2, ax2 = plt.subplots()
ax2.barh(most_rated["title"], most_rated["count"])
ax2.invert_yaxis()
st.pyplot(fig2)


# -------- Rating Distribution --------
st.subheader("📈 Rating Distribution")

fig3, ax3 = plt.subplots()
ax3.hist(ratings["rating"], bins=5)
st.pyplot(fig3)
