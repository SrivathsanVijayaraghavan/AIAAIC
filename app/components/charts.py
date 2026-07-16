import plotly.express as px

def style_chart(fig, xaxis_title=None, yaxis_title=None):
    """Applies global styling config to a Plotly figure."""
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    if xaxis_title is not None:
        fig.update_layout(xaxis_title=xaxis_title)
    if yaxis_title is not None:
        fig.update_layout(yaxis_title=yaxis_title)
    return fig

def create_bar_chart(df, x, y, title, orientation='v', color=None, barmode="relative"):
    """Creates a standardized bar chart."""
    kwargs = {}
    if color:
        kwargs["color"] = color
    else:
        # Default brand color
        kwargs["color_discrete_sequence"] = ["#F63366"]
        
    fig = px.bar(
        df, x=x, y=y, 
        orientation=orientation,
        title=title,
        template="plotly_white",
        barmode=barmode,
        **kwargs
    )
    return style_chart(fig)

def create_pie_chart(df, names, values):
    """Creates a standardized pie/donut chart."""
    fig = px.pie(
        df, names=names, values=values, hole=0.4,
        template="plotly_white", 
        color_discrete_sequence=px.colors.sequential.Sunset_r
    )
    return style_chart(fig)
