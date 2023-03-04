import altair as alt
import pandas as pd
import streamlit as st
import numpy as np

### Import data ###

###Trying by uploading the data files to github

#url = "https://raw.githubusercontent.com/emanuelemassaro/pois/master/indonesia_education.csv"

url_vax = "https://raw.githubusercontent.com/smkisvarday/InsightSquad/master/coverage--2021.csv"
url_dis = "https://raw.githubusercontent.com/smkisvarday/InsightSquad/master/incidence-rate--2021.csv"


vax = pd.read_csv(url_vax)
dis = pd.read_csv(url_dis)

print(vax)
print(dis)


#drop the mostly-nan row from both datasets
dis.dropna(thresh=7, inplace=True, axis=0)
vax.dropna(thresh=9, inplace=True, axis=0)


#add an a DISEASE column to the vax dataset, to match the ANTIGEN_DESCRIPTION column in dis dataset

#create empty column
vax['DISEASE'] = np.NaN

diphtheria_words = '|'.join(['Diphtheria', 'DTP']) 
measles_words = '|'.join(['Measles'])
tetanus_words = '|'.join(['Tetanus'])
mumps_words = []
pertussis_words = '|'.join(['Pertussis'])
polio_words = '|'.join(['Polio', 'polio', 'IPV'])
rubella_words = '|'.join(['Rubella'])
yellowfever_words = '|'.join(['Yellow fever'])
jenceph_words = '|'.join(['Japanese encephalitis'])

#populate with diseases matching antigen description, for diseases in the dis dataset 
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(diphtheria_words), 'DISEASE'] = 'DIPHTHERIA'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(measles_words), 'DISEASE'] = 'MEASLES'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(tetanus_words), 'DISEASE'] = 'TTETANUS'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(pertussis_words), 'DISEASE'] = 'PERTUSSIS'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(polio_words), 'DISEASE'] = 'POLIO'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(rubella_words), 'DISEASE'] = 'RUBELLA'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(yellowfever_words), 'DISEASE'] = 'YFEVER'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(jenceph_words), 'DISEASE'] = 'JAPENC'


#crete list of diseases in both vax and dis
common_diseases = vax.loc[vax.DISEASE.notna(), 'DISEASE'].unique()

#limit both datasets to just illnesses common to both, then merge on DISEASE
vax_lim = vax[vax.DISEASE.isin(common_diseases)]
dis_lim = dis[dis.DISEASE.isin(common_diseases)]
df = pd.merge(vax_lim, dis_lim, on=['GROUP', 'CODE', 'NAME', 'YEAR', 'DISEASE'], how='left')

#Selecting just the rows for the final dose vaccines:
WHO_completed_series = ['DIPHCV5', 'POL3', 'MCV2', 'DTPCV3',  'RCV1', 'TT2PLUS', 'YFV', 'JAPENC']
df_last_dose = df[df['ANTIGEN'].isin(WHO_completed_series)]


###
# for bubble plot
####
#limit to admin data, which has target #, coverage and incidence
df_last_admin = df_last_dose[df_last_dose.COVERAGE_CATEGORY!='OFFICIAL']

#create df grouped by region, for those w last dose of serires
comp_region = df_last_admin[df_last_admin.GROUP=='WHO_REGIONS']


#####
# create bubble plot
####

#slider for year 
year = st.slider('Year', min_value=float(df.YEAR.min()), max_value=float(df.YEAR.max()), step=1.0, format='%d')

#subset_lastdose = df_last_admin[df_last_admin["YEAR"] == year]

#disease selector
diseases = df.DISEASE.unique()
disease_dropdown = alt.binding_select(options=diseases, name='Select disease:')
disease_select = alt.selection_single(fields=['DISEASE'], bind=disease_dropdown, init={'DISEASE':'DIPHTHERIA'})

st.write("For Polio, incidence is for 1,000,000 population *under age 15*")

#build chart
bubble = alt.Chart(comp_region[comp_region.YEAR==year]).mark_circle().encode(
    x=alt.X('COVERAGE:Q', title='Vaccine coverage (% of target population)'),
    y=alt.Y('INCIDENCE_RATE:Q', title='Disease incidence per 1,000,000 population'),
    color=alt.Color('NAME:N', title='WHO Region'),
    size=alt.Size('TARGET_NUMBER:Q', title='Target population size')
).add_selection(
    disease_select
).transform_filter(
    disease_select
).properties(title='Vaccine coverage vs disease incidence by region',
             height=450,
             width=600)
#).configure_title(anchor='middle')

#bubble



####
# for stacked dose bar chart
####

#add dose number column
                #diphtheria
df['dose_num'] = np.where(df.ANTIGEN=='DTPCV1', 1,
                 np.where(df.ANTIGEN=='DTPCV3', 3,
                 np.where(df.ANTIGEN=='DIPHCV4', 4,
                 np.where(df.ANTIGEN=='DIPHCV5', 'final', 
                
                #polio
                 np.where(df.ANTIGEN=='IPV1', 1,
                 np.where(df.ANTIGEN=='IPV2', 2,
                 np.where(df.ANTIGEN=='POL3', 'final',
                
                 #measles
                 np.where(df.ANTIGEN=='MCV1', 1,
                 np.where(df.ANTIGEN=='MCV2', 'final', 

                #pertussis
                 #np.where((df.ANTIGEN=='DTPCV1') & (df.DISEASE_2=='PERTUSSIS'), 1,
                 #np.where((df.ANTIGEN=='DTPCV3') & (df.DISEASE_2=='PERTUSSIS'), 'final',
                 np.where(df.ANTIGEN=='PERCV4', 'final',
                 np.where(df.ANTIGEN=='PERCV_PW', 'booster',

                #rubella
                np.where(df.ANTIGEN=='RCV1', 'final',

                 #tetanus
                 np.where(df.ANTIGEN=='TT2PLUS', 'final',
                 np.where(df.ANTIGEN=='TTCV4','booster',
                 np.where(df.ANTIGEN=='TTCV5','booster',
                 np.where(df.ANTIGEN=='TTCV6','booster', 

                #yellow fever
                np.where(df.ANTIGEN=='YFV', 'final',

                #japanese encephalitis
                np.where(df.ANTIGEN=='JAPENC', 'final',
                 np.where(df.ANTIGEN=='JAPENC_1', 'final', np.NaN)))))))))))))))))))


# Bar chart for doses

# Bar chart for doses
#region selector
#regions = df[df.GROUP=='WHO_REGIONS'].NAME.unique()
#region_dropdown = alt.binding_select(options=regions, name='Select region:')
#region_select = alt.selection_single(fields=['NAME'], bind=region_dropdown, init={'NAME':'African Region'})

#country selector
countries = df[df.GROUP=='COUNTRIES'].NAME.unique()
country_dropdown = alt.binding_select(options=countries, name='Select country:')
country_select = alt.selection_single(fields=['NAME'], bind=country_dropdown, init={'NAME':'Aruba'})


dose_stacked = alt.Chart(df[df.dose_num.notna()]).mark_bar(size=6).encode(
    x=alt.X('YEAR', axis=alt.Axis(format=".0f")),
    y=alt.Y('COVERAGE:Q', title='Vaccine coverage (% target population)'),
    color=alt.Color('dose_num:N', title='Dose #', sort='descending'),
    order=alt.Order('dose_num:N', sort='descending')
).properties(title='Vaccine coverage by dose number over time',
             width=450,
             height=600
#).configure_title(anchor='middle'
).add_selection(
    disease_select
).transform_filter(
    disease_select
).add_selection(
    country_select
).transform_filter(
    country_select)

#dose_stacked

chart1 = bubble & dose_stacked
chart1