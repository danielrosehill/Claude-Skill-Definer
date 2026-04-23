#!/usr/bin/env bash
# Downsample a video for cheap vision-model ingestion.
# Usage: downsample-video.sh <input> [fps=1] [height=480]

set -euo pipefail

INPUT="${1:?input video required}"
FPS="${2:-1}"
HEIGHT="${3:-480}"

BASENAME="$(basename "${INPUT%.*}")"
WORKDIR="inbox/video/${BASENAME}-work"
mkdir -p "${WORKDIR}/frames"

echo "Downsampling to ${WORKDIR}/downsampled.mp4 …"
ffmpeg -y -i "${INPUT}" \
  -vf "fps=${FPS},scale=-2:${HEIGHT}" \
  -c:v libx264 -crf 32 -c:a aac -b:a 64k \
  "${WORKDIR}/downsampled.mp4"

echo "Extracting keyframes (1 per 5s) to ${WORKDIR}/frames/ …"
ffmpeg -y -i "${INPUT}" -vf "fps=1/5" "${WORKDIR}/frames/%04d.jpg"

if ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "${INPUT}" | grep -q audio; then
  echo "Extracting audio to ${WORKDIR}/audio.m4a …"
  ffmpeg -y -i "${INPUT}" -vn -c:a aac -b:a 96k "${WORKDIR}/audio.m4a"
fi

echo "Done. Workdir: ${WORKDIR}"
