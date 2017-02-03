# FLoB crawler

These are a couple of scripts for downloading information (duration, publish time, id) about the videos of the YouTube series called [Far Lands or Bust](https://www.youtube.com/user/kurtjmac/playlists?shelf_id=13&view=50&sort=dd). In this series KurtJMac walks towards West in an old version of Minecraft in order to reach the fabled Far Lands. I wrote the scripts when I was trying to guess the distance travelled before the coordinate reveal at the end of Season 6.

In order to run these, you need to have a Google API key and the following python packages (all can be pip-installed):
* google-api-python-client
* pandas
* json
* matplotlib (for the plotter script)

`flob_crawler.py` makes a search query to the YT API for the term "Minecraft Far Lands or Bust", within Kurt's channel. Interestingly, this doesn't find all the episodes, and the set of the found ones varies for each run. So I wrote another script, that can be used to get the missing episodes and the Flobathon videos, by supplying an input file containing a json list like `["#640", "FLoB-ATHON 2017 (Part 1)", "FLoB-ATHON 2017 (Part 2)"]`.

Example:

```
$ python flob_crawler.py $GOOGLE_API_KEY data.tsv
```
```
$ python get_missing_episodes.py $GOOGLE_API_KEY missing_ep_list.json data_so_far.tsv data.tsv
```
The `data_so_far.tsv` file doesn't have to exists. The `data.tsv` will contain the data in `data_so_far.tsv` and the newly downloaded info (they can be the same).

The file `FLoB_coordinates_-_video_data.tsv` contains the video data that I gathered this way, and also coordinates from [here](https://www.reddit.com/r/mindcrack/comments/1ognid/flob_coordinates_season_3_part_4_of_4season_4/) and some of the later videos.

```
$ python plot_Z_over_time.py
```
plots a point for each episode that has some known coordinate in the above file, with time on the `x` axis, and the (max known) Z coordinate on the `y` axis.

The `FLoB_coordinates.ods` file is an export of the spreadsheet that contains these infos and some other stuff.


