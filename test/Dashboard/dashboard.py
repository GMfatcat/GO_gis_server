import numpy as np
import psutil
from collections import deque
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context, State
from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
from PIL import ImageGrab


# 生成隨機的 5x5 Numpy 陣列
np.random.seed(0)
# init_data = np.random.rand(30, 20)
init_data = np.random.randint(100,size = (30, 20))

# 建立 Dash 應用程式
# 載入bootstrap感覺有點慢
# app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
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

# some emoji
SMILING_FACE = u"\U0001F600"
THUMBS_UP = u"\U0001F44D"

# Screenshots save path
SCREEN_FOLDER = "Screenshots"

# Queue for the flow fig，init with all 0
QUEUE_MAX_SIZE = 21
FLOW_QUEUE = deque([0]*QUEUE_MAX_SIZE, maxlen = QUEUE_MAX_SIZE)
FLOW_X = [i for i in range(QUEUE_MAX_SIZE)]
FLOW_THRESHOLD = 35000
WARNING_LINE = [FLOW_THRESHOLD for _ in range(QUEUE_MAX_SIZE)]

# 設定 Dash 應用程式的介面
app.layout = html.Div([
    # html.H1('Real Time Signal Dense Grid',style={'margin-left': '25px'}),
    # html.Label('Colormap: ',style={'margin-left': '25px'}),
    html.Div([
    html.H1('Real Time Signal Dense Grid',style={'margin-left': '25px'}),
    # html.Label('Colormap: ',style={'margin-left': '25px'}),
    # tool panel(color)
    dcc.Dropdown(
        id='colorscale-dropdown',
        options=colorscale_options,
        value='Viridis',
        style={'margin-left': '7px','margin-top': '12px','width': '120px'}
        ),
    html.Button('Generate Random Array',
                id='generate-button',
                n_clicks=0,
                style={'margin-left': '15px','margin-top': '22px','height': '37px'}
                ),
    html.Button('Full Page Screenshot',
                id='generate-full-page-screenshot',
                n_clicks=0,
                style={'margin-left': '10px','margin-top': '22px','height': '37px'}
                ),
    # only for screenshot output
    html.Div(id='screenshot-output-div',style={'margin-left': '10px','margin-top': '24px'})
    ],style={'display': 'flex', 'flex-direction': 'row'}),
    # only for screenshot output
    dcc.Interval(
        id='screenshot-output-component',
        interval=2500, # 2.5秒
        n_intervals=0
    ),
    html.Hr(),
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
    ),
    html.Div([
    dcc.Graph(
            id='flow-chart'
            ),
    html.Div([
        html.Img(src = '/assets/golang-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'}),
        html.Img(src = '/assets/redis-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'})
    ],style={'display': 'flex', 'flex-direction': 'column'}),
    html.Div([
        html.Img(src = '/assets/sql-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'}),
        html.Img(src = '/assets/github-142-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'})
    ],style={'display': 'flex', 'flex-direction': 'column'}),
    html.Div([
        html.Img(src = '/assets/flask-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'}),
        html.Img(src = '/assets/python-svgrepo-com.svg',
        style = {'height': '80px', 'width': '80px', 'margin': '10px'})
    ],style={'display': 'flex', 'flex-direction': 'column'})
    ],style={'margin-left': '30px','display': 'flex', 'flex-direction': 'row'})
    ])

def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage,memory_usage

@app.callback(
    Output('screenshot-output-div', 'children'),
    [Input('generate-full-page-screenshot', 'n_clicks')],
    [Input('screenshot-output-component', 'n_intervals')]
)
def handle_screenshot(n_clicks,n_intervals):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "generate-full-page-screenshot" and n_clicks is not None and n_clicks >0:
        current_time = get_current_time()
        # make valid path
        current_time = current_time.replace(" ","_").replace("-","_").replace(":","_")
        filename = os.path.join(SCREEN_FOLDER,current_time)
        screenshot = ImageGrab.grab(bbox=(0, 150, 1900, 1000))
        filepath = f"{filename}_fullscreenshot.png"
        # save to png file
        screenshot.save(filepath, 'PNG')
        # Console side output
        print(f"Save screenshot @ {current_time} {THUMBS_UP}")
        # dashboard side output for 2 sec
        return f"Save screenshot @ {current_time} {SMILING_FACE}"
    # remove the word after 2 sec
    if triggered_id == "screenshot-output-component" and n_intervals is not None and n_intervals > 0:
        return ""

def get_flowfig(key_value,data_queue,h,w,fig_title):
    # data save into queue
    data_queue.append(key_value)
    data_list = list(data_queue)
    # fig
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = FLOW_X, y = data_list, name='Signal Flow',
                         line = dict(color = 'royalblue', width = 3, dash = 'dashdot')))
    fig.add_trace(go.Scatter(x = FLOW_X, y = WARNING_LINE, name='Warning',
                         line = dict(color = 'firebrick', width = 2, dash = 'dash')))
    fig.layout.height = h
    fig.layout.width = w
    # get system status
    cpu_usage,memory_usage = get_system_status()
    fig.update_layout(title = f"{fig_title} CPU:{cpu_usage}% Memory:{memory_usage}%",
                   xaxis_title = 'Recent ➝ Past',
                   yaxis_title ='Total',title_x=0.5,title_y=0.8)
    return fig

def get_guage(key_value,fig_title,max_range):
    # 創建Gauge Chart
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

def get_gridfig(data, colorscale, colorbar_title, title, scale, current_time):
    fig = px.imshow(data,
        color_continuous_scale = colorscale,
        labels=dict(x="Longitude", y="Latitude", color = colorbar_title),
        title = f"{title} {current_time}")
    fig.layout.height = scale
    fig.layout.width = scale
    fig.update_layout(title_x=0.5,title_y=0.88)
    return fig

# TODO: make the x y axis number same to the longitude and latitude
def generate_fig(data,colorscale):
    # get current time
    current_time = get_current_time()
    # sum fig
    sum_fig = get_gridfig(data,colorscale,"Total","Signal Total Count",550,current_time)
    # density fig (signal / 4 km²) --> each grid is 2 km width and height
    density_fig = get_gridfig(data/4,colorscale,"Density","Signal Density",550,current_time)
    # Total sum and Max value
    total_sum = np.sum(data)
    max_value = data.max()
    # guage
    sum_guage_fig = get_guage(total_sum,"Total Signal",max_range = 45000)
    max_guage_fig = get_guage(max_value, "Max Signal in Grid",max_range = 120)
    # flow fig
    flow_fig = get_flowfig(total_sum,FLOW_QUEUE,250,1150,f'Signal Flow (Latest {QUEUE_MAX_SIZE - 1})')
    # return
    return sum_fig,density_fig,sum_guage_fig,max_guage_fig,flow_fig

# 合併兩個回呼為一個回呼
@app.callback(
    [Output('grid-graph', 'figure'),
     Output('grid-graph2', 'figure'),
     Output('gauge-chart1', 'figure'),
     Output('gauge-chart2', 'figure'),
     Output('flow-chart', 'figure')],
    [Input('colorscale-dropdown', 'value')],
    [Input('generate-button', 'n_clicks')],
    [Input('interval-component', 'n_intervals')]
)
def update_figures(colorscale, n_clicks, n_intervals):
    # ctx = dash.callback_context
    ctx = callback_context
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

    sum_fig,density_fig,guage_fig1,guage_fig2,flow_fig = generate_fig(data, colorscale)
    return sum_fig, density_fig,guage_fig1,guage_fig2,flow_fig


# 啟動 Dash 應用程式
if __name__ == '__main__':
    if not os.path.exists(SCREEN_FOLDER):
        os.makedirs(SCREEN_FOLDER)
    # run dashboard in debug mode
    app.run_server(debug=True)
    # run dashboard
    # app.run_server()
