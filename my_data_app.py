import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get

def num_page():
    N = int(st.number_input("Combien de pages voulez-vous scraper ?", min_value=1, value=1, step=1))
    return N

st.title("Scraper annonces voitures")

M = num_page()

df = pd.DataFrame()

if st.button("Scraper"):
    with st.spinner("Scraping en cours..."):
        for index in range(1, M+1):

            # URL CORRIGÉE (page variable)
            url = f'https://dakar-auto.com/senegal/voitures-4?page={index}'

            res = get(url)
            soup = bs(res.content, 'html.parser')

            # SELECTEUR CORRIGÉ
            containers = soup.find_all('div', class_='listings-cards__list-item')

            data = []
            for container in containers:
                try:
                    # TITLE
                    title_block = container.find('h2')
                    gen_inf = title_block.text.strip().split()

                    brand = gen_inf[0]
                    model = " ".join(gen_inf[1:len(gen_inf)-1])
                    year = gen_inf[-1]

                    # ATTRIBUTES
                    gen_inf1 = container.find('ul')
                    gen_inf2 = gen_inf1.find_all('li')

                    kms_driven = gen_inf2[1].text.replace('km', '') if len(gen_inf2) > 1 else "N/A"
                    gearbox = gen_inf2[2].text if len(gen_inf2) > 2 else "N/A"
                    fuel_type = gen_inf2[3].text if len(gen_inf2) > 3 else "N/A"

                    # OWNER
                    owner_block = container.find('p')
                    owner = owner_block.text.replace("Par", "").strip() if owner_block else "N/A"

                    # PRICE
                    price_block = container.find('h3')
                    price = price_block.text.replace("FCFA", "").strip() if price_block else "N/A"

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

    st.success("Scraping terminé !")
    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button(
        "Télécharger le CSV", 
        data=csv, 
        file_name="annonces.csv", 
        mime="text/csv"
    )
