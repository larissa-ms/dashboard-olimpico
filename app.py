import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

url = 'https://drive.google.com/uc?id=1vqWxGovNQFvauUn9_leTyTyEW80kagr6'
df = pd.read_csv(url)

df['Country_Name'] = df['Country_Name'].replace('United States', 'United States of America')
df = df[(df['Year'] >= 1992) & (df['Year'] <= 2020)]
df['Total_Medals'] = df['Gold'] + df['Silver'] + df['Bronze']

app = dash.Dash(__name__)
app.title = "Dashboard Olímpico"

app.layout = html.Div([
    html.H1("🏅 Dashboard Olímpico - Medalhas de Verão (1992–2020)", style={
        'textAlign': 'center',
        'marginBottom': '30px'
    }),

    html.Div([
        html.Div([
            html.Label("Tipo de Medalha:"),
            dcc.Dropdown(
                id='medal-type',
                options=[
                    {'label': 'Todos', 'value': 'Total_Medals'},
                    {'label': 'Ouro', 'value': 'Gold'},
                    {'label': 'Prata', 'value': 'Silver'},
                    {'label': 'Bronze', 'value': 'Bronze'}
                ],
                value='Total_Medals',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}),

        html.Div([
            html.Label("Ano Olímpico:"),
            dcc.Dropdown(
                id='year-select',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                value=None,
                placeholder='Selecione o ano',
                clearable=True
            )
        ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}),

        html.Div([
            html.Label("País (pizza):"),
            dcc.Dropdown(
                id='country-select',
                options=[{'label': c, 'value': c} for c in sorted(df['Country_Name'].unique())],
                value='United States of America',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'marginBottom': '40px', 'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='map-chart')
    ], style={'marginBottom': '50px'}),

    html.Div([
        html.Div([dcc.Graph(id='area-chart')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([dcc.Graph(id='bar-chart')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='pie-chart')
    ], style={'marginTop': '50px'})
])

@app.callback(
    Output('map-chart', 'figure'),
    Output('area-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('medal-type', 'value'),
    Input('year-select', 'value'),
    Input('country-select', 'value')
)
def update_graphs(medal_type, selected_year, selected_country):
    df_filtered = df.copy()
    color_col = medal_type

    if medal_type != 'Total_Medals':
        df_filtered = df_filtered[df_filtered[medal_type] > 0]

    df_map = df_filtered.groupby('Country_Name')[color_col].sum().reset_index()
    map_fig = px.choropleth(
        df_map, locations='Country_Name', locationmode='country names',
        color=color_col, color_continuous_scale='YlOrRd',
        title=f'Total de Medalhas por País ({medal_type})'
    )

    df_area = df_filtered.groupby(['Year', 'Country_Name'])[color_col].sum().reset_index()
    top_10 = df_area.groupby('Country_Name')[color_col].sum().nlargest(10).index
    df_area_top = df_area[df_area['Country_Name'].isin(top_10)]
    area_fig = px.area(df_area_top, x='Year', y=color_col, color='Country_Name',
                       title=f'Top 10 Países por Medalhas ({medal_type})')

    df_bar = df_filtered[df_filtered['Year'] == selected_year] if selected_year else df_filtered
    df_bar = df_bar.groupby('Country_Name')[color_col].sum().nlargest(10).reset_index()
    bar_color = {'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'}.get(medal_type, 'blue')
    bar_fig = px.bar(df_bar, x='Country_Name', y=color_col,
                     title=f'Top 10 Países no Ano {selected_year if selected_year else "Todos"} - {medal_type}',
                     color_discrete_sequence=[bar_color])

    df_pie = df[df['Country_Name'] == selected_country].groupby('Country_Name')[['Gold', 'Silver', 'Bronze']].sum().reset_index()
    df_pie = df_pie.melt(id_vars='Country_Name', value_vars=['Gold', 'Silver', 'Bronze'],
                         var_name='Medalha', value_name='Quantidade')
    pie_fig = px.pie(df_pie, names='Medalha', values='Quantidade',
                     title=f'Distribuição de Medalhas - {selected_country}')

    return map_fig, area_fig, bar_fig, pie_fig

if __name__ == '__main__':
    app.run(debug=True)
