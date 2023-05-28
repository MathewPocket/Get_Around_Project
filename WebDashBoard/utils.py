import pandas as pd

#Permet d'afficher une heure formatée en fonction de deux paramètres
def affiche_delai(hour=0,minute=0):
    return f"{hour:02d}:{minute:02d}"

#Calcul d'un délais en minute
def compute_delay(hour=0,minute=0):
    return hour*60+minute

#Calcul de la perte engendrée par la mise en place d'un certain délais
def calcul_perte_by_checkin(df, delai, cout):
    #Calcul des pertes engendrées par un changement de délai
    #L'idée est de récupérer le nombre de location effectuée pour chaque voiture
    #Récupérer les lignes ou les locations se sont enchainées (previous_ended_rental_id is not null)
    #S'assurer que le délai réel d'attente est supérieure au délai paramétré
    #Compter le nombre de location qui n'aurait pas pu avoir lieu
    #Le ratio des deux nombres donne un % de perte
    #Affichage dans le tableau le % de perte avec ce délai
    
    #Compte le nombre de location qui ont eu une précédente
    df2 = df[~df['previous_ended_rental_id'].isna()].groupby(by=['checkin_type']).count().loc[:,['rental_id']].rename(columns={'rental_id':'Locations (nb)'})
    
    #On compte les locations totales pour le CA
    df2['Locations Totales'] = df.groupby(by=['checkin_type']).count().loc[:,['rental_id']]['rental_id']
    
    #Join deux fois le dataframe DF et récupère les locations qui n'auraient pu avoir lieu en fonction du delai
    merged_df = pd.merge(df[~df['previous_ended_rental_id'].isna()], df, how="left", left_on='previous_ended_rental_id',right_on='rental_id',suffixes=[None,'_prev'])
    df2['Problèmes (nb)'] = merged_df[merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']].groupby(by=['checkin_type']).count().loc[:,['rental_id']]['rental_id']
    #Nombre de locations supprimées par le délai
    df2['Locations supprimées délai (nb)'] = merged_df[merged_df['time_delta_with_previous_rental_in_minutes'] < delai].groupby(by=['checkin_type']).count().loc[:,['rental_id']]['rental_id']
    # Probleme de location actualisés
    df2['Problèmes avec délai (nb)'] = merged_df[(merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']) & (merged_df['time_delta_with_previous_rental_in_minutes'] >= delai)].groupby(by=['checkin_type']).count().loc[:,['rental_id']]['rental_id']
    #Perte CA
    df2['Perte CA (€)'] = df2['Locations supprimées délai (nb)'] * cout

    #Ajour d'une ligne de total
    df2.loc['Total']= df2.sum(numeric_only=True, axis=0)

    #Calcul ratio avant apres 
    df2.loc[:,'Ratio Pb/Total (%)'] = df2['Problèmes (nb)'] / df2['Locations (nb)'] * 100
    df2.loc[:,'Ratio Pb/Total délai (%)'] = df2['Problèmes avec délai (nb)'] / (df2['Locations (nb)'] - df2['Locations supprimées délai (nb)']) * 100
    df2.loc[:,'Ratio Perte CA (%)'] = (df2['Locations supprimées délai (nb)'] / df2['Locations Totales']) * 100

    return df2

#Calcul de la perte engendrée par la mise en place d'un certain délais
def calcul_perte_by_car(df, delai, cout):
    #Calcul des pertes engendrées par un changement de délai
    #L'idée est de récupérer le nombre de location effectuée pour chaque voiture
    #Récupérer les lignes ou les locations se sont enchainées (previous_ended_rental_id is not null)
    #S'assurer que le délai réel d'attente est supérieure au délai paramétré
    #Compter le nombre de location qui n'aurait pas pu avoir lieu
    #Le ratio des deux nombres donne un % de perte
    #Affichage dans le tableau le % de perte avec ce délai
    
    #Compte le nombre de location qui ont eu une précédente
    df2 = df[~df['previous_ended_rental_id'].isna()].groupby(by=['car_id']).count().loc[:,['rental_id']].rename(columns={'rental_id':'Locations (nb)'})
    
    #On compte les locations totales pour le CA
    df2['Locations Totales'] = df.groupby(by=['car_id']).count().loc[:,['rental_id']]['rental_id']
    
     #Join deux fois le dataframe DF et récupère les locations qui n'auraient pu avoir lieu en fonction du delai
    merged_df = pd.merge(df[~df['previous_ended_rental_id'].isna()], df, how="left", left_on='previous_ended_rental_id',right_on='rental_id',suffixes=[None,'_prev'])
    df2['Problèmes (nb)'] = merged_df[merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']].groupby(by=['car_id']).count().loc[:,['rental_id']]['rental_id']
    #Nombre de locations supprimées par le délai
    df2['Locations supprimées délai (nb)'] = merged_df[merged_df['time_delta_with_previous_rental_in_minutes'] < delai].groupby(by=['car_id']).count().loc[:,['rental_id']]['rental_id']
    # Probleme de location actualisés
    df2['Problèmes avec délai (nb)'] = merged_df[(merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']) & (merged_df['time_delta_with_previous_rental_in_minutes'] >= delai)].groupby(by=['car_id']).count().loc[:,['rental_id']]['rental_id']
    #Perte CA
    df2['Perte CA (€)'] = df2['Locations supprimées délai (nb)'] * cout

    #Calcul ratio avant apres 
    df2.loc[:,'Ratio Pb/Total (%)'] = df2['Problèmes (nb)'] / df2['Locations (nb)'] * 100
    df2.loc[:,'Ratio Pb/Total délai (%)'] = df2['Problèmes avec délai (nb)'] / (df2['Locations (nb)'] - df2['Locations supprimées délai (nb)']) * 100
    df2.loc[:,'Ratio Perte CA (%)'] = (df2['Locations supprimées délai (nb)'] / df2['Locations Totales']) * 100

    return df2.sort_values(by='Perte CA (€)',ascending=False)


#Calcul de la perte engendrée par la mise en place d'un certain délais
def calcul_perte_by_state(df, delai, cout):
    #Calcul des pertes engendrées par un changement de délai
    #L'idée est de récupérer le nombre de location effectuée pour chaque voiture
    #Récupérer les lignes ou les locations se sont enchainées (previous_ended_rental_id is not null)
    #S'assurer que le délai réel d'attente est supérieure au délai paramétré
    #Compter le nombre de location qui n'aurait pas pu avoir lieu
    #Le ratio des deux nombres donne un % de perte
    #Affichage dans le tableau le % de perte avec ce délai
    
    #Compte le nombre de location qui ont eu une précédente
    df2 = df[~df['previous_ended_rental_id'].isna()].groupby(by=['state']).count().loc[:,['rental_id']].rename(columns={'rental_id':'Locations (nb)'})
    
    #On compte les locations totales pour le CA
    df2['Locations Totales'] = df.groupby(by=['state']).count().loc[:,['rental_id']]['rental_id']
    
    #Join deux fois le dataframe DF et récupère les locations qui n'auraient pu avoir lieu en fonction du delai
    merged_df = pd.merge(df[~df['previous_ended_rental_id'].isna()], df, how="left", left_on='previous_ended_rental_id',right_on='rental_id',suffixes=[None,'_prev'])
    df2['Problèmes (nb)'] = merged_df[merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']].groupby(by=['state']).count().loc[:,['rental_id']]['rental_id']
    #Nombre de locations supprimées par le délai
    df2['Locations supprimées délai (nb)'] = merged_df[merged_df['time_delta_with_previous_rental_in_minutes'] < delai].groupby(by=['state']).count().loc[:,['rental_id']]['rental_id']
    # Probleme de location actualisés
    df2['Problèmes avec délai (nb)'] = merged_df[(merged_df['delay_at_checkout_in_minutes_prev'] >= merged_df['time_delta_with_previous_rental_in_minutes']) & (merged_df['time_delta_with_previous_rental_in_minutes'] >= delai)].groupby(by=['state']).count().loc[:,['rental_id']]['rental_id']
    #Perte CA
    df2['Perte CA (€)'] = df2['Locations supprimées délai (nb)'] * cout

    #Ajour d'une ligne de total
    df2.loc['Total']= df2.sum(numeric_only=True, axis=0)

    #Calcul ratio avant apres 
    df2.loc[:,'Ratio Pb/Total (%)'] = df2['Problèmes (nb)'] / df2['Locations (nb)'] * 100
    df2.loc[:,'Ratio Pb/Total délai (%)'] = df2['Problèmes avec délai (nb)'] / (df2['Locations (nb)'] - df2['Locations supprimées délai (nb)']) * 100
    df2.loc[:,'Ratio Perte CA (%)'] = (df2['Locations supprimées délai (nb)'] / df2['Locations Totales']) * 100

    return df2

#BLOC2 RETARD
def get_retard(df):
    #Jointure des DF
    merged_df = pd.merge(df[~df['previous_ended_rental_id'].isna()], df, how="left", left_on='previous_ended_rental_id',right_on='rental_id',suffixes=[None,'_prev'])
    #Calcul pour tous les prev en retard combien sont en retard et de combien 
    merged_df['late_to_late'] = merged_df[merged_df['delay_at_checkout_in_minutes_prev'] > 0]['delay_at_checkout_in_minutes'].apply(lambda x : 0 if x <= 0 else 1)
    
    return pd.concat([pd.DataFrame(merged_df[~merged_df['late_to_late'].isna()].groupby(by='late_to_late').count()['rental_id']),pd.DataFrame(merged_df[~merged_df['late_to_late'].isna()][['delay_at_checkout_in_minutes','late_to_late']].groupby(by='late_to_late').mean()['delay_at_checkout_in_minutes'])],axis=1)

