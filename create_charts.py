import pandas as pd
from ridgeline import ridgeline


# Import data
df_raw = pd.read_csv('https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv', 
                 sep=';', 
                 parse_dates=['Date_of_publication'],
                 infer_datetime_format=True)
df_raw.columns= df_raw.columns.str.lower()

# Sum by province/date
df = df_raw.groupby(['date_of_publication', 'province']).sum().reset_index()

# Create ridgeline plot for daily cases
fig, ax = ridgeline(df, 
                    col_time='date_of_publication',
                    col_group='province',
                    col_value='total_reported',
                    dt_format="%b %Y",
                    title="COVID-19: Number of new daily cases in the Netherlands                      ",
                    norm='overall',
                    frac=.08,
                    scale=3,
                    note=(0.043, 0.05, "Data: RIVM"),
                    cmap='afmhot',
                    alpha=.55,
                    linspace=(0,.6))

fig.savefig('./cases.png', dpi=200)

# Create ridgeline plot for deaths
fig, ax = ridgeline(df, 
                    col_time='date_of_publication',
                    col_group='province',
                    col_value='deceased',
                    dt_format="%b %Y",
                    title="COVID-19: Number of deaths in the Netherlands             ",
                    norm='overall',
                    frac=.08,
                    scale=4,
                    note=(0.043, 0.05, "Data: RIVM"),
                    cmap='afmhot',
                    alpha=.55,
                    linspace=(0,.6))

fig.savefig('./deaths.png', dpi=200)

# Create ridgeline plot for hospital admissions
fig, ax = ridgeline(df, 
                    col_time='date_of_publication',
                    col_group='province',
                    col_value='hospital_admission',
                    dt_format="%b %Y",
                    title="COVID-19: Number of hospital admissions in the Netherlands              ",
                    norm='overall',
                    frac=.08,
                    scale=6.5,
                    note=(0.043, 0.05, "Data: RIVM"),
                    cmap='afmhot',
                    alpha=.55,
                    linspace=(0,.6))

fig.savefig('./hospitalizations.png', dpi=200)