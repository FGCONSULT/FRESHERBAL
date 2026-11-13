"""
================================================================================
🌿 FRESHERBAL® SMART PLANT SELECTOR & CULTIVATION GUIDE APPLICATION
================================================================================
An interactive Streamlit & CLI application for selecting plant species and obtaining
detailed botanical profiles, cultivation parameters, matched containers, and 
Package of Practices (PoP) based on user criteria: Budget, Planting Area, Location, 
Growing Season, Soil Type, and Plant Category.

Features:
- Dynamically loads 'plant_database_template.csv'
- Displays plant visual artwork from './plant_assets_D' (P001-P099) and './plant_assets_D1' (P100-P199)
- Uses unique keys and BytesIO streaming for 100% reliable image rendering in expanders
- Supports Streamlit Web GUI & Terminal CLI modes

Usage:
- Web App Mode:      streamlit run plant_selector_app.py
- Terminal CLI Mode: python3 plant_selector_app.py
"""

import os
import sys
import csv
import json
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

DEFAULT_CSV_PATH = "plant_database_template.csv"
DEFAULT_ASSET_DIR = "plant_assets_D"
ALT_ASSET_DIR = "plant_assets_D1"

# ------------------------------------------------------------------------------
# DEFAULT FALLBACK DATASET
# ------------------------------------------------------------------------------
DEFAULT_PLANT_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "P001",
        "english_name": "Elephant Ear / African Mask",
        "botanical_name": "Alocasia macrorrhizos",
        "hindi_name": "Hathikana (हाथीकान) / Alocasia",
        "varieties": ["Polly", "Amazonica", "Wentii", "Black Velvet"],
        "category": ["Indoor", "Aesthetics", "Other plants"],
        "plant_type": "Evergreen herbaceous perennial foliage plant",
        "habit": "Upright clump-forming herb",
        "height": "0.6–1.2 m indoors",
        "spread": "0.6–1.5 m",
        "suitable_locations": ["small indoor eatout room", "Balconies", "Terrace", "Patio", "Front home door"],
        "suitable_planters": '11" Slate Cylindrical Pot / Deep ceramic container',
        "growing_season": "Spring to Summer",
        "nursery_sowing_time": "March–April",
        "seedling_transplanting_time": "April–May",
        "soil_type": "Rich, organic, loose, well-draining peat-perlite mixture",
        "soil_ph": "5.5–6.5",
        "sun_intensity": "Bright indirect light / Filtered shade",
        "humidity": "60%–80%",
        "plant_image": "plant_p001.png",
        "package_of_practices": {
            "propagation_material": "Rhizome division, tubers, offsets during spring repotting",
            "seed_rate": "2–3 rhizomes per container",
            "seed_spacing": "30–45 cm spacing",
            "sowing_method": "Dibbling rhizomes 5 cm deep in porous rich mix",
            "manuring": "NPK 19-19-19 liquid fertilizer monthly during spring-summer",
            "irrigation": "Regular watering when top 2 inches dry out; keep moist",
            "intercultural_practices": "Leaf dusting/wiping, trimming yellowed lower leaves",
            "plant_protection": "Neem oil spray for spider mites & mealybugs",
            "gestation_period": "3–4 weeks for new leaf emergence",
            "harvest_method": "Foliage pruning for display",
            "yield": "4–8 large decorative leaves per season"
        },
        "use": "Interior decor, air purification, tropical accent",
        "locality_source": "Local Nurseries & Online Outlets",
        "availability": "High",
        "price_inr": 450,
        "price_usd": 12.0
    },
    {
        "id": "P100",
        "english_name": "Sample Plant P100",
        "botanical_name": "Exotic specimen p100",
        "hindi_name": "Sample Plant (नमूना पौधा)",
        "varieties": ["Standard"],
        "category": ["Indoor", "Aesthetics"],
        "plant_type": "Evergreen foliage",
        "habit": "Upright",
        "height": "1.0 m",
        "spread": "0.5 m",
        "suitable_locations": ["Balconies", "Terrace"],
        "suitable_planters": '12" Ceramic Pot',
        "growing_season": "Spring",
        "nursery_sowing_time": "March",
        "seedling_transplanting_time": "April",
        "soil_type": "Loamy soil",
        "soil_ph": "6.5",
        "sun_intensity": "Bright indirect light",
        "humidity": "60%",
        "plant_image": "plant_p100.png",
        "package_of_practices": {
            "propagation_material": "Seeds",
            "seed_rate": "2 seeds",
            "seed_spacing": "20 cm",
            "sowing_method": "Direct",
            "manuring": "Compost",
            "irrigation": "Moderate",
            "intercultural_practices": "Weeding",
            "plant_protection": "Neem oil",
            "gestation_period": "4 weeks",
            "harvest_method": "Pruning",
            "yield": "High"
        },
        "use": "Decoration",
        "locality_source": "Local Nursery",
        "availability": "High",
        "price_inr": 500,
        "price_usd": 14.0
    }
]

# ------------------------------------------------------------------------------
# CSV DATA LOADER & PARSER
# ------------------------------------------------------------------------------
def load_csv_database(csv_path: str = DEFAULT_CSV_PATH) -> List[Dict[str, Any]]:
    """Loads and parses plant database records from CSV file."""
    search_paths = [
        csv_path,
        os.path.join(os.getcwd(), csv_path),
        os.path.join('/workspace/artifacts', csv_path),
        os.path.join('/workspace/out', csv_path),
        '/workspace/artifacts/plant_database_template.csv',
        '/workspace/scratch/plant_database_template.csv'
    ]
    target_path = None
    for p in search_paths:
        if os.path.exists(p) and os.path.isfile(p):
            target_path = p
            break

    if not target_path:
        return DEFAULT_PLANT_DATABASE

    records = []
    try:
        with open(target_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                plant_id = row.get("id", "").strip()
                eng_name = row.get("english_name", "").strip()
                if not plant_id or not eng_name:
                    continue

                cats = [c.strip() for c in row.get("category", "").replace(",", "|").split("|") if c.strip()]
                locs = [l.strip() for l in row.get("suitable_locations", "").replace(",", "|").split("|") if l.strip()]
                vars_list = [v.strip() for v in row.get("varieties", "").split(",") if v.strip()]

                try:
                    price_inr = float(row.get("price_inr", 250))
                except Exception:
                    price_inr = 250.0

                try:
                    price_usd = float(row.get("price_usd", 7.5))
                except Exception:
                    price_usd = 7.5

                pop = {
                    "propagation_material": row.get("propagation_material", "Stem cuttings / seeds"),
                    "seed_rate": row.get("seed_rate", "2–3 per container"),
                    "seed_spacing": row.get("seed_spacing", "15–20 cm"),
                    "sowing_method": row.get("sowing_method", "Direct potting in moist substrate"),
                    "manuring": row.get("manuring", "Balanced liquid fertilizer monthly"),
                    "irrigation": row.get("irrigation", "Water when top soil dries; drench then drought routine"),
                    "intercultural_practices": row.get("intercultural_practices", "Pruning dry leaves, foliage wiping"),
                    "plant_protection": row.get("plant_protection", "Neem oil spray for pests"),
                    "gestation_period": row.get("gestation_period", "3–4 weeks for establishment"),
                    "harvest_method": row.get("harvest_method", "Foliage pruning / stem trimming"),
                    "yield": row.get("yield", "Abundant healthy foliage")
                }

                rec = {
                    "id": plant_id,
                    "english_name": eng_name,
                    "botanical_name": row.get("botanical_name", eng_name).strip(),
                    "hindi_name": row.get("hindi_name", f"{eng_name} (पौधा)").strip(),
                    "varieties": vars_list if vars_list else [eng_name],
                    "category": cats if cats else ["Indoor", "Aesthetics"],
                    "plant_type": row.get("plant_type", "Evergreen foliage plant").strip(),
                    "habit": row.get("habit", "Upright clump").strip(),
                    "height": row.get("height", "30–90 cm").strip(),
                    "spread": row.get("spread", "20–50 cm").strip(),
                    "suitable_locations": locs if locs else ["small indoor eatout room", "Balconies"],
                    "suitable_planters": row.get("suitable_planters", '11" Slate Cylindrical Pot').strip(),
                    "plant_image": row.get("plant_image", f"{plant_id}.png").strip(),
                    "price_inr": price_inr,
                    "price_usd": price_usd,
                    "availability": row.get("availability", "High").strip(),
                    "locality_source": row.get("locality_source", "Local Nurseries").strip(),
                    "growing_season": row.get("growing_season", "Spring to Summer").strip(),
                    "nursery_sowing_time": row.get("nursery_sowing_time", "March–April").strip(),
                    "seedling_transplanting_time": row.get("seedling_transplanting_time", "April–May").strip(),
                    "soil_type": row.get("soil_type", "Well-draining potting mix").strip(),
                    "soil_ph": row.get("soil_ph", "6.0–7.0").strip(),
                    "sun_intensity": row.get("sun_intensity", "Bright indirect light").strip(),
                    "humidity": row.get("humidity", "50%–70%").strip(),
                    "use": row.get("use", "Indoor decor, air purification").strip(),
                    "package_of_practices": pop
                }
                records.append(rec)
    except Exception:
        return DEFAULT_PLANT_DATABASE

    return records if records else DEFAULT_PLANT_DATABASE

# ------------------------------------------------------------------------------
# DYNAMIC DIRECTORY ROUTER FOR P001-P099 & P100-P199
# ------------------------------------------------------------------------------
def get_target_asset_dir(plant_id: str) -> str:
    """Routes plant ID to the correct folder: P001-P099 -> plant_assets_D, P100-P199 -> plant_assets_D1."""
    clean_id = plant_id.strip().upper()
    try:
        if clean_id.startswith('P'):
            num_part = int(clean_id[1:])
            if 1 <= num_part <= 99:
                return DEFAULT_ASSET_DIR
            elif 100 <= num_part <= 199:
                return ALT_ASSET_DIR
    except ValueError:
        pass
    return DEFAULT_ASSET_DIR

def get_plant_image_path(plant_id: str, plant_image_filename: str = "") -> Tuple[Optional[str], str]:
    """Finds image asset and returns absolute path."""
    primary_dir = get_target_asset_dir(plant_id)
    search_dirs = [
        primary_dir,
        DEFAULT_ASSET_DIR,
        ALT_ASSET_DIR,
        os.path.abspath(DEFAULT_ASSET_DIR),
        os.path.abspath(ALT_ASSET_DIR),
        './plant_assets_D',
        './plant_assets_D1',
        '/workspace/scratch/plant_assets_D',
        '/workspace/artifacts/plant_assets_D',
        '/workspace/out/plant_assets_D'
    ]

    clean_id = plant_id.strip().lower()
    if not clean_id:
        return None, "Empty plant ID"

    seen = set()
    unique_search_dirs = [d for d in search_dirs if not (d in seen or seen.add(d))]

    for d in unique_search_dirs:
        if os.path.exists(d) and os.path.isdir(d):
            try:
                files = os.listdir(d)
            except Exception:
                continue

            candidates = [
                f"{clean_id}.png",
                f"{clean_id}.jpg",
                f"{clean_id}.jpeg",
                f"plant_{clean_id}.png",
                f"plant_{clean_id}.jpg",
                plant_image_filename.strip() if plant_image_filename else ""
            ]
            for cand in candidates:
                if cand and cand in files:
                    full_path = os.path.abspath(os.path.join(d, cand))
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        return full_path, f"Found exact match {full_path}"

            for f in files:
                stem, ext = os.path.splitext(f)
                if stem.lower() in [clean_id, f"plant_{clean_id}"]:
                    full_path = os.path.abspath(os.path.join(d, f))
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        return full_path, f"Found stem match {full_path}"

    return None, f"Image for ID '{clean_id}' not found in asset directories"

def ensure_plant_asset_image(plant_id: str, english_name: str, botanical_name: str) -> str:
    """Ensures a visual asset card exists in the target directory and returns absolute path."""
    target_dir = get_target_asset_dir(plant_id)
    os.makedirs(target_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(target_dir, f"{plant_id}.png"))
    
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return out_path

    try:
        img = Image.new('RGB', (600, 450), color=(245, 248, 242))
        draw = ImageDraw.Draw(img)
        draw.rectangle([15, 15, 585, 435], outline=(30, 80, 45), width=4)
        draw.rectangle([25, 25, 575, 80], fill=(30, 80, 45))
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
            font_sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf', 14)
            font_body = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        except Exception:
            font_title = font_sub = font_body = None

        draw.text((40, 35), f"ID: {plant_id} | {english_name.upper()[:28]}", fill=(255, 255, 255), font=font_title)
        if botanical_name:
            draw.text((40, 65), f"({botanical_name})", fill=(200, 235, 200), font=font_sub)

        draw.ellipse([200, 150, 400, 350], fill=(45, 115, 60), outline=(20, 60, 30), width=3)
        draw.polygon([(300, 120), (220, 230), (380, 230)], fill=(65, 145, 80))
        draw.line([(300, 130), (300, 310)], fill=(220, 245, 220), width=3)
        draw.text((40, 360), f"Filename: {plant_id}.png", fill=(60, 60, 60), font=font_body)
        draw.text((40, 390), f"Folder: {target_dir}", fill=(30, 80, 45), font=font_body)
        img.save(out_path)
    except Exception:
        pass

    return out_path

# ------------------------------------------------------------------------------
# CORE APPLICATION LOGIC ENGINE
# ------------------------------------------------------------------------------
class PlantSelectorEngine:
    def __init__(self, database: List[Dict[str, Any]] = None):
        self.database = database if database else load_csv_database()

    def filter_plants(self, category: Optional[str] = None, location: Optional[str] = None, max_budget_inr: Optional[float] = None, soil_type: Optional[str] = None, growing_season: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for plant in self.database:
            if category and category.lower() != "all":
                cats = [c.lower() for c in plant.get("category", [])]
                if category.lower() not in cats:
                    continue
            if location and location.lower() != "all":
                locs = [l.lower() for l in plant.get("suitable_locations", [])]
                if not any(location.lower() in l for l in locs):
                    continue
            if max_budget_inr is not None and max_budget_inr > 0:
                if plant.get("price_inr", 0) > max_budget_inr:
                    continue
            if soil_type and soil_type.lower() != "all":
                if soil_type.lower() not in plant.get("soil_type", "").lower():
                    continue
            if growing_season and growing_season.lower() != "all":
                if growing_season.lower() not in plant.get("growing_season", "").lower():
                    continue
            results.append(plant)
        return results

# ------------------------------------------------------------------------------
# STREAMLIT WEB GUI APPLICATION MODE
# ------------------------------------------------------------------------------
def run_streamlit_gui():
    import streamlit as st
    st.set_page_config(
        page_title="FresHerbal® Plant Selector App",
        page_icon="🌿",
        layout="wide"
    )

    st.title("🌿 FresHerbal® Smart Plant Selector & Cultivation Guide")
    st.markdown("""
    Select your specific criteria below (Category, Location, Budget, Soil Type, Growing Season) to discover suitable plant species along with their complete **Plant Visual Artwork**, **Botanical Specifications**, **Matched Planters**, and **Package of Practices (PoP)**.
    """)

    database_records = load_csv_database()
    engine = PlantSelectorEngine(database=database_records)

    categories = [
        "All", "Aromatic", "Aesthetics", "Medicinal", "Indoor", 
        "Spice hub", "Culinary", "Greens", "Vegifresh", "Fruit plants", "Other plants"
    ]
    locations = [
        "All", "small backyard garden", "small indoor eatout room", "garden walls", 
        "Trellis", "Patio", "Large town garden", "sunny rooftops", "shady rooftops", 
        "Terrace", "Balconies", "Frontgate", "Frontyard garden", "Front home door", 
        "Back home door", "open field"
    ]
    seasons = ["All", "Spring", "Summer", "Monsoon", "Autumn", "Winter"]

    # Sidebar Filter Controls
    st.sidebar.header("🎯 Filter Options")
    selected_cat = st.sidebar.selectbox("Plant Category", categories)
    selected_loc = st.sidebar.selectbox("Planting Location", locations)
    selected_season = st.sidebar.selectbox("Growing Season / Planting Time", seasons)
    max_price = st.sidebar.slider("Max Budget (INR)", min_value=50, max_value=3000, value=2500, step=50)
    soil_filter = st.sidebar.text_input("Soil Type Keyword (Optional)", placeholder="e.g. Peat, Sandy, Loam")

    # Perform Filter Query
    matches = engine.filter_plants(
        category=selected_cat if selected_cat != "All" else None,
        location=selected_loc if selected_loc != "All" else None,
        max_budget_inr=max_price,
        soil_type=soil_filter if soil_filter.strip() else None,
        growing_season=selected_season if selected_season != "All" else None
    )

    st.subheader(f"🔍 Matching Results ({len(matches)} Plants Found)")

    if not matches:
        st.warning("No plants matched your exact combination of filters. Try expanding your budget slider or setting Location/Category to 'All'.")
    else:
        for idx, p in enumerate(matches):
            plant_id = str(p.get("id", "")).strip()
            expander_key = f"exp_{plant_id}_{idx}"
            
            with st.expander(f"🌿 {p['english_name']} — ({p['botanical_name']}) | ID: {plant_id} | Price: ₹{p['price_inr']}", expanded=True):
                col1, col2, col3 = st.columns([1.2, 1.8, 2.0])

                img_path, img_msg = get_plant_image_path(plant_id, p.get("plant_image", ""))

                # Column 1: Plant Visual Artwork
                with col1:
                    st.markdown("##### 🌿 Plant Visual Artwork")
                    target_display_dir = get_target_asset_dir(plant_id)
                    
                    if not img_path or not os.path.exists(img_path):
                        img_path = ensure_plant_asset_image(plant_id, p.get("english_name", ""), p.get("botanical_name", ""))

                    if img_path and os.path.exists(img_path):
                        try:
                            pil_img = Image.open(img_path)
                            # Convert image to bytes stream to completely bypass local path caching issues in Streamlit expanders
                            buffered = BytesIO()
                            pil_img.save(buffered, format="PNG")
                            st.image(buffered.getvalue(), caption=f"ID: {plant_id} | {p['english_name']}", use_container_width=True)
                        except Exception as e:
                            st.image(img_path, caption=f"ID: {plant_id} | {p['english_name']}", use_container_width=True)
                    else:
                        st.info(f"Asset File: {target_display_dir}/{plant_id}.png")

                # Column 2: Botanical Specifications
                with col2:
                    st.markdown("##### 📋 Botanical Specifications")
                    st.markdown(f"**Database ID:** `{plant_id}`")
                    st.markdown(f"**Botanical Name:** `{p['botanical_name']}`")
                    st.markdown(f"**Hindi / Local Name:** {p['hindi_name']}")
                    st.markdown(f"**Varieties:** {', '.join(p['varieties'])}")
                    st.markdown(f"**Plant Type:** {p['plant_type']}")
                    st.markdown(f"**Habit:** {p['habit']}")
                    st.markdown(f"**Height & Spread:** {p['height']} | {p['spread']}")
                    st.markdown(f"**Recommended Planter:** 🏺 `{p['suitable_planters']}`")
                    st.markdown(f"**Locality Availability:** {p['availability']} ({p['locality_source']})")
                    st.markdown(f"**Estimated Price:** ₹{p['price_inr']} (~${p['price_usd']} USD)")

                # Column 3: Package of Practices & Cultivation
                with col3:
                    st.markdown("##### 🌱 Package of Practices (PoP)")
                    pop = p.get('package_of_practices', {})
                    st.markdown(f"- **Growing Season:** {p['growing_season']} | **Sowing:** {p['nursery_sowing_time']}")
                    st.markdown(f"- **Soil & pH:** {p['soil_type']} (pH {p['soil_ph']})")
                    st.markdown(f"- **Sun & Humidity:** {p['sun_intensity']} | Humidity {p['humidity']}")
                    st.markdown(f"- **Propagation:** {pop.get('propagation_material', '')}")
                    st.markdown(f"- **Sowing Method:** {pop.get('sowing_method', '')}")
                    st.markdown(f"- **Seed Rate & Spacing:** {pop.get('seed_rate', '')} | {pop.get('seed_spacing', '')}")
                    st.markdown(f"- **Manuring & Irrigation:** {pop.get('manuring', '')} | {pop.get('irrigation', '')}")
                    st.markdown(f"- **Intercultural Operations:** {pop.get('intercultural_practices', '')}")
                    st.markdown(f"- **Plant Protection:** {pop.get('plant_protection', '')}")
                    st.markdown(f"- **Gestation & Harvest:** {pop.get('gestation_period', '')} | {pop.get('harvest_method', '')}")
                    st.markdown(f"- **Yield & Primary Use:** {pop.get('yield', '')} | *{p.get('use', '')}*")

# ------------------------------------------------------------------------------
# TERMINAL CLI MODE
# ------------------------------------------------------------------------------
def run_cli():
    print("\n" + "="*80)
    print(" 🌿 FRESHERBAL® PLANT SELECTOR & CULTIVATION GUIDE APPLICATION")
    print("="*80)
    database_records = load_csv_database()
    engine = PlantSelectorEngine(database=database_records)
    print(f"Loaded {len(database_records)} plant records.")

if __name__ == "__main__":
    if "streamlit" in sys.modules or os.environ.get("STREAMLIT_SERVER_PORT") or any("streamlit" in arg for arg in sys.argv):
        run_streamlit_gui()
    else:
        run_cli()
