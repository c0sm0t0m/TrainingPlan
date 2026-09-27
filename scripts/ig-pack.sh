#!/usr/bin/env bash
# Build a folder Thomas can AirDrop and post to Instagram himself.
# Feed stills are 4:5 (1080x1350). Reels are 9:16 (1080x1920), H.264, with a silent audio track.
#
# scripts/ig-pack.sh <out-dir> --caption-file <path> \
#   [--post img ...] [--reel-stills img ...] [--reel-clips video ...] [--still-seconds 3]
set -euo pipefail

if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: scripts/ig-pack.sh <out-dir> --caption-file <path> [--post img ...] [--reel-stills img ...] [--reel-clips video ...] [--still-seconds 3]" >&2
  exit 1
fi

OUT="$1"
shift

CAPTION_FILE=""
STILL_SECONDS=3
POST_IMAGES=()
REEL_STILLS=()
REEL_CLIPS=()
OPEN_FINDER=1
mode=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --caption-file) CAPTION_FILE="$2"; mode=""; shift 2 ;;
    --still-seconds) STILL_SECONDS="$2"; mode=""; shift 2 ;;
    --no-open) OPEN_FINDER=0; mode=""; shift ;;
    --post) mode="post"; shift ;;
    --reel-stills) mode="stills"; shift ;;
    --reel-clips) mode="clips"; shift ;;
    --*) echo "Unknown flag: $1" >&2; exit 1 ;;
    *)
      case "$mode" in
        post) POST_IMAGES+=("$1") ;;
        stills) REEL_STILLS+=("$1") ;;
        clips) REEL_CLIPS+=("$1") ;;
        *) echo "Unexpected argument: $1" >&2; exit 1 ;;
      esac
      shift
      ;;
  esac
done

if [[ -z "$CAPTION_FILE" || ! -f "$CAPTION_FILE" ]]; then
  echo "Need an existing --caption-file" >&2
  exit 1
fi
if [[ ${#POST_IMAGES[@]} -eq 0 && ${#REEL_STILLS[@]} -eq 0 && ${#REEL_CLIPS[@]} -eq 0 ]]; then
  echo "Need at least one --post image, --reel-stills image, or --reel-clips video" >&2
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required" >&2
  exit 1
fi

mkdir -p "$OUT/post" "$OUT/reel"
cp "$CAPTION_FILE" "$OUT/caption.txt"

# Fit the image inside WxH. Fill the bars with a blurred copy of the same image.
fit_image() {
  local src="$1" dest="$2" w="$3" h="$4"
  ffmpeg -y -i "$src" -filter_complex \
    "[0:v]scale=${w}:${h}:force_original_aspect_ratio=increase,crop=${w}:${h},boxblur=24:2[bg]; \
     [0:v]scale=${w}:${h}:force_original_aspect_ratio=decrease[fg]; \
     [bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p" \
    -frames:v 1 -q:v 2 "$dest" >/dev/null 2>&1
}

still_to_segment() {
  local src="$1" dest="$2"
  ffmpeg -y -loop 1 -i "$src" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -t "$STILL_SECONDS" -filter_complex \
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2[bg]; \
     [0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; \
     [bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fps=30" \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "$dest" >/dev/null 2>&1
}

clip_to_segment() {
  local src="$1" dest="$2"
  ffmpeg -y -i "$src" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -filter_complex \
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2[bg]; \
     [0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; \
     [bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fps=30[v]" \
    -map "[v]" -map 1:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "$dest" >/dev/null 2>&1
}

i=1
if [[ ${#POST_IMAGES[@]} -gt 0 ]]; then
  for img in "${POST_IMAGES[@]}"; do
    printf -v name "post/%02d.jpg" "$i"
    fit_image "$img" "$OUT/$name" 1080 1350
    i=$((i + 1))
  done
fi

SEG_DIR="$(mktemp -d)"
trap 'rm -rf "$SEG_DIR"' EXIT
segments=()
n=0
if [[ ${#REEL_STILLS[@]} -gt 0 ]]; then
  for img in "${REEL_STILLS[@]}"; do
    n=$((n + 1))
    seg="$SEG_DIR/s$(printf '%02d' "$n").mp4"
    still_to_segment "$img" "$seg"
    segments+=("$seg")
  done
fi
if [[ ${#REEL_CLIPS[@]} -gt 0 ]]; then
  for clip in "${REEL_CLIPS[@]}"; do
    n=$((n + 1))
    seg="$SEG_DIR/c$(printf '%02d' "$n").mp4"
    clip_to_segment "$clip" "$seg"
    segments+=("$seg")
  done
fi

if [[ ${#segments[@]} -gt 0 ]]; then
  list="$SEG_DIR/list.txt"
  : > "$list"
  for seg in "${segments[@]}"; do
    printf "file '%s'\n" "$seg" >> "$list"
  done
  ffmpeg -y -f concat -safe 0 -i "$list" -c copy "$OUT/reel/reel.mp4" >/dev/null 2>&1
  ffmpeg -y -i "$OUT/reel/reel.mp4" -frames:v 1 -q:v 2 "$OUT/reel/cover.jpg" >/dev/null 2>&1
else
  rm -rf "$OUT/reel"
fi

if [[ ${#POST_IMAGES[@]} -eq 0 ]]; then
  rm -rf "$OUT/post"
fi

cat > "$OUT/UPLOAD.txt" <<'EOF'
AirDrop this folder to your iPhone, then post it yourself.

Post: Instagram + → Post → pick the files in post/ → paste caption.txt
Reel: Instagram + → Reel → pick reel/reel.mp4 → paste caption.txt
Cover for the reel is reel/cover.jpg if you want to set one.
EOF

if [[ "$OPEN_FINDER" -eq 1 && "$(uname)" == "Darwin" ]]; then
  open "$OUT"
fi

echo "$OUT"
