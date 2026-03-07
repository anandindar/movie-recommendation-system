import math
import base64
from pathlib import Path

OMDB_API_KEY = "e09f8ad5"

# ── Credentials ──────────────────────────────────────────
VALID_USERNAME = "anand@0814"
VALID_PASSWORD = "Tamkuhi@274407"


def load_frontend_images():
    """Load and base64-encode all poster images from the frontend/ folder."""
    frontend_path = Path("frontend")
    images_data = []

    if frontend_path.exists():
        for img_file in sorted(frontend_path.glob("*")):
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                try:
                    with open(img_file, "rb") as f:
                        img_base64 = base64.b64encode(f.read()).decode()
                    mime_type = (
                        "image/jpeg"
                        if img_file.suffix.lower() in [".jpg", ".jpeg"]
                        else f"image/{img_file.suffix.lower().strip('.')}"
                    )
                    images_data.append(
                        {"name": img_file.stem, "data": img_base64, "mime": mime_type}
                    )
                except Exception as e:
                    print(f"Error loading {img_file}: {e}")

    return images_data


def build_background(movie_images):
    """
    Build the CSS grid layout variable string and the HTML for the
    full-page background poster grid.

    Returns:
        grid_layout_css  (str) – CSS custom-property assignments
        background_html  (str) – HTML injected into the page
    """
    grid_layout_css = (
        "--bg-cols: 1; --bg-rows: 1; "
        "--bg-cols-md: 1; --bg-rows-md: 1; "
        "--bg-cols-sm: 1; --bg-rows-sm: 1;"
    )
    background_html = ""

    if not movie_images:
        return grid_layout_css, background_html

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
    tiled = [movie_images[i % total_images] for i in range(total_slots)]
    cells = [
        f"<div class='bg-cell'>"
        f"<img src='data:{img['mime']};base64,{img['data']}' alt='{img['name']}'/>"
        f"</div>"
        for img in tiled
    ]

    background_html = (
        "<div class='page-bg-grid'>" + "".join(cells) + "</div>"
        "<div class='page-bg-overlay'></div>"
    )

    return grid_layout_css, background_html


def background_css(grid_layout_css: str) -> str:
    """Return the CSS for the full-page poster grid and overlay."""
    return f"""
/* ── Base ── */
.stApp {{
    position: relative;
    background: transparent !important;
    min-height: 100vh;
    font-family: 'Poppins', sans-serif;
}}

/* ── Poster grid ── */
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
    display: block;
    filter: brightness(0.76) contrast(1.12) saturate(0.95);
}}

.page-bg-overlay {{
    position: fixed;
    inset: 0;
    z-index: 1;
    background:
        radial-gradient(circle at 50% 20%, rgba(229,9,20,0.09), transparent 50%),
        linear-gradient(rgba(0,0,0,0.42), rgba(0,0,0,0.50));
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

header[data-testid="stHeader"] {{ background: transparent; }}
section.main > div {{ position: relative; z-index: 2; }}
"""
