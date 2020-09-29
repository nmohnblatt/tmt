# TENNIS MOMENTUM TRACKER

An application that produces visual representations of the switches in momentum during a tennis match. See `ZverevThiem2020-09-13.mp4` for an example output based on the [2020 US Open's men's final](https://www.scoreboard.com/game/O8bBVnn7/) and `OsakaAzarenka2020-09-12.mp4` based on the [2020 US Open's ladies final](https://www.scoreboard.com/game/CSHYm4GH).

Follow our [Twitter account](https://twitter.com/TennisMomentum)

## Running the application 
After a game is over, find the results on [scoreboard.com](https://www.scoreboard.com) and copy the game URL (e.g. `https://www.scoreboard.com/game/O8bBVnn7`). When running the script, pass the URL as argument:
``$ python tmt.py https://www.scoreboard.com/game/O8bBVnn7 ``



## Requirements

Running the script requires:
- `python v3.8` or above
- `Chrome` browser
- packages `selenium`, `bs4` and `matplotlib`. Install these packages using `pip`:
``$ pip install selenium bs4 matplotlib``
- outputting videos requires to have `ffmpeg` [installed](ffmpeg.org) and linked

NOTE: Script uses `ChromeDriver v85.0.4183.87`. Check your version of `Chrome` and which version of `chromedriver` is recommended. Replace the `chromedriver` file if needed.

## TODO
- Manage application dependencies
- Live game monitoring
- Support for Wimbledon last set TB format. Use [2019 men's final](https://www.scoreboard.com/game/fyXBxdlb) as example (hasn't happened yet on the WTA circuit)
- Support for DOUBLES games
- Improve animation graphics. Improvements include final set scores (e.g. 6-4, 7-5), message announcing the winner, overall design, etc...
