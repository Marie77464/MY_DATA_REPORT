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

# Custom CSS for styling with background image
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 229, 229, 0.85), rgba(255, 229, 229, 0.85)), 
                          url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1920');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .main {
        padding: 2rem;
        background-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF3333;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #00C853;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: bold;
    }
    .header-style {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader-style {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 214, 214, 0.95);
        backdrop-filter: blur(10px);
    }
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 1rem;
    }
    div[data-testid="stMetricValue"] {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 0.5rem;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="header-style">MY BEST DATA APP</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader-style">Web Scraping & Data Analysis Tool</p>', unsafe_allow_html=True)

# Description
st.markdown("""
    <div class="info-box">
    <h3>About This App</h3>
    <p>This app performs webscraping of data from <strong>dakar-auto</strong> over multiple pages. 
    You can also download pre-scraped data from the app directly without scraping them.</p>
    
    <p><strong>Python libraries:</strong> base64, pandas, streamlit, requests, bs4</p>
    
    <p><strong>Data sources:</strong></p>
    <ul>
        <li><a href="https://dakar-auto.com/senegal/voitures-4" target="_blank">Cars</a></li>
        <li><a href="https://dakar-auto.com/senegal/motos-and-scooters-3" target="_blank">Motorcycles & Scooters</a></li>
        <li><a href="https://dakar-auto.com/senegal/location-de-voitures-19" target="_blank">Car Rentals</a></li>
    </ul>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/000000/car.png", width=100)
st.sidebar.title("Menu")
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
                                         color_continuous_scale='Reds')
                            fig1.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            st.markdown("**Brand Distribution**")
                            fig2 = px.pie(top_brands, values='Count', names='Brand',
                                         color_discrete_sequence=px.colors.sequential.RdBu)
                            fig2.update_layout(height=400)
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
                                             color_continuous_scale='Oranges')
                                fig3.update_layout(height=400, showlegend=False)
                                st.plotly_chart(fig3, use_container_width=True)
                        
                        if 'gearbox' in df.columns:
                            with col2:
                                st.markdown("**Gearbox Type Distribution**")
                                gearbox_counts = df['gearbox'].value_counts().reset_index()
                                gearbox_counts.columns = ['Gearbox', 'Count']
                                fig4 = px.pie(gearbox_counts, values='Count', names='Gearbox',
                                             color_discrete_sequence=px.colors.sequential.Purples)
                                fig4.update_layout(height=400)
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
                                               color_discrete_sequence=['#FF4B4B'])
                            fig5.update_layout(height=400, xaxis_title="Price (FCFA)", yaxis_title="Count")
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
                                             color_continuous_scale='Greens')
                                fig6.update_layout(height=400, showlegend=False)
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
                                      color_discrete_sequence=['#FF4B4B'])
                        fig7.update_layout(height=400, xaxis_title="Year", yaxis_title="Number of Listings")
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
    <div style='text-align: center; color: #666;'>
        <p>Developed with love using Streamlit | 2024 Dakar Auto Scraper</p>
    </div>
""", unsafe_allow_html=True)
