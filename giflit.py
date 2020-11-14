import asyncio
import os

import requests
from dotenv import load_dotenv
from PIL import Image


load_dotenv()


GAME_NAME = "GIFLIT_KEYBOARD_LIGHTING"
EVENT_NAME = "BITMAP_EVENT"
SRV_ADDRESS = "http://" + os.getenv("SRV_ADDRESS")
GS_EVENT_ENDPOINT = f"{SRV_ADDRESS}/game_event"
GS_HB_ENDPOINT = f"{SRV_ADDRESS}/game_heartbeat"

TEST_GIF_SOURCE = "test.gif"


def send_to_gs(data):
    r = requests.post(
        GS_EVENT_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=data,
    )
    assert (
        r.status_code == requests.codes.OK
    ), f"Request to {GS_EVENT_ENDPOINT} failed. Code: {r.status_code}, Response: {r.content}"


def register_game():
    r = requests.post(
        f"{SRV_ADDRESS}/game_metadata",
        headers={"Content-Type": "application/json"},
        data={
            "game": GAME_NAME,
            "game_display_name": "gif-lighting for keyboards",
            "developer_name": "nikochiko (github/nikochiko)",
        },
    )
    assert r.status_code == requests.codes.OK, "Couldn't register game"


def register_event():
    r = requests.post(
        GS_EVENT_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data={"game": GAME_NAME, "event": EVENT_NAME, "value_optional": True},
    )
    assert r.status_code == requests.codes.OK, "Couldn't register event"


def get_box(size, req_size=(22, 6)):
    width, height = size
    req_width, req_height = req_size
    w_to_h = req_width / req_height
    x1, y1 = 0, 0
    new_width = w_to_h * height

    if new_width > width:
        new_height = width / w_to_h
        new_width = w_to_h * new_height
    else:
        new_height = new_width / w_to_h

    x1, y1 = (width - new_width) / 2, (height - new_height) / 2
    x2, y2 = x1 + new_width, y1 + new_height
    return (x1, y1, x2, y2)


def yield_rgb_frames(im, req_size=(22, 6)):
    for frame_no in range(0, im.n_frames):
        im.seek(frame_no)
        im2 = im.resize(req_size, box=get_box(im.size, req_size))
        yield [
            im2.getpixel((x, y))
            for x in range(im2.width)
            for y in range(im2.height)
        ]


async def start_sending_heartbeats(interval=14):
    while True:
        r = requests.post(
            GS_HB_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data={"game": GAME_NAME},
        )
        assert r.status_code == requests.codes.OK, "Heartbeat failed"
        await asyncio.sleep(interval)


async def send_gif_frames(
    gif_source, frame_delay=0.1, req_size=(22, 6), forever=False
):
    im = Image.open(gif_source).convert("RGB")

    while True:
        for frame in yield_rgb_frames(im, req_size):
            data = {
                "game": GAME_NAME,
                "event": EVENT_NAME,
                "data": {"frame": {"bitmap": frame}},
            }
            send_to_gs(data)
            await asyncio.sleep(frame_delay)
        if not forever:
            break


async def main(heartbeat_interval=14):
    register_game()
    register_event()

    heartbeats = asyncio.create_task(
        start_sending_heartbeats(heartbeat_interval)
    )
    send_gifs = asyncio.create_task(
        send_gif_frames(TEST_GIF_SOURCE, forever=True)
    )
    await heartbeats
    await send_gifs


if __name__ == "__main__":
    asyncio.run(main())
