import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import requests
import plotly.graph_objects as go
from datetime import datetime
import dash_bootstrap_components as dbc
import pytz

# ==========================================================
# ÁREA DE CONFIGURAÇÃO
# ==========================================================
VM_IP = "127.0.0.1" 
FUSO_HORARIO_LOCAL = 'America/Sao_Paulo'
# ==========================================================

# --- CONFIGURAÇÃO DA API ORION CONTEXT BROKER ---
ORION_URL = f"http://{VM_IP}:1026/v2/entities/urn:ngsi-ld:CheckinPoint:QuadraPrincipal"
ORION_HEADERS = {
    'fiware-service': 'smart',
    'fiware-servicepath': '/'
}

# --- ARMAZENAMENTO DE HISTÓRICO EM MEMÓRIA ---
unique_players_history = {}

# --- Inicialização do App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Passa a Bola - Check-in"

# --- Layout do Dashboard (HTML) ---
app.layout = html.Div(style={'padding': '20px'}, children=[
    
    html.H1("Passa a Bola - Dashboard de Check-in em Tempo Real"),
    html.P("Este dashboard atualiza a cada 5 segundos."),
    
    html.Hr(),
    
    dbc.Row(
        [
            dbc.Col(
                [ 
                    html.H3("Quantidade de Jogadoras Únicas:"),
                    dcc.Graph(
                        id='indicator-quantity',
                        figure=go.Figure(go.Indicator(mode="number", value=0))
                    )
                ], 
                width=6
            ),
            dbc.Col(
                html.Button('Zerar Contagem de Check-ins', 
                            id='reset-button', 
                            className="mt-5", 
                            style={'fontSize': '16px'}),
                width=6,
                style={'textAlign': 'center'}
            )
        ], 
        align="start" 
    ),
    
    html.Hr(),
    
    html.H3("Jogadoras Presentes (Primeiro Check-in):"),
    dash_table.DataTable(
        id='table-players',
        columns=[
            {"name": "ID da Jogadora", "id": "playerId"},
            {"name": "Horário do Check-in", "id": "checkinTime"},
        ],
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        sort_action="native",
        page_size=10,
    ),

    dcc.Interval(
        id='interval-component',
        interval=5*1000, 
        n_intervals=0
    )
])

# --- Função de Callback (Lógica do "Tempo Real") ---
@app.callback(
    [Output('indicator-quantity', 'figure'),
     Output('table-players', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('reset-button', 'n_clicks')]
)
def update_dashboard(n_intervals, n_clicks):
    global unique_players_history

    ctx = dash.callback_context
    
    # --- CORREÇÃO DA LÓGICA DE RESET ---
    # Se o botão de reset foi o gatilho...
    if ctx.triggered and 'reset-button' in ctx.triggered[0]['prop_id']:
        # 1. Limpa o histórico local
        unique_players_history = {}
        print("--- HISTÓRICO DE CHECK-INS ZERADO ---")
        
        # 2. Deleta a entidade no FIWARE Orion
        try:
            print(f"--- Enviando DELETE para {ORION_URL} ---")
            requests.delete(ORION_URL, headers=ORION_HEADERS, timeout=3)
            print("--- Entidade no Orion deletada com sucesso ---")
        except Exception as e:
            print(f"Erro ao deletar entidade do Orion: {e}")
            
        # 3. Prepara a figura "zerada"
        fig_indicator = go.Figure(go.Indicator(mode="number", value=0))
        fig_indicator.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        
        # 4. Prepara a tabela "zerada"
        table_data = []
        
        # 5. RETORNA IMEDIATAMENTE, sem consultar o Orion
        return fig_indicator, table_data
    # --- FIM DA CORREÇÃO ---

    # Se o gatilho foi o intervalo de 5s, continua a lógica normal:
    try:
        response = requests.get(ORION_URL, headers=ORION_HEADERS, timeout=3)
        
        # Se a entidade foi encontrada (Status 200)
        if response.status_code == 200:
            data = response.json()
            
            player_id = data.get('lastPlayerId', {}).get('value', None)
            checkin_time_str = data.get('TimeInstant', {}).get('value', '')

            formatted_time = checkin_time_str
            try:
                utc_time = datetime.strptime(checkin_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                local_tz = pytz.timezone(FUSO_HORARIO_LOCAL)
                local_time = utc_time.astimezone(local_tz)
                formatted_time = local_time.strftime("%d/%m/%Y %H:%M:%S")
            except Exception as e:
                print(f"Erro ao converter timestamp: {e}")
            
            if player_id and player_id not in unique_players_history:
                unique_players_history[player_id] = formatted_time
                print(f"Nova jogadora detectada: {player_id}")
        
        # Se a entidade não foi encontrada (Status 404), não faz nada.
        # O histórico local (que está vazio) será usado.

    except Exception as e:
        print(f"Erro ao buscar dados do Orion: {e}")

    # Prepara os dados para o dashboard a partir do histórico atual
    player_quantity = len(unique_players_history)
    
    fig_indicator = go.Figure(go.Indicator(
        mode = "number",
        value = player_quantity
    ))
    fig_indicator.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    table_data = [
        {"playerId": pid, "checkinTime": time} 
        for pid, time in unique_players_history.items()
    ]
    table_data.reverse() 
    
    return fig_indicator, table_data

# --- Rodar o Servidor ---
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5000)