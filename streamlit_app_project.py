import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
from vega_datasets import data

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
# for map plot
###

df_ld = df_last_dose[['NAME', 'YEAR', 'DISEASE', 'COVERAGE', 'INCIDENCE_RATE']]
df_ld = df_ld.rename(columns={'NAME': 'Country'})
country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})
country_df_nw = country_df.copy()
country_df_2 = country_df_nw[['Country', 'country-code']]

for_geo = df_ld.merge(country_df_2, how='inner'
)
#for_geo = for_geo[for_geo['DISEASE'] == 'DIPHTHERIA']

source = alt.topo_feature(data.world_110m.url, 'countries')


st.header("Global Vaccine-Preventable Disease Dashboard")

width = 600
height  = 300
project = 'equirectangular'

#slider for year 
year = st.slider('Year', min_value=float(df.YEAR.min()), max_value=float(df.YEAR.max()), step=1.0, format='%d', value=2018.0)

# filter the data based on the year selected
for_geo = for_geo[for_geo['YEAR']==year]

# a gray map using as the visualization background
background = alt.Chart(source
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

######################
# P3.4 create a selector to link two map visualizations
selector = alt.selection_single(
    empty='all', fields = ['Country']
)


# select disease through dropdown
# make list of all disease used above
all_disease = for_geo['DISEASE'].unique()

disease_select_marius = st.selectbox('Select disease', all_disease)
# filter the data based on the disease selected
for_geo = for_geo[for_geo['DISEASE']==disease_select_marius]

chart_base = alt.Chart(source
    ).properties( 
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
# Rate = COVERAGE,  Population = Incidence Rate, 
        from_=alt.LookupData(for_geo, "country-code", ['COVERAGE', 'Country', 'INCIDENCE_RATE', 'YEAR']),
    )

# fix the color schema so that it will not change upon user selection
coverage_scale = alt.Scale(domain=[for_geo['COVERAGE'].min(), for_geo['COVERAGE'].max()], scheme='oranges')
coverage_color = alt.Color(field="COVERAGE:Q", type="quantitative", scale=coverage_scale)

chart_coverage = chart_base.mark_geoshape().encode(
    color=alt.Color('COVERAGE:Q', type="quantitative", scale=coverage_scale), 
    tooltip=['COVERAGE:Q', 'Country:N']  
    ######################
    # P3.1 map visualization showing the mortality rate
    # add your code here
    # ...
    ######################
    # P3.3 tooltip
    # add your code here
    # ...
    ).transform_filter(
    selector
    ).properties(
###Need to fix the year in title?
    title=f'Vaccine Coverage Worldwide {int(year)}'
)


# fix the color schema so that it will not change upon user selection
# incidence_scale = alt.Scale(domain=[for_geo['INCIDENCE_RATE'].min(), for_geo['INCIDENCE_RATE'].max()], scheme='yellowgreenblue')
incidence_scale = alt.Scale(domain=[for_geo['INCIDENCE_RATE'].min(), for_geo['INCIDENCE_RATE'].max()], scheme='yellowgreenblue')
chart_incidence = chart_base.mark_geoshape().encode(
    color=alt.Color('INCIDENCE_RATE:Q', type="quantitative", scale=incidence_scale),
    tooltip=['INCIDENCE_RATE:Q', 'Country:N'] 
    ).transform_filter(
    selector
).properties(
###Again the year?
    title=f'World Disease Incidence Rate {int(year)}'
)

chart2 = alt.vconcat(background + chart_coverage, background + chart_incidence
).resolve_scale(
    color='independent'
)

chart2



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


#subset_lastdose = df_last_admin[df_last_admin["YEAR"] == year]

#disease selector
#diseases = df.DISEASE.unique()
#disease_dropdown = alt.binding_select(options=diseases, name='Select disease:')
#disease_select = alt.selection_single(fields=['DISEASE'], bind=disease_dropdown, init={'DISEASE':'DIPHTHERIA'})



#build chart
st.write("For Polio, incidence is for 1,000,000 population *under age 15*")

comp_region_plot = comp_region[comp_region['DISEASE']==disease_select_marius]

bubble = alt.Chart(comp_region_plot[comp_region_plot.YEAR==year]).mark_circle().encode(
    x=alt.X('COVERAGE:Q', title='Vaccine coverage (% of target population)'),
    y=alt.Y('INCIDENCE_RATE:Q', title='Disease incidence per 1,000,000 population'),
    color=alt.Color('NAME:N', title='WHO Region'),
    size=alt.Size('TARGET_NUMBER:Q', title='Target population size')
#).add_selection(
  #  disease_select_marius
#).transform_filter(
  #  disease_select_marius
).properties(title='Vaccine coverage vs disease incidence by region',
             height=180,
             width=500)
#).configure_title(anchor='middle')

#bubble


##
# for butterfly bar chart
##


# make a bar chart showing the vaccine coverage for each disease in 2018 on the left and the incidence rate on the right


df_3 = df_ld.copy()
df_3 = df_3[df_3['YEAR']==year]
df_3 = df_3[df_3['DISEASE']==disease_select_marius]

#make a selection for the disease

# Filter the data to include only the counties for which we have both COVERAGE and INCIDENCE_RATE data
df_3 = df_3[df_3['COVERAGE'].notna()]
df_3 = df_3[df_3['INCIDENCE_RATE'].notna()]

# make a bar chart showing the vaccine coverage for each disease
chart3_left = alt.Chart(df_3).mark_bar(opacity=0.8).encode(
    x=alt.X('COVERAGE', scale= alt.Scale(reverse=True)),
    y=alt.Y('Country', axis = None, sort=alt.EncodingSortField(field="COVERAGE", order="descending"))
).properties(
    width=300,
    height=750
)


chart3_right = alt.Chart(df_3).mark_bar(opacity=0.8, color='red').encode(
    x=alt.X('INCIDENCE_RATE', scale= alt.Scale(reverse=False)) ,
    y=alt.Y('Country', sort=alt.EncodingSortField(field="COVERAGE", order="descending")),
).properties(
    width=300,
    height=750
)

chart3 = alt.hconcat(chart3_left, chart3_right).properties(
    title=f'Vaccine Coverage and Disease Incidence Rate in {int(year)}'
).resolve_scale(
    y = 'shared'
)

chart3

# end of butterfly bar chart

##
# Illustrate change in vaccination coverage and disease incidence over time using a line chart
##



df_5 = df_ld.copy()
# for each year and disease, get the mean coverage and incidence rate
df_5 = df_5.groupby(['YEAR', 'DISEASE']).mean().reset_index()

disease_selection_3 = alt.selection_single(
    fields=['DISEASE'], bind = "legend"
)


# make an altair chart with the Year on the x-axis and the COVERAGE on the y-axis with different colors for each disease

chart5_1 = alt.Chart(df_5).mark_line().encode(
    x= alt.X('YEAR', title='Year', scale=alt.Scale(domain=(1980, 2021))),
    y='COVERAGE',
    color='DISEASE'
).add_selection(
    disease_selection_3
).transform_filter(
    disease_selection_3
).properties(
    title='Vaccine Coverage Over Time',
    width=700,
    height=350
)
# make another chart that shows the INCIDENCE_RATE over time
chart5_2 = alt.Chart(df_5).mark_line().encode(
    x= alt.X('YEAR', title='Year', scale=alt.Scale(domain=(1980, 2021))),
    y='INCIDENCE_RATE',
    color='DISEASE'
).transform_filter(
    disease_selection_3
).properties(
    title='Disease Incidence Rate Over Time',
    width=700,
    height=350
)


# combine the two charts into one chart showing one chart above the other
chart5 = alt.vconcat(chart5_1, chart5_2)
chart5


# end of line chart




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
regions = df[df.GROUP=='WHO_REGIONS'].NAME.unique()
region_dropdown = alt.binding_select(options=regions, name='Select region:')
region_select = alt.selection_single(fields=['NAME'], bind=region_dropdown, init={'NAME':'African Region'})

#country selector
countries = df[df.GROUP=='COUNTRIES'].NAME.unique()
country_dropdown = alt.binding_select(options=countries, name='Select country to view doses over time:')
country_select = alt.selection_single(fields=['NAME'], bind=country_dropdown, init={'NAME':'Aruba'})

df_plotbar = df[df.DISEASE==disease_select_marius]

dose_stacked = alt.Chart(df_plotbar[(df_plotbar.dose_num.notna()) & (df_plotbar.dose_num!='nan')]).mark_bar(size=8).encode(
    x=alt.X('YEAR', axis=alt.Axis(format=".0f")),
    y=alt.Y('COVERAGE:Q', title='Coverage (%)'),
    color=alt.Color('dose_num:N', title='Dose #', sort='descending'),
    order=alt.Order('dose_num:N', sort='descending')
).properties(title='Vaccine coverage by dose number over time',
             width=500,
             height=75
#).configure_title(anchor='middle'
#).add_selection(
 #   disease_select
#).transform_filter(
 #   disease_select
).add_selection(
    country_select
).transform_filter(
    country_select)

#dose_stacked

chart1 = alt.vconcat(bubble, dose_stacked
).resolve_scale(
    color='independent'
)
chart1

#print('NaN count:', df[df.dose_num.isna()].shape)
#print('String nan count: ', df[df.dose_num=='nan'].shape)






### Filtering the vaccine dataframe for only the development status group ###

dev_status = vax[vax.GROUP=='DEVELOPMENT_STATUS']

### creating the vaccine list for the development status vaccine coverage plot ###
vxlst = ['BCG', 'DTPCV3', 'HEPB3', 'HIB3', 'MCV2', 'PCV3', 'POL3', 'RCV1', 'ROTAC', 'YFV']
dev_stat_short = dev_status[dev_status['ANTIGEN'].isin(vxlst)]

### Naming the extra vaccines ###

DTP_words = '|'.join(['DTP']) 
HepB_words = '|'.join(['HepB'])
BCG_words = '|'.join(['BCG'])
Hib_words = '|'.join(['Hib'])
Rotavirus_words = '|'.join(['Rotavirus'])
Pneumococcal_words = '|'.join(['Pneumococcal'])

dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(DTP_words), 'DISEASE'] = 'DIPHTHERIA,TETANUS,PERTUSSIS'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(HepB_words), 'DISEASE'] = 'HEPATITIS B'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(BCG_words), 'DISEASE'] = 'TUBERCULOSIS'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(Hib_words), 'DISEASE'] = 'HAEMOPHILUS INFLUENZAE'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(Rotavirus_words), 'DISEASE'] = 'ROTAVIRUS'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(yellowfever_words), 'DISEASE'] = 'YELLOW FEVER'
dev_stat_short.loc[dev_stat_short.ANTIGEN_DESCRIPTION.str.contains(Pneumococcal_words), 'DISEASE'] = 'PNEUMOCOCCUS'


### Vaccine coverage by development status plot ###

title = alt.TitleParams('Vaccine Coverage by Development Status', anchor='middle', fontSize=18)
ds_plot = alt.Chart(dev_stat_short, title = title).mark_bar().encode(
    x=alt.X('NAME:O', title=' '),
    y=alt.Y('COVERAGE:Q', axis=alt.Axis(title='Vaccine Coverage')), 
            # scale=alt.Scale(domain=[25, 100], clamp=True)), #
    color='NAME:N',
    facet=alt.Facet('DISEASE:N', title= ' ', columns=5, spacing = 0, align = 'each'),
).properties(
    width=100,
    height=100
)

#   , color='red'  

# plot4 # Render it!
ds_plot
