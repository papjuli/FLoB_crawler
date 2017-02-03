import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("FLoB_coordinates_-_video_data.tsv", sep="\t")
t = df["cumulative duration"]
z = df["Z coord (max known)"]

fig, ax = plt.subplots()
ax.scatter(t, z)
for i, ep in enumerate(df["episode"]):
  ax.annotate(ep, (t[i], z[i]))

plt.show()
