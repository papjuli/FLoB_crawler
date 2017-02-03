from apiclient.discovery import build
from apiclient.errors import HttpError
import pandas as pd
import json


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class YoutubeFlobEp(object):
  """A Youtube querying class to get info of given Far Lands or Bust episodes one by one.
  """
  def __init__(self, developer_key, log_file=None):
    """
    Args:
        developer_key (string): for the Youtube Data API. See https://developers.google.com/youtube/registering_an_application
        episodes (list of ints): list of episode numbers to query
        log_file (string, optional): name of file to log query answers
    """
    self.youtube = build(YOUTUBE_API_SERVICE_NAME, 
                         YOUTUBE_API_VERSION,
                         developerKey=developer_key)
    self.channelId="UC1Un5592U9mFx5n6j2HyXow"
    self.query = "Minecraft Far Lands or Bust "
    self.maxResults = 1
    self.empty_data = {"episode":  pd.Series([]).astype("int16"), 
                       "title": [], 
                       "publishedAt": [], 
                       "videoId": [], 
                       "duration": pd.Series([]).astype("int16")}
    self.attributes = ["episode", "title", "publishedAt", "videoId", "duration"]
    self.results = pd.DataFrame(data=self.empty_data, columns=self.attributes)
    if log_file != None:
      self.log_file = open(log_file, "w")
    else:
      self.log_file = None
  
  def run(self, data_so_far, episodes):
    try:
      self.results = pd.read_csv(data_so_far, sep="\t")
    except IOError:
      self.results = pd.DataFrame(data=self.empty_data, columns=self.attributes)
    for ep in episodes:
      search_response = self.make_search_query(ep)
      video_data = self.video_data_from_search(search_response.get("items", [])[0])
      
      video_id = video_data["videoId"]
      videos_response = self.make_videos_query(video_id)
      for video_result in videos_response.get("items", []):
        videoId = video_result["id"]
        duration_str = video_result["contentDetails"]["duration"]
        video_data["duration"] = duration_string_to_seconds(duration_str)
      
      row = [video_data[attr] for attr in self.attributes]
      print row  
      print self.results.columns
      self.results.loc[self.results.shape[0]] = row
    self.results = self.results.sort_values(by="episode").drop_duplicates()
  
  def get_livestreams(self, video_ids):
    for vid in video_ids:
      videos_response = self.make_videos_query(video_id)
      video_data = video_data_from_search(videos_response)
      for video_result in videos_response.get("items", []):
        videoId = video_result["id"]
        duration_str = video_result["contentDetails"]["duration"]
        video_data["duration"] = duration_string_to_seconds(duration_str)
      
      row = [video_data[attr] for attr in self.attributes]
      self.results.loc[self.results.shape[0]] = row
  
  def make_search_query(self, episode):
    ep_string = str(episode)
    #query = self.query + " #" + "0"*(3 - len(ep_string)) + ep_string
    query = self.query + ep_string
    search_response = self.youtube.search().list(
      channelId=self.channelId,
      q=query,
      type="video",
      part="id,snippet",
      maxResults=self.maxResults,
      #pageToken=None
    ).execute()
    if self.log_file:
      self.log_file.write(json.dumps(search_response, indent=2))
    return search_response
  
  def make_videos_query(self, video_ids):
    videos_response = self.youtube.videos().list(
      part="id,snippet,contentDetails",
      id=video_ids,
      maxResults=self.maxResults,
    ).execute()
    if self.log_file:
      self.log_file.write(json.dumps(videos_response, indent=2))
    return videos_response
  
  @staticmethod
  def video_data_from_search(search_result):
    data = {}
    data["title"] = search_result["snippet"]["title"]
    data["publishedAt"] = search_result["snippet"]["publishedAt"]
    data["videoId"] = search_result["id"]["videoId"]
    data["episode"] = get_episode_number(data["title"])
    return data


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
  episodes_file = sys.argv[2]
  data_file = sys.argv[3]
  output_file = sys.argv[4]
  if len(sys.argv) >= 6:
    log_file = sys.argv[5]
  else:
    log_file = None
  with open(episodes_file) as f:
    episodes = json.load(f)
  crawler = YoutubeFlobEp(developer_key, log_file=log_file)
  try:
    crawler.run(data_file, episodes)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  if crawler.results.shape[0] > 0:
    crawler.results.to_csv(output_file, sep="\t", encoding='utf-8', index=False)

