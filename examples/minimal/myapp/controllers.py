"""A plain application endpoint living next to the actuator ones."""

from pico_fastapi import controller, get


@controller(prefix="/api", tags=["demo"])
class HelloController:
    @get("/hello")
    async def hello(self):
        return {"message": "hello from pico-fastapi + pico-actuator"}
