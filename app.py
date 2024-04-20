import os

import dash
from dash import dcc, html
from speech_recognizer import SpeechRecognizer
from dash.dependencies import Input, Output

PATH = "assets/pmoney.wav"

app = dash.Dash(__name__)
server = app.server

recognizer = SpeechRecognizer(PATH)

app.layout = html.Div(
    [
        html.H4(children="AI Speech Recognition (Planet Money podcast)"),
        dcc.Markdown(
            "Written in 100 lines of Python with [Dash](https://dash.plot.ly/)."
        ),
        html.P(children="Transcription using Azure speech to text:"),
        html.Br(),
        html.Audio(id="player", src=PATH, controls=True, style={"width": "100%"}),
        dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0),
        html.Div(id="output-container"),
    ]
)


@app.callback(
    Output("output-container", "children"), [Input("interval-component", "n_intervals")]
)
def update_output(n_intervals):
    print(f"Interval called {n_intervals} times")
    return [html.P(children=line) for line in recognizer.converted_text]


if __name__ == "__main__":
    recognizer.start_converting()
    app.run_server(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8500))
