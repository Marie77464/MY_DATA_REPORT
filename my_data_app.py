import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob

# Check if plotly is available
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Dakar Auto Scraper",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for elegant automotive theme with pink Lamborghini background
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Montserrat', sans-serif;
    }
    
    .stApp {
        background-image: url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    .main {
        padding: 2rem;
        background-color: transparent;
    }
    
    /* Sidebar styling - WHITE */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        box-shadow: 2px 0 20px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Buttons - PINK GRADIENT */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FFB6D9 0%, #FF69B4 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 0.9rem;
        font-weight: 600;
        border: 2px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.4);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 105, 180, 0.6);
        border-color: #ffffff;
    }
    
    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FFB6D9 0%, #FF69B4 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 0.9rem;
        font-weight: 600;
        border: 2px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.4);
    }
    
    /* Radio buttons in sidebar - PINK TEXT */
    [data-testid="stSidebar"] .stRadio > label {
        background: transparent;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
        font-weight: 500;
        color: #FF1493;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 20, 147, 0.1);
        transform: translateX(5px);
    }
    
    /* Header styling */
    .header-style {
        font-size: 4rem;
        font-weight: 700;
        color: #FF1493;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .subheader-style {
        font-size: 1.3rem;
        color: #FF69B4;
        text-align: center;
        margin-bottom: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Info box - WHITE */
    .info-box {
        background: rgba(255, 255, 255, 0.98);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(255, 20, 147, 0.3);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .info-box h3 {
        color: #FF1493;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .info-box p, .info-box ul {
        color: #333333;
        line-height: 1.8;
    }
    
    .info-box a {
        color: #FF1493;
        font-weight: 600;
        text-decoration: none;
        border-bottom: 2px solid #FF1493;
        transition: all 0.3s ease;
    }
    
    .info-box a:hover {
        color: #FF69B4;
        border-bottom-color: #FF69B4;
    }
    
    /* Content sections - WHITE */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Metrics - WHITE */
    div[data-testid="stMetricValue"] {
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 10px;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #FF1493;
        font-weight: 600;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FF1493;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.9);
        font-weight: 700;
    }
    
    /* Text elements */
    .stMarkdown {
        color: #FF1493;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    
    /* Input fields - WHITE */
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        border: 2px solid rgba(0,0,0,0.1);
        font-weight: 600;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
    }
    
    /* Expander - WHITE */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Progress bar - WHITE/GREY */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ffffff 0%, #cccccc 100%);
    }
    
    /* Success/Warning/Info messages - WHITE */
    .stSuccess, .stWarning, .stInfo, .stError {
        background: rgba(255, 255, 255, 0.95);
        color: #000000;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar title - PINK */
    [data-testid="stSidebar"] h1 {
        color: #FF1493;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #333333;
    }
    
    [data-testid="stSidebar"] .stInfo {
        background: rgba(255, 20, 147, 0.1);
        color: #333333;
        border-radius: 10px;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="header-style">🚗 DAKAR AUTO SCRAPER</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader-style">Welcome to the Ultimate Car Data Extraction Platform</p>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
    <div class="info-box">
    <h3>Welcome!</h3>
    <p>Welcome to <strong>Dakar Auto Scraper</strong> - your professional tool designed specifically to extract and analyze vehicle data from <strong>Dakar-Auto.com</strong>, Senegal's leading automotive marketplace!</p>
    
    <p><strong>What can you do here?</strong></p>
    <ul>
        <li><strong>Scrape live data</strong> - Extract fresh listings from multiple pages</li>
        <li><strong>Access pre-scraped data</strong> - Download ready-to-use datasets</li>
        <li><strong>Visualize insights</strong> - Explore interactive dashboards and analytics</li>
        <li><strong>Share feedback</strong> - Help us improve with your valuable input</li>
    </ul>
    
    <p><strong>Powered by:</strong> Python, Streamlit, BeautifulSoup, Pandas, Plotly</p>
    
    <p><strong>Data sources from Dakar-Auto.com:</strong></p>
    <ul>
        <li><a href="https://dakar-auto.com/senegal/voitures-4" target="_blank">Used Cars</a></li>
        <li><a href="https://dakar-auto.com/senegal/motos-and-scooters-3" target="_blank">Motorcycles and Scooters</a></li>
        <li><a href="https://dakar-auto.com/senegal/location-de-voitures-19" target="_blank">Car Rentals</a></li>
    </ul>
    
    <p>Get started by choosing an option from the menu on the left!</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("Navigation Menu")
st.sidebar.markdown("---")

menu_option = st.sidebar.radio(
    "Choose an option:",
    ["Scrape Data", "Download Pre-scraped Data", "Dashboard", "App Evaluation"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("Tip: Start by scraping data or download existing data!")

# Scraping function
def scrape_data(num_pages):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index in range(1, num_pages + 1):
        status_text.text(f"Scraping page {index}/{num_pages}...")
        progress_bar.progress(index / num_pages)
        
        url = f'https://dakar-auto.com/senegal/voitures-4?page={index}'
        
        try:
            res = get(url, timeout=10)
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
                    
                    kms_driven = gen_inf2[1].text.replace('km', '').strip()
                    gearbox = gen_inf2[2].text.strip()
                    fuel_type = gen_inf2[3].text.strip()
                    
                    owner = "".join(container.find('p', class_='time-author m-0').a.text).replace('Par', '').strip()
                    price = "".join(container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().split()).replace('FCFA', '')
                    
                    dic = {
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "kilometer": kms_driven,
                        "fuel_type": fuel_type,
                        "gearbox": gearbox,
                        "owner": owner,
                        "price": price,
                    }
                    data.append(dic)
                except:
                    pass
            
            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
        except Exception as e:
            st.error(f"Error scraping page {index}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return df

# Initialize session state for scraped data
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None

# Option 1: Scrape data
if menu_option == "Scrape Data":
    st.header("Scrape Car Listings")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        num_pages = st.number_input(
            "How many pages do you want to scrape?",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            help="Each page contains approximately 20-30 listings"
        )
    
    with col2:
        st.metric("Estimated listings", f"~{num_pages * 25}")
    
    if st.button("Start Scraping", key="scrape_btn"):
        with st.spinner("Scraping in progress..."):
            df = scrape_data(num_pages)
        
        if not df.empty:
            st.success(f"Scraping completed! {len(df)} listings retrieved.")
            
            # Display data
            st.subheader("Data Preview")
            st.dataframe(df, use_container_width=True)
            
            # Quick statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total listings", len(df))
            with col2:
                st.metric("Unique brands", df['brand'].nunique())
            with col3:
                st.metric("Average price", f"{df['price'].str.replace(' ', '').astype(float).mean():,.0f} FCFA")
            with col4:
                st.metric("Most recent year", df['year'].max())
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"dakar_auto_listings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data was retrieved.")

# Option 2: Download pre-scraped data
elif menu_option == "Download Pre-scraped Data":
    st.header("Pre-scraped Data (Uncleaned)")
    
    data_folder = "data"
    else:
        # Local files option
        data_folder = "data"
    
        if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
        
        if csv_files:
            st.info(f"{len(csv_files)} CSV file(s) available in the 'data/' folder")
            
            for csv_file in csv_files:
                file_name = os.path.basename(csv_file)
                file_size = os.path.getsize(csv_file) / 1024  # in KB
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{file_name}**")
                with col2:
                    st.write(f"{file_size:.1f} KB")
                with col3:
                    with open(csv_file, "rb") as f:
                        st.download_button(
                            "Download",
                            data=f,
                            file_name=file_name,
                            mime="text/csv",
                            key=file_name
                        )
                
                # Preview
                with st.expander(f"Preview {file_name}"):
                    df_preview = pd.read_csv(csv_file)
                    st.dataframe(df_preview.head(10), use_container_width=True)
                    st.caption(f"Showing first 10 rows out of {len(df_preview)} total")
                
                st.markdown("---")
        else:
            st.warning("No CSV files found in the 'data/' folder")
    else:
        st.error("The 'data/' folder does not exist. Please create this folder and add your CSV files.")

# Option 3: Dashboard
elif menu_option == "Dashboard":
    st.header("Data Dashboard (Cleaned)")
    
    # Data source selection
    data_source = st.radio(
        "Choose data source:",
        ["Local Files (data folder)", "From GitHub CSV Files"],
        horizontal=True
    )
    
    if data_source == "From GitHub CSV Files":
        # Select file type
        data_type = st.selectbox(
            "Select vehicle type:",
            ["Used Cars", "Motorcycles and Scooters", "Car Rentals"]
        )
        
        # GitHub raw URLs for CSV files
        github_csv_urls = {
            "Used Cars": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/auto_voiture_scraper.csv",
            "Motorcycles and Scooters": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/motos_and_scooters.csv",
            "Car Rentals": "https://raw.githubusercontent.com/Marie77464/MY_DATA_REPORT/refs/heads/master/data/location_de_voiture.csv"
        }
        
        try:
            with st.spinner(f'Loading {data_type} from GitHub...'):
                df = pd.read_csv(github_csv_urls[data_type])
                st.success(f"Loaded {len(df)} records from GitHub CSV file")
        except Exception as e:
            st.error(f"Error loading CSV from GitHub: {str(e)}")
            st.info("Make sure your CSV files are in the 'data' folder on GitHub")
            df = pd.DataFrame()
        
        if not df.empty:
            st.subheader("General Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total records", len(df))
            
            # Statistics based on file type and available columns
            if data_type == "Used Cars":
                # Columns: price, owner, adress, web_scraper_order, web_scraper_start_url
                with col2:
                    st.metric("Unique owners", df['owner'].nunique() if 'owner' in df.columns else 'N/A')
                with col3:
                    if 'price' in df.columns:
                        try:
                            prices = pd.to_numeric(df['price'].astype(str).str.replace(' ', '').str.replace(',', ''), errors='coerce')
                            st.metric("Average price", f"{prices.mean():,.0f} FCFA")
                        except:
                            st.metric("Average price", "N/A")
                with col4:
                    st.metric("Locations", df['adress'].nunique() if 'adress' in df.columns else 'N/A')
            
            elif data_type == "Car Rentals":
                # Columns: brand, brand_year, price, owner, adress, web_scraper_order, web_scraper_start_url
                with col2:
                    st.metric("Unique brands", df['brand'].nunique() if 'brand' in df.columns else 'N/A')
                with col3:
                    if 'price' in df.columns:
                        try:
                            prices = pd.to_numeric(df['price'].astype(str).str.replace(' ', '').str.replace(',', ''), errors='coerce')
                            st.metric("Average price", f"{prices.mean():,.0f} FCFA")
                        except:
                            st.metric("Average price", "N/A")
                with col4:
                    if 'brand_year' in df.columns:
                        try:
                            years = pd.to_numeric(df['brand_year'], errors='coerce')
                            st.metric("Average year", f"{years.mean():.0f}")
                        except:
                            st.metric("Average year", "N/A")
            
            elif data_type == "Motorcycles and Scooters":
                # Columns: web_scraper_order, web_scraper_start_url, adress, owner, price, brand_year
                with col2:
                    st.metric("Unique owners", df['owner'].nunique() if 'owner' in df.columns else 'N/A')
                with col3:
                    if 'price' in df.columns:
                        try:
                            prices = pd.to_numeric(df['price'].astype(str).str.replace(' ', '').str.replace(',', ''), errors='coerce')
                            st.metric("Average price", f"{prices.mean():,.0f} FCFA")
                        except:
                            st.metric("Average price", "N/A")
                with col4:
                    if 'brand_year' in df.columns:
                        try:
                            years = pd.to_numeric(df['brand_year'], errors='coerce')
                            st.metric("Average year", f"{years.mean():.0f}")
                        except:
                            st.metric("Average year", "N/A")
            
            # Display dataframe
            st.subheader("Data Table")
            st.dataframe(df, use_container_width=True)
            
            # Charts section
            if PLOTLY_AVAILABLE:
                st.subheader("Visual Analytics")
                
                # Charts based on available columns
                if data_type == "Used Cars":
                    col1, col2 = st.columns(2)
                    
                    # Price distribution
                    if 'price' in df.columns:
                        with col1:
                            st.markdown("**Price Distribution**")
                            df_price = df.copy()
                            df_price['price_numeric'] = pd.to_numeric(
                                df_price['price'].astype(str).str.replace(' ', '').str.replace(',', ''),
                                errors='coerce'
                            )
                            df_price = df_price.dropna(subset=['price_numeric'])
                            
                            fig1 = px.histogram(df_price, x='price_numeric', nbins=30,
                                               color_discrete_sequence=['#FF69B4'])
                            fig1.update_layout(height=400, xaxis_title="Price (FCFA)", yaxis_title="Count",
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    # Top locations
                    if 'adress' in df.columns:
                        with col2:
                            st.markdown("**Top 10 Locations**")
                            location_counts = df['adress'].value_counts().head(10).reset_index()
                            location_counts.columns = ['Location', 'Count']
                            
                            fig2 = px.bar(location_counts, x='Location', y='Count',
                                         color='Count', color_continuous_scale='Pinkyl')
                            fig2.update_layout(height=400, showlegend=False,
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig2, use_container_width=True)
                
                elif data_type == "Car Rentals":
                    col1, col2 = st.columns(2)
                    
                    # Brand distribution
                    if 'brand' in df.columns:
                        with col1:
                            st.markdown("**Top 10 Brands**")
                            brand_counts = df['brand'].value_counts().head(10).reset_index()
                            brand_counts.columns = ['Brand', 'Count']
                            
                            fig1 = px.bar(brand_counts, x='Brand', y='Count',
                                         color='Count', color_continuous_scale='Pinkyl')
                            fig1.update_layout(height=400, showlegend=False,
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    # Year distribution
                    if 'brand_year' in df.columns:
                        with col2:
                            st.markdown("**Year Distribution**")
                            df_year = df.copy()
                            df_year['year_numeric'] = pd.to_numeric(df_year['brand_year'], errors='coerce')
                            df_year = df_year.dropna(subset=['year_numeric'])
                            
                            year_counts = df_year['year_numeric'].value_counts().sort_index().reset_index()
                            year_counts.columns = ['Year', 'Count']
                            
                            fig2 = px.line(year_counts, x='Year', y='Count', markers=True,
                                          color_discrete_sequence=['#FF1493'])
                            fig2.update_layout(height=400, xaxis_title="Year", yaxis_title="Count",
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    # Price analysis
                    if 'price' in df.columns and 'brand' in df.columns:
                        st.markdown("**Average Price by Brand (Top 10)**")
                        df_price = df.copy()
                        df_price['price_numeric'] = pd.to_numeric(
                            df_price['price'].astype(str).str.replace(' ', '').str.replace(',', ''),
                            errors='coerce'
                        )
                        df_price = df_price.dropna(subset=['price_numeric'])
                        
                        top_10_brands = df['brand'].value_counts().head(10).index
                        df_top = df_price[df_price['brand'].isin(top_10_brands)]
                        avg_price = df_top.groupby('brand')['price_numeric'].mean().sort_values(ascending=False).reset_index()
                        avg_price.columns = ['Brand', 'Average Price']
                        
                        fig3 = px.bar(avg_price, x='Brand', y='Average Price',
                                     color='Average Price', color_continuous_scale='Pinkyl')
                        fig3.update_layout(height=400, showlegend=False,
                                         paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                        st.plotly_chart(fig3, use_container_width=True)
                
                elif data_type == "Motorcycles and Scooters":
                    col1, col2 = st.columns(2)
                    
                    # Price distribution
                    if 'price' in df.columns:
                        with col1:
                            st.markdown("**Price Distribution**")
                            df_price = df.copy()
                            df_price['price_numeric'] = pd.to_numeric(
                                df_price['price'].astype(str).str.replace(' ', '').str.replace(',', ''),
                                errors='coerce'
                            )
                            df_price = df_price.dropna(subset=['price_numeric'])
                            
                            fig1 = px.histogram(df_price, x='price_numeric', nbins=30,
                                               color_discrete_sequence=['#FF69B4'])
                            fig1.update_layout(height=400, xaxis_title="Price (FCFA)", yaxis_title="Count",
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    # Year distribution
                    if 'brand_year' in df.columns:
                        with col2:
                            st.markdown("**Year Distribution**")
                            df_year = df.copy()
                            df_year['year_numeric'] = pd.to_numeric(df_year['brand_year'], errors='coerce')
                            df_year = df_year.dropna(subset=['year_numeric'])
                            
                            year_counts = df_year['year_numeric'].value_counts().sort_index().reset_index()
                            year_counts.columns = ['Year', 'Count']
                            
                            fig2 = px.line(year_counts, x='Year', y='Count', markers=True,
                                          color_discrete_sequence=['#FF1493'])
                            fig2.update_layout(height=400, xaxis_title="Year", yaxis_title="Count",
                                             paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Install Plotly for interactive charts: pip install plotly")
    
    else:
        # Local files option
        data_folder = "data"
    
    if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
        
        if csv_files:
            selected_file = st.selectbox("Choose a file to visualize:", csv_files)
            
            if selected_file:
                df = pd.read_csv(selected_file)
                
                st.subheader("General Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total listings", len(df))
                with col2:
                    if 'brand' in df.columns:
                        st.metric("Brands", df['brand'].nunique())
                with col3:
                    if 'price' in df.columns:
                        prices = pd.to_numeric(df['price'].astype(str).str.replace(' ', '').str.replace(',', ''), errors='coerce')
                        st.metric("Average price", f"{prices.mean():,.0f} FCFA")
                with col4:
                    if 'year' in df.columns:
                        st.metric("Average year", f"{pd.to_numeric(df['year'], errors='coerce').mean():.0f}")
                
                # Display dataframe
                st.subheader("Data Table")
                st.dataframe(df, use_container_width=True)
                
                # Charts section
                st.subheader("Visual Analytics")
                
                if PLOTLY_AVAILABLE:
                    # Top brands chart
                    if 'brand' in df.columns:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Top 10 Brands**")
                            top_brands = df['brand'].value_counts().head(10).reset_index()
                            top_brands.columns = ['Brand', 'Count']
                            fig1 = px.bar(top_brands, x='Brand', y='Count', 
                                         color='Count',
                                         color_continuous_scale='Greys')
                            fig1.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            st.markdown("**Brand Distribution**")
                            fig2 = px.pie(top_brands, values='Count', names='Brand',
                                         color_discrete_sequence=px.colors.sequential.gray)
                            fig2.update_layout(height=400, paper_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    # Fuel type and gearbox
                    if 'fuel_type' in df.columns or 'gearbox' in df.columns:
                        col1, col2 = st.columns(2)
                        
                        if 'fuel_type' in df.columns:
                            with col1:
                                st.markdown("**Fuel Type Distribution**")
                                fuel_counts = df['fuel_type'].value_counts().reset_index()
                                fuel_counts.columns = ['Fuel Type', 'Count']
                                fig3 = px.bar(fuel_counts, x='Fuel Type', y='Count',
                                             color='Count',
                                             color_continuous_scale='Greys')
                                fig3.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                                st.plotly_chart(fig3, use_container_width=True)
                        
                        if 'gearbox' in df.columns:
                            with col2:
                                st.markdown("**Gearbox Type Distribution**")
                                gearbox_counts = df['gearbox'].value_counts().reset_index()
                                gearbox_counts.columns = ['Gearbox', 'Count']
                                fig4 = px.pie(gearbox_counts, values='Count', names='Gearbox',
                                             color_discrete_sequence=px.colors.sequential.gray)
                                fig4.update_layout(height=400, paper_bgcolor='rgba(255,255,255,0.95)')
                                st.plotly_chart(fig4, use_container_width=True)
                    
                    # Price analysis
                    if 'price' in df.columns:
                        st.markdown("**Price Analysis**")
                        df_price = df.copy()
                        df_price['price_numeric'] = pd.to_numeric(
                            df_price['price'].astype(str).str.replace(' ', '').str.replace(',', ''), 
                            errors='coerce'
                        )
                        df_price = df_price.dropna(subset=['price_numeric'])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Price Distribution**")
                            fig5 = px.histogram(df_price, x='price_numeric', nbins=30,
                                               color_discrete_sequence=['#333333'])
                            fig5.update_layout(height=400, xaxis_title="Price (FCFA)", yaxis_title="Count", paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                            st.plotly_chart(fig5, use_container_width=True)
                        
                        with col2:
                            if 'brand' in df.columns:
                                st.markdown("**Average Price by Brand (Top 10)**")
                                top_10_brands = df['brand'].value_counts().head(10).index
                                df_top_brands = df_price[df_price['brand'].isin(top_10_brands)]
                                avg_price_by_brand = df_top_brands.groupby('brand')['price_numeric'].mean().sort_values(ascending=False).reset_index()
                                avg_price_by_brand.columns = ['Brand', 'Average Price']
                                fig6 = px.bar(avg_price_by_brand, x='Brand', y='Average Price',
                                             color='Average Price',
                                             color_continuous_scale='Greys')
                                fig6.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                                st.plotly_chart(fig6, use_container_width=True)
                    
                    # Year analysis
                    if 'year' in df.columns:
                        st.markdown("**Year Analysis**")
                        df_year = df.copy()
                        df_year['year_numeric'] = pd.to_numeric(df_year['year'], errors='coerce')
                        df_year = df_year.dropna(subset=['year_numeric'])
                        
                        year_counts = df_year['year_numeric'].value_counts().sort_index().reset_index()
                        year_counts.columns = ['Year', 'Count']
                        
                        fig7 = px.line(year_counts, x='Year', y='Count', markers=True,
                                      color_discrete_sequence=['#000000'])
                        fig7.update_layout(height=400, xaxis_title="Year", yaxis_title="Number of Listings", paper_bgcolor='rgba(255,255,255,0.95)', plot_bgcolor='rgba(255,255,255,0.95)')
                        st.plotly_chart(fig7, use_container_width=True)
                else:
                    # Fallback to basic charts using streamlit native charts
                    st.warning("Plotly not installed. Install it with: pip install plotly")
                    
                    if 'brand' in df.columns:
                        st.markdown("**Top 10 Brands**")
                        top_brands = df['brand'].value_counts().head(10)
                        st.bar_chart(top_brands)
                    
                    if 'fuel_type' in df.columns:
                        st.markdown("**Fuel Type Distribution**")
                        fuel_counts = df['fuel_type'].value_counts()
                        st.bar_chart(fuel_counts)
                    
                    if 'gearbox' in df.columns:
                        st.markdown("**Gearbox Type Distribution**")
                        gearbox_counts = df['gearbox'].value_counts()
                        st.bar_chart(gearbox_counts)
                    
                    if 'year' in df.columns:
                        st.markdown("**Year Distribution**")
                        year_counts = df['year'].value_counts().sort_index()
                        st.line_chart(year_counts)
                
        else:
            st.warning("No CSV files found in the 'data/' folder")
    else:
        st.error("The 'data/' folder does not exist.")

# Option 4: Evaluation
elif menu_option == "App Evaluation":
    st.header("Evaluate Our Application")
    
    st.markdown("""
        Your feedback matters! Help us improve this application by completing an evaluation form.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("KoboToolbox")
        st.markdown("""
            Detailed form for a comprehensive evaluation of the application.
        """)
        kobotoolbox_url = "https://ee.kobotoolbox.org/x/uYmlZU5X"
        if st.button("Open KoboToolbox Form", key="kobo"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url={kobotoolbox_url}">', unsafe_allow_html=True)
            st.markdown(f'[Click here if not redirected automatically]({kobotoolbox_url})')
    
    with col2:
        st.subheader("Google Forms")
        st.markdown("""
            Quick form to share your user experience.
        """)
        google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeL5dzKVxgxD-rOZqLLiDWmIE1dPhBjeeYcrEl3_EcTGeH2zw/viewform?usp=header"
        if st.button("Open Google Forms", key="gforms"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url={google_form_url}">', unsafe_allow_html=True)
            st.markdown(f'[Click here if not redirected automatically]({google_form_url})')
    
    st.markdown("---")
    st.info("Your feedback helps us constantly improve the application. Thank you for your contribution!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #FF1493; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);'>
        <p style='font-weight: 600; letter-spacing: 1px;'>Developed with passion | 2024 Dakar Auto Scraper Premium</p>
    </div>
""", unsafe_allow_html=True)
