#!/bin/bash
# Assemble the bring-the-humans-03 ad: frames -> clip, then composite the
# make.fun brand badge (from frame 0 until the end card) and the referral
# end card (last 2.5 s) with our referral code, per make.fun's press guide
# (https://make.fun/press/llms.txt). Run from the repo root.
set -euo pipefail

CLIP=clip.mp4
CODE=qyk2abaw
FONT=assets/JetBrainsMono-Bold.ttf
BADGE=assets/makefun-badge-9x16.png
CARD=assets/makefun-card-9x16-transparent.webm
OUT=video/bring-the-humans-03.mp4

# 1. Frames -> clip (30 fps, 1080x1920).
ffmpeg -y -v error -framerate 30 -i /tmp/bth03-frames/f%04d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 18 "$CLIP"

# 2. Badge + end card. The card's numbers come from the press manifest
# (referral_card.fields "9:16"): it rests 1.433 s in, the field's caret is at
# x 210, y 1232 (5 x 78 px), the code is centred on y 1271 at 62 px.
LEN=2.5
REST=1.433
CX=210
CY=1232
CW=5
CH=78
MID=1271
SIZE=62
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
T=$(awk "BEGIN{print $D-$LEN}")
CODE_AT=$(awk "BEGIN{print $T+$REST}")

ffmpeg -y -v error -i "$CLIP" -c:v libvpx-vp9 -i "$CARD" -i "$BADGE" \
  -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuva420p,split[clip][soft];\
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft];\
[clip][soft]overlay[bg];\
[2:v]format=yuva420p[badge];\
[bg][badge]overlay=enable='lt(t,$T)'[badged];\
[1:v]format=yuva420p,setpts=PTS-STARTPTS+$T/TB[card];\
[badged][card]overlay=eof_action=pass,\
drawbox=x=$CX-2:y=$CY-2:w=$CW+4:h=$CH+4:color=white:t=fill:enable='gte(t,$CODE_AT)',\
drawtext=fontfile=$FONT:text=$CODE:fontsize=$SIZE:fontcolor=0x191419:x=$CX:y=$MID-(ascent-descent)/2:enable='gte(t,$CODE_AT)'[v]" \
  -map '[v]' -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "$OUT"

echo "wrote $OUT"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 "$OUT"
