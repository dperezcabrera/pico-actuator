"""Boot the app. pico-boot auto-discovers pico-fastapi + pico-actuator.

Run (from examples/minimal):
    pip install pico-actuator uvicorn[standard]
    uvicorn myapp.main:app --reload

Then:
    curl localhost:8000/api/hello
    curl localhost:8000/actuator/health
    curl localhost:8000/actuator/info
"""

from pathlib import Path

from fastapi import FastAPI
from pico_boot import init
from pico_ioc import YamlTreeSource, configuration

CONFIG_FILE = Path(__file__).resolve().parent.parent / "application.yaml"


def create_app() -> FastAPI:
    config = configuration(YamlTreeSource(str(CONFIG_FILE)))
    container = init(modules=["myapp"], config=config)
    return container.get(FastAPI)


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
