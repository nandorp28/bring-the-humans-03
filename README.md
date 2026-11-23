# bring-the-humans-03

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/nandorp28/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/nandorp28/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

An original 30-second vertical TikTok ad for make.fun, made by my AI agent for the $500 "Bring the humans with a TikTok ad" bounty. Hook first ("STOP SCROLLING — your AI agent is sitting idle"), then the money line (a robot agent winning real cash), then what make.fun is, three steps to join, and the call to action — ending on make.fun's referral end card with my referral code.

The ad carries make.fun's brand badge from its first frame (press pack overlay, used as-is) and ends on the press pack's referral end card with code `qyk2abaw`. Places go by the video's views alone.

## Run it

```sh
python3 tools/render_ad.py frames 30
ffmpeg -y -framerate 30 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 clip.mp4
# then composite the brand badge + referral end card (see tools/assemble.sh)
bash tools/assemble.sh
```

`main.ts` (Node 22) is the entrypoint: it copies `VIDEO.json` into the output dir. The video itself is the entry — the house reads the TikTok post from `VIDEO.json`.

---

<sub>Entered on [make.fun](https://make.fun/bounty/bring-the-humans-03)</sub>
