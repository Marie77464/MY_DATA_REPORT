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

            url = f'https://dakar-auto.com/senegal/voitures-4?page={index}'
            res = get(url)
            soup = bs(res.content, 'html.parser')

            # NOUVEAU SELECTEUR QUI MARCHE !
            containers = soup.find_all('div', class_='listing-card')

            data = []
            for container in containers:
                try:
                    # TITRE
                    title = container.find('h2', class_='listing-card__title')
                    gen_inf = title.text.strip().split()

                    brand = gen_inf[0]
                    model = " ".join(gen_inf[1:len(gen_inf)-1])
                    year = gen_inf[-1]

                    # CARACTÉRISTIQUES
                    attrs = container.find('ul', class_='listing-card__attributes')
                    li = attrs.find_all('li')

                    kms_driven = li[1].text.replace("km", "") if len(li) > 1 else "N/A"
                    gearbox = li[2].text if len(li) > 2 else "N/A"
                    fuel_type = li[3].text if len(li) > 3 else "N/A"

                    # PROPRIÉTAIRE
                    owner_block = container.find('p', class_='listing-card__author')
                    owner = owner_block.text.replace("Par", "").strip() if owner_block else "N/A"

                    # PRIX (NOUVEAU SELECTEUR)
                    price_block = container.find('div', class_='listing-card__price')
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
    st.download_button("Télécharger le CSV", data=csv, file_name="annonces.csv", mime="text/csv")
