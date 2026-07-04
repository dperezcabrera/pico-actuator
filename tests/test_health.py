import asyncio
import time

from pico_actuator.health import DOWN, UP, gather


class _Up:
    name = "db"

    def check(self):
        return True


class _Detail:
    name = "disk"

    def check(self):
        return {"status": UP, "free_mb": 1234}


class _Down:
    name = "redis"

    def check(self):
        raise RuntimeError("boom")


def test_gather_aggregates_and_isolates_failures():
    overall, comp = asyncio.run(gather([_Up(), _Detail(), _Down()]))
    assert overall == DOWN  # a single DOWN drags the overall down
    assert comp["db"]["status"] == UP
    assert comp["disk"]["free_mb"] == 1234  # detail dicts pass through
    assert comp["redis"]["status"] == DOWN and "boom" in comp["redis"]["error"]


def test_gather_all_up():
    overall, comp = asyncio.run(gather([_Up(), _Detail()]))
    assert overall == UP
    assert set(comp) == {"db", "disk"}


class _Slow:
    name = "slow"

    async def check(self):
        await asyncio.sleep(10)


class _SlowSync:
    name = "slow-sync"

    def check(self):  # blocking sleep: must not freeze the event loop
        time.sleep(0.5)


def test_timeout_reports_down_instead_of_hanging():
    async def timed():
        start = time.monotonic()
        result = await gather([_Slow(), _SlowSync(), _Up()], timeout=0.1)
        # measured inside the loop: the endpoint answers fast even though the
        # orphaned sync thread is still sleeping (asyncio.run waits for it at exit)
        return result, time.monotonic() - start

    (overall, comp), elapsed = asyncio.run(timed())
    assert elapsed < 0.4
    assert overall == DOWN
    assert "timed out" in comp["slow"]["error"]
    assert "timed out" in comp["slow-sync"]["error"]
    assert comp["db"]["status"] == UP  # siblings unaffected


class _Napper:
    def __init__(self, name):
        self.name = name

    async def check(self):
        await asyncio.sleep(0.2)
        return True


def test_indicators_run_concurrently():
    start = time.monotonic()
    overall, comp = asyncio.run(gather([_Napper("a"), _Napper("b"), _Napper("c")]))
    assert overall == UP and len(comp) == 3
    assert time.monotonic() - start < 0.5  # ~0.2s concurrent, not 0.6s sequential


if __name__ == "__main__":
    test_gather_aggregates_and_isolates_failures()
    test_gather_all_up()
    print("ok")
