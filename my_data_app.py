import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import glob
import plotly.express as px

# === LE RESTE DU CODE QUE JE T'AI DONNÉ HIER (à partir de st.set_page_config) ===
st.set_page_config(page_title="Dakar Auto Scraper", page_icon="car", layout="wide")

# === CSS (le même que je t'ai envoyé) ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    * {font-family: 'Montserrat', sans-serif;}
    
    .stApp {
        background-image: url('https://images.pexels.com/photos/6891809/pexels-photo-6891809.jpeg?auto=compress&cs=tinysrgb&w=1920');
        background-size: cover;
        background-attachment: fixed;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2d3436, #636e72);
    }
    [data-testid="stSidebar"] * {color: white !important;}

    .main-section {
        background: rgba(52, 73, 94, 0.92);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
    }
    .main-section h1, .main-section h2 {color: #f1c40f !important;}

    .sub-section {
        background: rgba(236, 240, 245, 0.97);
        padding: 1.8rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid #3498db;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .sub-section h3, .sub-section p {color: #2c3e50 !important;}

    .stButton>button {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 700;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2980b9, #1abc9c);
        transform: translateY(-3px);
    }

    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
