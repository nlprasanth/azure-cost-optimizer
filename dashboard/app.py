import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from .api import DashboardAPI

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize Dashboard API
api = DashboardAPI(os.getenv('AZURE_SUBSCRIPTION_ID'))

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="#")),
        dbc.NavItem(dbc.NavLink("Cost Analysis", href="#")),
        dbc.NavItem(dbc.NavLink("Resource Optimization", href="#")),
        dbc.NavItem(dbc.NavLink("Recommendations", href="#"))
    ],
    brand="Azure Cost Optimization Dashboard",
    brand_href="#",
    color="primary",
    dark=True
)

# Layout
app.layout = html.Div([
    navbar,
    dbc.Container([
        # Time range selector
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Time Range:"),
                        dcc.Dropdown(
                            id='time-range-selector',
                            options=[
                                {'label': 'Last 7 Days', 'value': 7},
                                {'label': 'Last 30 Days', 'value': 30},
                                {'label': 'Last 90 Days', 'value': 90}
                            ],
                            value=30,
                            clearable=False
                        )
                    ])
                ], className="mt-3 mb-3")
            ])
        ]),

        # Summary cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Cost", className="card-title"),
                        html.H2(id="total-cost", className="text-primary"),
                        html.P(id="cost-trend", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Potential Savings", className="card-title"),
                        html.H2(id="potential-savings", className="text-success"),
                        html.P(id="savings-opportunity", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Resources", className="card-title"),
                        html.H2(id="resource-count", className="text-info"),
                        html.P(id="resource-status", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Optimization Score", className="card-title"),
                        html.H2(id="optimization-score", className="text-warning"),
                        html.P(id="score-trend", className="card-text")
                    ])
                ])
            ], width=3)
        ], className="mb-4"),

        # Cost Analysis Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Cost Trends"),
                    dbc.CardBody([
                        dcc.Graph(id='cost-trend-graph')
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Cost Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id='cost-distribution-graph')
                    ])
                ])
            ], width=4)
        ], className="mb-4"),

        # Resource Optimization Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Resource Utilization"),
                    dbc.CardBody([
                        dcc.Graph(id='resource-utilization-graph')
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Scaling Efficiency"),
                    dbc.CardBody([
                        dcc.Graph(id='scaling-efficiency-graph')
                    ])
                ])
            ], width=6)
        ], className="mb-4"),

        # Recommendations Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Optimization Recommendations"),
                    dbc.CardBody([
                        html.Div(id='recommendations-table')
                    ])
                ])
            ])
        ])
    ], fluid=True)
])

# Callbacks
@app.callback(
    [Output('total-cost', 'children'),
     Output('cost-trend', 'children'),
     Output('potential-savings', 'children'),
     Output('savings-opportunity', 'children'),
     Output('resource-count', 'children'),
     Output('resource-status', 'children'),
     Output('optimization-score', 'children'),
     Output('score-trend', 'children')],
    [Input('time-range-selector', 'value')]
)
def update_summary_cards(time_range):
    try:
        # Get summary data
        summary = api.get_summary()
        
        # Format outputs
        total_cost = f"${summary['cost']['total_cost']:,.2f}"
        cost_trend = "↑ 5% vs. previous period"  # You'll need to calculate this
        
        potential_savings = f"${summary['cost']['potential_savings']:,.2f}"
        savings_opportunity = f"{len(summary['cost']['recommendation_count'])} opportunities"
        
        resource_count = sum(
            summary[module]['resources_analyzed']
            for module in ['scaling', 'monitoring', 'tagging', 'utilization']
        )
        resource_status = f"{summary['utilization']['underutilized_resources']} need attention"
        
        optimization_score = f"{summary['cost']['optimization_score']:.1f}%"
        score_trend = "↑ 2% vs. previous period"  # You'll need to calculate this
        
        return (
            total_cost, cost_trend,
            potential_savings, savings_opportunity,
            resource_count, resource_status,
            optimization_score, score_trend
        )
    except Exception as e:
        return ("$0", "", "$0", "", "0", "", "0%", "")

@app.callback(
    Output('cost-trend-graph', 'figure'),
    [Input('time-range-selector', 'value')]
)
def update_cost_trend(time_range):
    try:
        # Get cost trends
        trends = api.get_cost_trends()
        
        # Create figure
        fig = go.Figure()
        
        # Add actual costs
        fig.add_trace(go.Scatter(
            x=trends['daily_trends']['dates'],
            y=trends['daily_trends']['costs'],
            name='Actual Cost',
            line=dict(color='blue')
        ))
        
        # Add forecasted costs
        fig.add_trace(go.Scatter(
            x=trends['cost_forecast']['dates'],
            y=trends['cost_forecast']['costs'],
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title='Daily Cost Trend and Forecast',
            xaxis_title='Date',
            yaxis_title='Cost (USD)',
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output('cost-distribution-graph', 'figure'),
    [Input('time-range-selector', 'value')]
)
def update_cost_distribution(time_range):
    try:
        # Get cost analysis
        analysis = api.get_cost_analysis()
        
        # Get service costs
        services = []
        costs = []
        for service, data in analysis['analysis']['service_costs'].items():
            services.append(service)
            costs.append(data['total_cost'])
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=services,
            values=costs,
            hole=.3
        )])
        
        fig.update_layout(
            title='Cost Distribution by Service'
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output('resource-utilization-graph', 'figure'),
    [Input('time-range-selector', 'value')]
)
def update_resource_utilization(time_range):
    try:
        # Get utilization analysis
        analysis = api.get_utilization_analysis()
        
        # Process data
        resources = []
        cpu_util = []
        memory_util = []
        for resource in analysis['analysis']['resources']:
            resources.append(resource['name'])
            cpu_util.append(resource['cpu_utilization'])
            memory_util.append(resource['memory_utilization'])
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(name='CPU', x=resources, y=cpu_util),
            go.Bar(name='Memory', x=resources, y=memory_util)
        ])
        
        fig.update_layout(
            title='Resource Utilization',
            barmode='group',
            yaxis_title='Utilization %'
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output('scaling-efficiency-graph', 'figure'),
    [Input('time-range-selector', 'value')]
)
def update_scaling_efficiency(time_range):
    try:
        # Get scaling analysis
        analysis = api.get_scaling_analysis()
        
        # Process data
        resources = []
        efficiency = []
        for resource in analysis['analysis']['resources']:
            resources.append(resource['name'])
            efficiency.append(resource['scaling_efficiency'])
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                x=resources,
                y=efficiency,
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title='Scaling Efficiency by Resource',
            yaxis_title='Efficiency %',
            yaxis_range=[0, 100]
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output('recommendations-table', 'children'),
    [Input('time-range-selector', 'value')]
)
def update_recommendations(time_range):
    try:
        # Get recommendations
        recommendations = api.get_cost_recommendations()
        
        # Create table header
        table_header = [
            html.Thead(html.Tr([
                html.Th("Priority"),
                html.Th("Category"),
                html.Th("Resource"),
                html.Th("Recommendation"),
                html.Th("Potential Savings"),
                html.Th("Action")
            ]))
        ]
        
        # Create table rows
        rows = []
        for priority in ['immediate_actions', 'short_term', 'long_term']:
            for rec in recommendations.get(priority, []):
                row = html.Tr([
                    html.Td(priority.replace('_', ' ').title()),
                    html.Td(rec['type']),
                    html.Td(rec['resource_name']),
                    html.Td(rec.get('recommendations', [])[0] if rec.get('recommendations') else ''),
                    html.Td(f"${rec.get('estimated_savings', 0):,.2f}"),
                    html.Td(
                        dbc.Button(
                            "Apply",
                            color="primary",
                            size="sm",
                            className="mr-1"
                        )
                    )
                ])
                rows.append(row)
        
        table_body = [html.Tbody(rows)]
        
        return dbc.Table(
            table_header + table_body,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True
        )
    except Exception as e:
        return html.Div("No recommendations available")

if __name__ == '__main__':
    app.run_server(debug=True)
