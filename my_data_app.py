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
        # loop over pages indexes
        for index in range(1, M+1):
            url = 'https://dakar-auto.com/senegal/voitures-4'
            # get the html code of the page using the get function requests
            res = get(url)
            res
            # store the html code dans un objet BeautifulSoup avec html parser
            soup = bs(res.content, 'html.parser')
            # get all containers that contains the informations of each car
            containers = soup.find_all('div', class_='listings-cards__list-item mb-md-3 mb-3')
            # scrape data from all the containers
            data = []
            for container in containers:
                try:
                    gen_inf = container.find('h2', class_='listing-card__header__title mb-md-2 mb-0').a.text.strip().split()
                    # get the brand
                    brand = gen_inf[0]
                    # get the model
                    model = " ".join(gen_inf[1:len(gen_inf)-1])
                    # get the year
                    year = gen_inf[-1]
                    # Scrape the kilometer, fuel type and gearbox type
                    gen_inf1 = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    gen_inf2 = gen_inf1.find_all('li', 'listing-card__attribute list-inline-item')
                    # get kilometer driven
                    kms_driven = gen_inf2[1].text.replace('km', '')
                    # get the gearbox
                    gearbox = gen_inf2[2].text
                    # get fuel type
                    fuel_type = gen_inf2[3].text
                    # scrape owner
                    owner = "".join(container.find('p', class_='time-author m-0').a.text).replace('Par', '')
                    # scrape the price
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

    st.success("Scraping terminé !")
    st.dataframe(df)

    # Optionnel : proposer de télécharger le résultat en CSV
    csv = df.to_csv(index=False)
    st.download_button("Télécharger le CSV", data=csv, file_name="annonces.csv", mime="text/csv")
