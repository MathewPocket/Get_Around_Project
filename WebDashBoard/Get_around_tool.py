import streamlit as st
import pandas as pd
import plotly.express as px
from utils import *
### CONFIG
st.set_page_config(
    page_title="app",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

### TITLE AND TEXT
st.title("📈 Get Around Tool")

st.divider()
st.markdown("""
### Bienvenue sur ce dashboard d'aide à l'analyse des délais.
""")

#PARTIE SELECTEUR
st.divider()
st.header("Sélecteur de délais")
colA, colB,colC = st.columns([4,2,4])
with colA:
    hour_val = st.slider('Sélectionner un nombre d''heures de délais', min_value=0, max_value=12, value=1, step=1,  on_change=None)
    min_val = st.slider('Sélectionner un nombre de minutes de délais', min_value=0, max_value=59, value=0, step=1,  on_change=None)
with colB:
    st.text("Délai d'analyse choisi :")
    st.header(affiche_delai(hour_val,min_val))
    #Centrage Vertical de l'heure affichée
    st.write(
    """<style>
    [data-testid="stHorizontalBlock"] {
        align-items: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
#Calcul du délai en minute
delay_min = compute_delay(hour_val,min_val)

#PARTIE SELECTEUR
st.divider()
st.header("Coût moyen de la location")
mean_loc_cost = int(st.text_input(
        "Indiquer le coût moyen d'une location",
        121,#Obtenu via la moyenne des prix à la location du fichier de data
        key="placeholder"
    ))
st.text("Montant obtenu en faisant la moyenne des prix à la location pour une journée du fichier data.")

#CHARGEMENT DES DATAS
df = pd.read_excel("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx")

#EDA
#Beaucoup de lignes delay_at_checkout_in_minutes sont vides, nous les remplaçons par des 0
df['delay_at_checkout_in_minutes'].fillna(0,inplace=True)

#Partie ANALYSE BLOC1
st.divider()

#Calcul des pertes engendrées par un changement de délai
#L'idée est de récupérer le nombre de location effectuée pour chaque voiture
#Récupérer les lignes ou les locations se sont enchainées (previous_ended_rental_id is not null)
#S'assurer que le délai réel d'attente est supérieure au délai paramétré
#Compter le nombre de location qui n'aurait pas pu avoir lieu
#Le ratio des deux nombres donne un % de perte
#Affichage dans le tableau le % de perte avec ce délai
st.header("Perte de location en % en fonction du délai")
st.text("Description par type de reservation du nombre de location dans le scope initiale (ayant une location précédente) et le nombre de location posant problème.")
st.text("En modifiant les curseurs de délai, on fait disparaitre un certain nombre de location qui n'auraient pas pu avoir lieu, et donc un nombre de location à problème.")
st.text("En jouant avec la feature de délais, nous avons un apercu du % de perte de location. En se basant sur le prix moyen d'une location (modifiable) on estime la perte de CA.")
df_ratio = calcul_perte_by_checkin(df, delay_min, mean_loc_cost)
colA, colB = st.columns([5,5])
with colA:
    affiche_detail = st.checkbox('Afficher le détail',key = 'chkbox1')
    if affiche_detail:
        st.dataframe(data=df_ratio.style.format({'Ratio Pb/Total (%)':'{:.2f}%' , 'Ratio Pb/Total délai (%)':'{:.2f}%'},precision=2))
    else:
        st.dataframe(data=df_ratio[['Ratio Pb/Total (%)','Ratio Pb/Total délai (%)','Ratio Perte CA (%)']].style.format({'Ratio Pb/Total (%)':'{:.2f}%' , 'Ratio Pb/Total délai (%)':'{:.2f}%'},precision=2))
with colB:
    fig = px.histogram(df_ratio[df_ratio.index != 'Total'].reset_index(), x='checkin_type', y='Ratio Pb/Total (%)',histfunc='avg')
    st.plotly_chart(fig, theme=None, use_container_width=True)

st.header("Détail par voiture")
df_ratio = calcul_perte_by_car(df, delay_min, mean_loc_cost)
colA, colB = st.columns([5,5])
with colA:
    st.dataframe(data=df_ratio.reset_index().style.format({'Ratio Pb/Total (%)':'{:.2f}%' , 'Ratio Pb/Total délai (%)':'{:.2f}%'},precision=2) )
with colB:
    fig = px.histogram(df_ratio, x='Locations (nb)', y='Perte CA (€)',histfunc='avg')
    st.plotly_chart(fig, theme=None, use_container_width=True)
    fig = px.histogram(df_ratio, x='Locations (nb)', y='Perte CA (€)',histfunc='sum')
    st.plotly_chart(fig, theme=None, use_container_width=True)

#Vérification des statuts canceled
st.header("Nombre de locations annulées")
df_ratio = calcul_perte_by_state(df, delay_min, mean_loc_cost)
colA, colB = st.columns([5,5])
with colA:
    affiche_detail_canceled = st.checkbox('Afficher le détail',key = 'chkbox2')
    if affiche_detail_canceled:
        st.dataframe(data=df_ratio.style.format({'Ratio Pb/Total (%)':'{:.2f}%' , 'Ratio Pb/Total délai (%)':'{:.2f}%'},precision=2))
    else:
        st.dataframe(data=df_ratio[['Ratio Pb/Total (%)','Ratio Pb/Total délai (%)','Ratio Perte CA (%)']].style.format({'Ratio Pb/Total (%)':'{:.2f}%' , 'Ratio Pb/Total délai (%)':'{:.2f}%'},precision=2))
with colB:
    fig = px.histogram(df_ratio[df_ratio.index != 'Total'].reset_index(), x='state', y='Problèmes avec délai (nb)',histfunc='sum')
    st.plotly_chart(fig, theme=None, use_container_width=True)

st.header("Conclusion")
st.text("On peut voir que la part des locations connect est supérieure quand il y a une location dans les -12h.\n\
Pour les cas ou les locations s'enchainent, il a 13% de cas problématiques actuellement. En modifiant le délai mini entre deux locations\n\
1H de délais entre deux locations descend le ratio à 5% de problèmes soit plus de moitié moins. En revanche, à scénario identique cela ferait perdre quasiment de 2% du chiffre d'affaire.\n\
L'analyse par voiture nous permet de voir que les plus gros loueurs de leur voiture (plus de 12 fois sur la période) seraient le plus impactés par la perte. Perdant jusqu'à 20% du CA.\n\
En revanche en terme de nombre, la perte de CA est maximum sur les petits nombre de location.\n\
Enfin, nous voyons que 20% des locations problématiques sont en status annulées. En passant le délai d'attente à 1H il n'en reste que la moitié.\n\
")

#Trace graphique Récap
df_recap = pd.DataFrame(columns=['Délai','CA','AvgLossCar','NB_PB'])
temp_dict = dict()
for i in range(0,12):
    df_checkin = calcul_perte_by_checkin(df, i*60, mean_loc_cost)
    df_car = calcul_perte_by_car(df, i*60, mean_loc_cost)
    temp_dict = {'Délai':i,
                 'CA': (df_checkin.loc[['Total'],['Locations (nb)']].values[0][0] - df_checkin.loc[['Total'],['Locations supprimées délai (nb)']].values[0][0]) * mean_loc_cost / 184100,
                 'AvgLossCar':df_car['Perte CA (€)'].mean() / 158.032129,
                 'NB_PB': df_checkin.loc[['Total'],['Problèmes avec délai (nb)']].values[0][0] / 241.0
    }
    df_recap = pd.concat([df_recap,pd.DataFrame.from_records([temp_dict])])

#Normalisation
df_recap['CA'] = df_recap['CA'] / df_recap['CA'].max()
df_recap['AvgLossCar'] = df_recap['AvgLossCar'] / df_recap['AvgLossCar'].max()
df_recap['NB_PB'] = df_recap['NB_PB'] / df_recap['NB_PB'].max()
df_recap['AvgLossCar'] = df_recap['AvgLossCar'].fillna(0)

fig = px.line(df_recap, x="Délai", y="CA")
fig.add_scatter(x=df_recap['Délai'], y=df_recap['AvgLossCar'],name='Perte Moyenne par voiture')
fig.add_scatter(x=df_recap['Délai'], y=df_recap['NB_PB'], name='Nombre de problèmes supprimés')
st.plotly_chart(fig, theme=None, use_container_width=True)

st.text("Le délai aux alentours de 2H règle 80% des problèmes pour 40% du CA, au dela, la perte de CA est trop importante")

#Partie ANALYSE BLOC2 Retard
st.divider()
st.header("Analyse des retards")
colA,colB,colC,colD = st.columns([25,25,25,25])

#NB loc avec suite vs nb loc sans suite
#NB personne en retard / en avance 
#Retard moyen par voiture 
#Retard moyen par checkin_type

with colA:
    fig = px.pie(df, values=[df[~df['previous_ended_rental_id'].isna()].count()['rental_id'],df[df['previous_ended_rental_id'].isna()].count()['rental_id']], names=['Avec location précédente','Sans location précédente ou >12h'], title='')
    
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    st.plotly_chart(fig, theme=None, use_container_width=True)
with colB:
    fig = px.pie(df, values=[df[df['delay_at_checkout_in_minutes'] < 0 ].count()['rental_id'],df[df['delay_at_checkout_in_minutes'] > 0 ].count()['rental_id'],df[df['delay_at_checkout_in_minutes'] == 0 ].count()['rental_id']], names=['En avance','En retard','On time'], title='')
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    st.plotly_chart(fig, theme=None, use_container_width=True)
with colC:
    fig = px.bar( x=['Avance moyenne (min)','Retard moyen (min)'],y=[abs(df[df['delay_at_checkout_in_minutes'] < 0 ]['delay_at_checkout_in_minutes'].mean()),df[df['delay_at_checkout_in_minutes'] > 0 ]['delay_at_checkout_in_minutes'].mean()])
    st.plotly_chart(fig, theme=None, use_container_width=True)


st.header("Influence des retards")
df_ret = get_retard(df)
st.dataframe(df_ret)
st.text("En sélectionnant toutes les lignes dont la location précédente a éété rendue en retard, en comptand le nombre de retour de la location suivante, on s'appercoit que le nombre de personne en retard (ligne '1') est quasiement égale au nombre de personne en avance (ligne '0'). Les locataires ne se vengent pas.")

st.divider()
st.header("Conclusion Générale")
st.text("Délai de 2H")
st.text("Peu de location de la voiture")
st.text("Surtout sur les mobiles")


