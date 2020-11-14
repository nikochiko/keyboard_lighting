### GifLit Keyboard lighting

**Works with SteelSeries GameSense**

Note: Python 3.8 recommended (3.7 and 3.9 also probably work)

### How to get it running?

1. Edit .env and change the SRV_ADDRESS variable to the local gamesense server adress. (Refer [this doc](https://github.com/SteelSeries/gamesense-sdk/blob/master/doc/api/sending-game-events.md#server-discovery) for where it can be found.)
2. For testing, put a gif in this directory with the name "test.gif"
3. Optional: Create a virtualenv and activate it
4. Run `pip install -r requirements.txt` to install dependencies
5. Run `giflit.py` with `python giflit.py`. It will run on a forever loop and keep sending heartbeats. Use `CTRL+C` to stop it.
