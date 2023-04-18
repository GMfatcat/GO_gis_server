import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, Output

# 生成隨機的 5x5 Numpy 陣列
np.random.seed(0)
# init_data = np.random.rand(30, 20)
init_data = np.random.randint(100,size = (30, 20))

# 建立 Dash 應用程式
app = Dash(__name__)

# 定義下拉選單選項
# color in plotly:https://plotly.com/python/builtin-colorscales/
colorscale_options = [
{'label': 'Viridis', 'value': 'Viridis'},
{'label': 'Cividis', 'value': 'Cividis'},
{'label': 'Jet', 'value': 'Jet'},
{'label': 'Hot', 'value': 'Hot'},
{'label': 'Inferno', 'value': 'Inferno'}
]

# 設定 Dash 應用程式的介面
app.layout = html.Div([
    html.H1('Real Time Signal Dense Grid',style={'margin-left': '25px'}),
    html.Label('Colormap: ',style={'margin-left': '25px'}),
    html.Div([
    # tool panel(color)
    dcc.Dropdown(
        id='colorscale-dropdown',
        options=colorscale_options,
        value='Viridis',
        style={'margin-left': '10px','width': '200px'}
        ),
    html.Button('Generate Random Array',
                id='generate-button',
                n_clicks=0,
                style={'margin-left': '20px'}
                ),
    html.Button('Full Page Screenshot',
                id='generate-full-page-screenshot',
                n_clicks=0,
                style={'margin-left': '20px'}
                )],style={'display': 'flex', 'flex-direction': 'row'}),
    # heatmap and guage
    html.Div([
        dcc.Graph(
            id='grid-graph'
            ),
        dcc.Graph(
            id='grid-graph2'
            ),
        html.Div([
            dcc.Graph(id='gauge-chart1',style={'height': '300px', 'width': '470px'}),
            dcc.Graph(id='gauge-chart2', style={'height': '300px', 'width': '470px'})
            ],style={'display': 'flex', 'flex-direction': 'column'})],
        style={'display': 'flex', 'flex-direction': 'row'}),
    dcc.Interval(
        id='interval-component',
        interval=10000,  # 設定觸發間隔為10秒
        n_intervals=0  # 起始時點的 n_intervals 值
    )
    ])

# TODO: function of making and saving full page screenshot
def get_screenshot():
    pass

def get_guage(key_value,fig_title,max_range):
    # 創建一個 Gauge Chart
    fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = key_value,  # 指標的值
    title = {'text': fig_title},
    gauge = {
        'axis': {'range': [None, max_range]},  # 指標範圍
        'steps': [
            {'range': [0, max_range//2], 'color': "lightgray"},  # 指標顏色
            {'range': [max_range//2, max_range], 'color': "gray"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},  # 閾值線的顏色和寬度
            'thickness': 0.75,  # 閾值線的粗細
            'value': max_range*0.9  # 危險閾值
        }
    }))
    return fig

def get_current_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

# TODO: make the x y axis number same to the longitude and latitude
def show_grid(data,colorscale):
    # get current time
    current_time = get_current_time()
    # sum fig
    sum_fig = px.imshow(data,
        color_continuous_scale = colorscale,
        labels=dict(x="Longitude", y="Latitude", color="Total"),
        title = f"Signal Total Count {current_time}")
    sum_fig.layout.height = 550
    sum_fig.layout.width = 550
    sum_fig.update_layout(title_x=0.5,title_y=0.88)

    # density fig (signal / 4 km²) --> each grid is 2 km width and height
    density_data = data / 4
    density_fig = px.imshow(density_data,
        color_continuous_scale = colorscale,
        labels=dict(x="Longitude", y="Latitude", color="Density"),
        title = f"Signal Density {current_time}")
    density_fig.layout.height = 550
    density_fig.layout.width = 550
    density_fig.update_layout(title_x=0.5,title_y=0.88)
    # guage
    sum_guage_fig = get_guage(np.sum(data),"Total Signal",max_range = 45000)
    max_guage_fig = get_guage(data.max(), "Max Signal in Grid",max_range = 120)
    # return
    return sum_fig,density_fig,sum_guage_fig,max_guage_fig

# 合併兩個回呼為一個回呼
@app.callback(
    [Output('grid-graph', 'figure'),
     Output('grid-graph2', 'figure'),
     Output('gauge-chart1', 'figure'),
     Output('gauge-chart2', 'figure')],
    [Input('colorscale-dropdown', 'value')],
    [Input('generate-button', 'n_clicks')],
    [Input('interval-component', 'n_intervals')]
)
def update_figures(colorscale, n_clicks, n_intervals):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'generate-button' and n_clicks is not None and n_clicks > 0:
        # 手動更新
        data = np.random.randint(100, size=(30, 20))
    elif triggered_id == 'interval-component' and n_intervals is not None and n_intervals > 0:
        # 定時更新
        data = np.random.randint(100, size=(30, 20))
    else:
        # 初始資料
        data = init_data

    sum_fig,density_fig,guage_fig1,guage_fig2 = show_grid(data, colorscale)
    return sum_fig, density_fig,guage_fig1,guage_fig2


# 啟動 Dash 應用程式
if __name__ == '__main__':
    app.run_server(debug=True)
