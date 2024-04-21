from datetime import datetime
import os
from typing import Optional

import dash
from dash import dcc, html
from speech_recognizer import SpeechRecognizer
from dash.dependencies import Input, Output
import base64

app = dash.Dash(__name__)
server = app.server

recognizer: Optional[SpeechRecognizer] = None

app.layout = html.Div(
    [
        html.H4(children="AI Speech Recognition (Planet Money podcast)"),
        dcc.Markdown(
            "Written in 100 lines of Python with [Dash](https://dash.plot.ly/)."
        ),
        dcc.Upload(
            id="upload-audio",
            children=html.Button("Upload Audio File"),
            accept=".wav, .mp3",
        ),
        html.Div(id="output-audio"),
        html.P(children="Transcription using Azure speech to text:"),
        html.Br(),
        dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0),
        html.Div(id="output-container"),
    ]
)


@app.callback(
    Output("output-container", "children"), [Input("interval-component", "n_intervals")]
)
def update_transcript_output(n_intervals):
    global recognizer
    if not recognizer:
        return None
    return [html.P(children=line) for line in recognizer.converted_text]


def save_file_locally(file_content: bytes, file_ext: str):
    try:
        filename = f"uploads/{datetime.now():%Y%m%d_%H%M%S}.{file_ext}"
        with open(filename, "wb") as f:
            f.write(file_content)
        return filename
    except Exception as e:
        print(str(e))


def parse_contents(contents, filename):
    content_string = contents
    if "," in contents:
        content_string = contents.split(",")[1]

    decoded = base64.b64decode(content_string)

    if "wav" in filename:
        file_ext = "wav"
    elif "mp3" in filename:
        file_ext = "mp3"
    else:
        return html.Div("Unsupported file format")
    base64string_content = (
        f"data:audio/{file_ext};base64,{base64.b64encode(decoded).decode()}"
    )
    file_name = save_file_locally(file_content=decoded, file_ext=file_ext)
    if not file_name:
        return html.Div("Couldn't transcribe the audio file")
    global recognizer
    recognizer = SpeechRecognizer(file_name)
    recognizer.start_converting()

    return html.Audio(
        src=base64string_content,
        controls=True,
    )


@app.callback(
    Output("output-audio", "children"),
    [Input("upload-audio", "contents")],
    [Input("upload-audio", "filename")],
)
def update_output(content: Optional[str], file_name: Optional[str]):
    if content and file_name:
        return parse_contents(content, file_name)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8500))
