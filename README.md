Simple PCA on Dutch mortality data. Self explanatory python script to process:

1) Eurostat weekly mortality in 5-year age groups. https://ec.europa.eu/eurostat/databrowser/view/demo_r_mwk2_05__custom_10531046/settings_1/line?lang=en
2) To correct for age group size, CBS population data: Download one csv for each year. https://www.cbs.nl/nl-nl/visualisaties/dashboard-bevolking/bevolkingspiramide

cbsparse.awk parses the csv files from CBS into one singe file

pca.py imports eurostat mortality data and population size data and performs the analysis

