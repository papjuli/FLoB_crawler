from apiclient.discovery import build
from apiclient.errors import HttpError
import pandas as pd
import json


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class YoutubeFlobCrawler(object):
  """A Youtube crawler to get info of the Far Lands or Bust episodes.
     Note that it uses a search query, which does not get all episodes,
     and the set of episodes varies for each run.
  """
  def __init__(self, developer_key, log_file=None):
    """
    Args:
        developer_key (string): for the Youtube Data API. See https://developers.google.com/youtube/registering_an_application
        log_file (string, optional): name of file to log query answers
    """
    self.youtube = build(YOUTUBE_API_SERVICE_NAME, 
                         YOUTUBE_API_VERSION,
                         developerKey=developer_key)
    self.channelId="UC1Un5592U9mFx5n6j2HyXow"
    self.query = "Minecraft Far Lands or Bust"
    self.empty_data = {"episode":  pd.Series([]).astype("int16"), 
                       "title": [], 
                       "publishedAt": [], 
                       "videoId": [], 
                       "duration": pd.Series([]).astype("int16")}
    self.attributes = ["episode", "title", "publishedAt", "videoId", "duration"]
    self.results = pd.DataFrame(data=self.empty_data, columns=self.attributes)
    self.counter = 0
    self.maxResults = 50
    self.nextPageToken = None
    self.nextPageExists = True
    if log_file != None:
      self.log_file = open(log_file, "w")
    else:
      self.log_file = None
  
  
  def run(self, last_episode=637):
    while self.nextPageExists and (self.counter < last_episode):
      self.get_next_batch()
    self.results = self.results.sort_values(by="episode").drop_duplicates()
  
  
  def get_next_batch(self):
    batch_data = {}
    
    search_response = self.make_next_search_query()
    for search_result in search_response.get("items", []):
      title = search_result["snippet"]["title"]
      if self.query not in title or "#" not in title:
        continue
      data = self.video_data_from_search(search_result)
      batch_data[data["videoId"]] = data
      self.counter += 1
    
    videos_response = self.make_videos_query(",".join(batch_data.keys()))
    for video_result in videos_response.get("items", []):
      videoId = video_result["id"]
      duration_str = video_result["contentDetails"]["duration"]
      batch_data[videoId]["duration"] = duration_string_to_seconds(duration_str)
    
    for id_ in batch_data:
      row = [batch_data[id_][attr] for attr in self.attributes]
      self.results.loc[self.results.shape[0]] = row
    print self.results.shape[0], self.counter
  
  
  def make_next_search_query(self):
    search_response = self.youtube.search().list(
      channelId=self.channelId,
      q=self.query,
      type="video",
      part="id,snippet",
      maxResults=self.maxResults,  # at most 50
      pageToken=self.nextPageToken
    ).execute()
    if self.log_file:
      self.log_file.write(json.dumps(search_response, indent=2))
    try:
      self.nextPageToken = search_response["nextPageToken"]
    except KeyError:
      self.nextPageExists = False
    if len(search_response["items"]) < self.maxResults:
      self.nextPageExists = False
    return search_response
  
  def make_videos_query(self, video_ids):
    videos_response = self.youtube.videos().list(
      part="id,contentDetails",
      id=video_ids,
      maxResults=self.maxResults,
    ).execute()
    if self.log_file:
      self.log_file.write(json.dumps(videos_response, indent=2))
    return videos_response
  
  def video_data_from_search(self, search_result):
    data = {}
    data["title"] = search_result["snippet"]["title"]
    data["publishedAt"] = search_result["snippet"]["publishedAt"]
    data["videoId"] = search_result["id"]["videoId"]
    data["episode"] = get_episode_number(data["title"])
    return data
  
  
  def __del__(self):
    if self.log_file != None:
      self.log_file.close()


def get_episode_number(title):
  try:
    hashmark_index = title.index("#")
    from_hashmark = title[hashmark_index : ]
    ep_string = title[hashmark_index + 1 : hashmark_index + from_hashmark.index(" ")]
    return int(ep_string)
  except:
    return "NA"

def duration_string_to_seconds(dur):
  amounts = {"H": 0, "M": 0, "S": 0}
  while dur[-1] in "HMS":
    letter = dur[-1]
    dur = dur[:-1]
    i = [x for x in range(len(dur)) if dur[x].isalpha()][-1]
    amounts[letter] = int(dur[i + 1:])
    dur = dur[:i + 1]
  return amounts["H"] * 3600 + amounts["M"] * 60 + amounts["S"]


if __name__ == "__main__":
  import sys
  developer_key = sys.argv[1]
  output_file = sys.argv[2]
  if len(sys.argv) >= 4:
    log_file = sys.argv[3]
  else:
    log_file = None
  crawler = YoutubeFlobCrawler(developer_key, log_file)
  try:
    crawler.run()
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  if crawler.counter > 0:
    crawler.results.to_csv(output_file, sep="\t", encoding='utf-8')

