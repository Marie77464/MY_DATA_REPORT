import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="DAKAR_AUTO_SCRAPER",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design with pink Lamborghini background
st.markdown("""
    <style>
    .main {
        background: linear-gradient(rgba(26, 32, 44, 0.92), rgba(26, 32, 44, 0.92)),
                    url('https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?q=80&w=2070') center/cover no-repeat fixed;
    }
    .stApp {
        background: linear-gradient(rgba(26, 32, 44, 0.92), rgba(26, 32, 44, 0.92)),
                    url('https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?q=80&w=2070') center/cover no-repeat fixed;
    }
    h1 {
        color: #FFD700;
        text-align: center;
        font-size: 3.5em;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
        padding: 20px;
        animation: glow 2s ease-in-out infinite alternate;
        font-weight: bold;
        letter-spacing: 2px;
    }
    @keyframes glow {
        from { text-shadow: 3px 3px 6px rgba(0,0,0,0.8); }
        to { text-shadow: 0 0 30px rgba(255,215,0,0.8), 0 0 60px rgba(255,215,0,0.5); }
    }
    .stButton>button {
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 100%);
        color: #FFD700;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px 30px;
        border: 2px solid #FFD700;
        font-size: 1.2em;
        box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(255,215,0,0.6);
        background: linear-gradient(90deg, #2d3748 0%, #4a5568 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2em;
        color: #FFD700;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: #E2E8F0 !important;
    }
    .stSelectbox label, .stNumberInput label {
        color: #FFD700 !important;
        font-weight: bold;
    }
    h2, h3 {
        color: #FFD700 !important;
    }
    .stMarkdown p {
        color: #E2E8F0;
    }
    div[data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(255,215,0,0.4);
        border: 2px solid #FFD700;
    }
    div[data-testid="stDataFrame"] > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    div[data-testid="stDataFrame"] table {
        color: #000000 !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #1a202c !important;
        color: #FFD700 !important;
        font-weight: bold !important;
    }
    div[data-testid="stDataFrame"] td {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Database functions
def init_db():
    conn = sqlite3.connect('daka_auto.db')
    c = conn.cursor()
    
    # Table for cars
    c.execute('''CREATE TABLE IF NOT EXISTS voitures
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  brand TEXT, model TEXT, year TEXT, kilometer TEXT,
                  fuel_type TEXT, gearbox TEXT, adress TEXT,
                  owner TEXT, price TEXT, scraped_date TEXT)''')
    
    # Table for motos
    c.execute('''CREATE TABLE IF NOT EXISTS motos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  brand TEXT, year TEXT, kilometer TEXT,
                  adress TEXT, owner TEXT, price TEXT, scraped_date TEXT)''')
    
    # Table for car rental
    c.execute('''CREATE TABLE IF NOT EXISTS location
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  brand TEXT, year TEXT, adress TEXT,
                  owner TEXT, price TEXT, scraped_date TEXT)''')
    
    conn.commit()
    conn.close()

def save_to_db(df, table_name):
    df['scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('daka_auto.db')
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

def load_from_db(table_name):
    conn = sqlite3.connect('daka_auto.db')
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# Scraping functions
def scrape_voitures(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index in range(1, num_pages + 1):
        status_text.text(f'Scraping page {index}/{num_pages}...')
        progress_bar.progress(index / num_pages)
        
        url = f'https://dakar-auto.com/senegal/voitures-4?&page={index}'
        res = get(url)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item mb-md-3 mb-3')
        
        data = []
        for container in containers:
            try:
                gen_inf = container.find('h2', class_='listing-card__header__title mb-md-2 mb-0').a.text.strip().split()
                brand = gen_inf[0]
                model = " ".join(gen_inf[1:len(gen_inf)-1])
                year = gen_inf[-1]
                
                gen_inf1 = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                gen_inf2 = gen_inf1.find_all('li', 'listing-card__attribute list-inline-item')
                kms_driven = gen_inf2[1].text.replace('km','')
                gearbox = gen_inf2[2].text
                fuel_type = gen_inf2[3].text
                
                adress = container.find('div',class_='col-12 entry-zone-address').text
                owner = "".join(container.find('p', class_='time-author m-0').a.text).replace('Par','')
                price = "".join(container.find('h3','listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().split()).replace('FCFA','')
                
                dic = {
                    "brand": brand, "model": model, "year": year,
                    "kilometer": kms_driven, "fuel_type": fuel_type,
                    "gearbox": gearbox, "adress": adress,
                    "owner": owner, "price": price
                }
                data.append(dic)
            except:
                pass
        
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    
    df = df.drop_duplicates()
    progress_bar.empty()
    status_text.empty()
    return df

def scrape_motos(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index in range(1, num_pages + 1):
        status_text.text(f'Scraping page {index}/{num_pages}...')
        progress_bar.progress(index / num_pages)
        
        url = f'https://dakar-auto.com/senegal/motos-and-scooters-3?&page={index}'
        res = get(url)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item mb-md-3 mb-3')
        
        data = []
        for container in containers:
            try:
                gen_inf = container.find('h2', class_='listing-card__header__title mb-md-2 mb-0').a.text.strip().split()
                brand = gen_inf[0]
                year = gen_inf[-1]
                
                kms_driven = None
                gen_inf1 = container.find('ul', class_='listing-card__attribute-list list-inline mb-0')
                if gen_inf1:
                    gen_inf2 = gen_inf1.find_all('li', class_='listing-card__attribute list-inline-item')
                    if len(gen_inf2) > 1:
                        kms_driven = gen_inf2[1].text.replace('km', '')
                if not kms_driven:
                    kms_driven = "0"
                
                adress = container.find('div', class_='col-12 entry-zone-address').text
                owner = "".join(container.find('p', class_='time-author m-0').a.text).replace('Par','')
                price = "".join(container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().split()).replace('FCFA','')
                
                dic = {
                    "brand": brand, "year": year, "kilometer": kms_driven,
                    "adress": adress, "owner": owner, "price": price
                }
                data.append(dic)
            except:
                pass
        
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    
    df = df.drop_duplicates()
    progress_bar.empty()
    status_text.empty()
    return df

def scrape_location(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index in range(1, num_pages + 1):
        status_text.text(f'Scraping page {index}/{num_pages}...')
        progress_bar.progress(index / num_pages)
        
        url = f'https://dakar-auto.com/senegal/location-de-voitures-19?&page={index}'
        res = get(url)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item mb-md-3 mb-3')
        
        data = []
        for container in containers:
            try:
                gen_inf = container.find('h2',class_='listing-card__header__title mb-md-2 mb-0').a.text.strip().split()
                brand = gen_inf[0]
                year = gen_inf[-1]
                
                owner = "".join(container.find('p',class_='time-author m-0').a.text).replace('Par','')
                adress = container.find('div', class_='col-12 entry-zone-address').text
                price = "".join(container.find('h3','listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().split()).replace('FCFA','')
                
                dic = {
                    "brand": brand, "year": year, "adress": adress,
                    "owner": owner, "price": price
                }
                data.append(dic)
            except:
                pass
        
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    
    df = df.drop_duplicates()
    progress_bar.empty()
    status_text.empty()
    return df

# Initialize database
init_db()

# Main title
st.markdown("<h1>🚗 DAKAR_AUTO_SCRAPER 🏍️</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/car.png")
    st.markdown("### 📊 Navigation")
    menu = st.radio(
        "",
        ["🏠 Home", "🔍 Scraper", "📈 Dashboard", "📁 View Data", "📝 Web Evaluation App"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("DAKAR_AUTO_SCRAPER is a powerful tool to scrape and analyze car data from Dakar-Auto.com")

# HOME PAGE
if menu == "🏠 Home":
    st.markdown("## 👋 Welcome to DAKAR_AUTO_SCRAPER!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='background: rgba(26, 32, 44, 0.9); padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(255,215,0,0.3); border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700;'>🚗 Cars</h3>
            <p style='color: #E2E8F0;'>Scrape detailed car listings including brand, model, year, and more!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(26, 32, 44, 0.9); padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(255,215,0,0.3); border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700;'>🏍️ Motos</h3>
            <p style='color: #E2E8F0;'>Get information about motorcycles and scooters available in Senegal!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: rgba(26, 32, 44, 0.9); padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(255,215,0,0.3); border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700;'>🔑 Location</h3>
            <p style='color: #E2E8F0;'>Explore car rental options with pricing and availability!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Start Guide")
    st.markdown("""
    <div style='color: #E2E8F0;'>
    <ol>
        <li><strong>Go to Scraper</strong> - Choose your data source and number of pages</li>
        <li><strong>Run the scraper</strong> - Get fresh data from Dakar-Auto.com</li>
        <li><strong>View Dashboard</strong> - Analyze the scraped data with beautiful charts</li>
        <li><strong>View Data</strong> - Browse and download your scraped data</li>
        <li><strong>Web Evaluation</strong> - Fill out evaluation forms</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 View Pre-Scraped Data")
    st.markdown("""
    <div style='color: #E2E8F0; margin-bottom: 20px;'>
        <p>Click on a button below to view the pre-scraped data:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚗 View Cars Data", key="view_cars", use_container_width=True):
            st.session_state['show_csv'] = 'cars'
    
    with col2:
        if st.button("🏍️ View Motos Data", key="view_motos", use_container_width=True):
            st.session_state['show_csv'] = 'motos'
    
    with col3:
        if st.button("🔑 View Location Data", key="view_location", use_container_width=True):
            st.session_state['show_csv'] = 'location'
    
    # Display data based on button clicked
    if 'show_csv' in st.session_state:
        st.markdown("---")
        
        if st.session_state['show_csv'] == 'cars':
            st.markdown("### 🚗 Cars Data from GitHub")
            try:
                with st.spinner('Loading cars data...'):
                    df = pd.read_csv("https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/auto_voiture_scraper.csv")
                    st.success(f"✅ Loaded {len(df)} cars records")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Cars CSV",
                        data=csv,
                        file_name=f"cars_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
        
        elif st.session_state['show_csv'] == 'motos':
            st.markdown("### 🏍️ Motos Data from GitHub")
            try:
                with st.spinner('Loading motos data...'):
                    df = pd.read_csv("https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/motos_and_scooters.csv")
                    st.success(f"✅ Loaded {len(df)} motos records")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Motos CSV",
                        data=csv,
                        file_name=f"motos_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
        
        elif st.session_state['show_csv'] == 'location':
            st.markdown("### 🔑 Location Data from GitHub")
            try:
                with st.spinner('Loading location data...'):
                    df = pd.read_csv("https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/location_de_voiture.csv")
                    st.success(f"✅ Loaded {len(df)} rental cars records")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Location CSV",
                        data=csv,
                        file_name=f"location_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")

# SCRAPER PAGE
elif menu == "🔍 Scraper":
    st.markdown("## 🔍 Start Scraping")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url_choice = st.selectbox(
            "📍 Select data source:",
            ["🚗 Voitures (Cars)", "🏍️ Motos & Scooters", "🔑 Location de Voitures (Car Rental)"]
        )
    
    with col2:
        num_pages = st.number_input("📄 Number of pages:", min_value=1, max_value=50, value=1)
    
    st.markdown("---")
    
    if st.button("🚀 Start Scraping", use_container_width=True):
        with st.spinner('🔄 Scraping in progress...'):
            try:
                if "Voitures" in url_choice and "Location" not in url_choice:
                    df = scrape_voitures(num_pages)
                    if len(df) > 0:
                        save_to_db(df, 'voitures')
                        st.success(f'✅ Successfully scraped {len(df)} cars!')
                        st.balloons()
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("⚠️ No data found. Please try again.")
                    
                elif "Motos" in url_choice:
                    df = scrape_motos(num_pages)
                    if len(df) > 0:
                        save_to_db(df, 'motos')
                        st.success(f'✅ Successfully scraped {len(df)} motos!')
                        st.balloons()
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("⚠️ No data found. Please try again.")
                    
                elif "Location" in url_choice:
                    df = scrape_location(num_pages)
                    if len(df) > 0:
                        save_to_db(df, 'location')
                        st.success(f'✅ Successfully scraped {len(df)} rental cars!')
                        st.balloons()
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("⚠️ No data found. Please try again.")
                
            except Exception as e:
                st.error(f'❌ Error during scraping: {str(e)}')

# DASHBOARD PAGE
elif menu == "📈 Dashboard":
    st.markdown("## 📈 Data Analytics Dashboard")
    
    data_type = st.selectbox(
        "Select data to visualize:",
        ["Voitures", "Motos", "Location"]
    )
    
    table_map = {"Voitures": "voitures", "Motos": "motos", "Location": "location"}
    
    # Load data based on source selection
    if data_source == "📁 From GitHub CSV Files":
        # GitHub raw URLs for your CSV files in data folder
        github_csv_urls = {
            "Voitures": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/auto_voiture_scraper.csv",
            "Motos": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/motos_and_scooters.csv",
            "Location": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/location_de_voiture.csv"
        }
        
        try:
            with st.spinner(f'Loading {data_type} from GitHub...'):
                df = pd.read_csv(github_csv_urls[data_type])
                st.success(f"✅ Loaded {len(df)} records from GitHub CSV file")
        except Exception as e:
            st.error(f"❌ Error loading CSV from GitHub: {str(e)}")
            st.info("💡 Make sure your CSV files are in the 'data' folder on GitHub with these names: auto_voiture_scraper.csv, motos_and_scooters.csv, location_de_voiture.csv")
            df = pd.DataFrame()
    else:
        # Load from database
        df = load_from_db(table_map[data_type])
    
    if len(df) > 0:
        # Remove scraped_date and id for analysis
        df_clean = df.drop(['scraped_date', 'id'], axis=1, errors='ignore')
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", len(df_clean))
        with col2:
            st.metric("🏷️ Unique Brands", df_clean['brand'].nunique())
        with col3:
            if 'price' in df_clean.columns:
                try:
                    avg_price = df_clean['price'].str.replace(',', '').astype(float).mean()
                    st.metric("💰 Avg Price (FCFA)", f"{avg_price:,.0f}")
                except:
                    st.metric("💰 Avg Price (FCFA)", "N/A")
        with col4:
            st.metric("📅 Latest Year", df_clean['year'].max() if 'year' in df_clean.columns else "N/A")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Brand distribution
            brand_counts = df_clean['brand'].value_counts().head(10)
            fig1 = px.bar(
                x=brand_counts.values,
                y=brand_counts.index,
                orientation='h',
                title="Top 10 Brands",
                labels={'x': 'Count', 'y': 'Brand'},
                color=brand_counts.values,
                color_continuous_scale='YlOrRd'
            )
            fig1.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(26, 32, 44, 0.8)',
                paper_bgcolor='rgba(26, 32, 44, 0.8)',
                font=dict(color='#FFD700')
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Year distribution
            if 'year' in df_clean.columns:
                year_counts = df_clean['year'].value_counts().sort_index()
                fig2 = px.line(
                    x=year_counts.index,
                    y=year_counts.values,
                    title="Vehicles by Year",
                    labels={'x': 'Year', 'y': 'Count'},
                    markers=True
                )
                fig2.update_traces(line_color='#FFD700', marker=dict(color='#FFD700', size=10))
                fig2.update_layout(
                    plot_bgcolor='rgba(26, 32, 44, 0.8)',
                    paper_bgcolor='rgba(26, 32, 44, 0.8)',
                    font=dict(color='#FFD700')
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Price distribution
        if 'price' in df_clean.columns:
            st.markdown("### 💰 Price Distribution")
            try:
                df_clean['price_numeric'] = df_clean['price'].str.replace(',', '').astype(float)
                fig3 = px.histogram(
                    df_clean,
                    x='price_numeric',
                    nbins=30,
                    title="Price Distribution",
                    labels={'price_numeric': 'Price (FCFA)'},
                    color_discrete_sequence=['#FFD700']
                )
                fig3.update_layout(
                    plot_bgcolor='rgba(26, 32, 44, 0.8)',
                    paper_bgcolor='rgba(26, 32, 44, 0.8)',
                    font=dict(color='#FFD700')
                )
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("⚠️ Could not create price distribution chart")
        
    else:
        st.warning("⚠️ No data available. Please scrape some data first!")

# VIEW DATA PAGE
elif menu == "📁 View Data":
    st.markdown("## 📁 View Scraped Data")
    
    # Option to load from GitHub CSV files
    st.markdown("### 📥 Load Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["📊 From Database (Scraped Data)", "📁 From GitHub CSV Files"],
        horizontal=True
    )
    
    data_type = st.selectbox(
        "Select data to view:",
        ["Voitures", "Motos", "Location"]
    )
    
    table_map = {"Voitures": "voitures", "Motos": "motos", "Location": "location"}
    df = load_from_db(table_map[data_type])
    
    if len(df) > 0:
        st.success(f"✅ Found {len(df)} records in {data_type} table")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search in data:", "")
        with col2:
            if st.button("🗑️ Clear Table"):
                confirm = st.checkbox("⚠️ Confirm deletion")
                if confirm:
                    conn = sqlite3.connect('daka_auto.db')
                    conn.execute(f"DELETE FROM {table_map[data_type]}")
                    conn.commit()
                    conn.close()
                    st.success("✅ Table cleared!")
                    st.rerun()
        
        # Filter dataframe
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df = df[mask]
        
        st.dataframe(df, use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.warning("⚠️ No data available in this table. Please scrape some data first!")

# WEB EVALUATION APP PAGE
elif menu == "📝 Web Evaluation App":
    st.markdown("## 📝 Web Application Evaluation Forms")
    
    st.markdown("### Please fill out one of the evaluation forms below:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: rgba(26, 32, 44, 0.9); padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(255,215,0,0.3); border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700;'>📋 Google Form</h3>
            <p style='color: #E2E8F0;'>Evaluate the web application using Google Forms</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔗 Open Google Form", key="google", use_container_width=True):
            st.components.v1.iframe("https://docs.google.com/forms/d/e/1FAIpQLSeL5dzKVxgxD-rOZqLLiDWmIE1dPhBjeeYcrEl3_EcTGeH2zw/viewform?embedded=true", height=800, scrolling=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(26, 32, 44, 0.9); padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(255,215,0,0.3); border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700;'>📊 KoboToolbox Form</h3>
            <p style='color: #E2E8F0;'>Evaluate the web application using KoboToolbox</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔗 Open KoboToolbox Form", key="kobo", use_container_width=True):
            st.components.v1.iframe("https://ee.kobotoolbox.org/x/uYmlZU5X", height=800, scrolling=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(26, 32, 44, 0.8); padding: 15px; border-radius: 8px; border-left: 4px solid #FFD700;'>
        <p style='color: #E2E8F0; margin: 0;'>💡 <strong>Tip:</strong> You can open the forms in a new tab by right-clicking the buttons and selecting 'Open in new tab'</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #FFD700; background: rgba(26, 32, 44, 0.8); padding: 15px; border-radius: 10px;'>
    <p style='margin: 0;'><strong>Made with ❤️ by MARIE PAUL BASSE | © 2024 DAKAR_AUTO_SCRAPER</strong></p>
</div>
""", unsafe_allow_html=True)
