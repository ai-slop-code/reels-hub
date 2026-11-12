#!/bin/sh
# Generates the test clips (spec §24.2, R120): synthetic test patterns and tones with metadata that
# mimics Sony and DJI cameras. Everything goes to tests/fixtures/generated/ (git-ignored); nothing real
# is generated and nothing generated is committed. The folder layout mirrors the watch folders of §5.1.
#
# Known facts the tests rely on:
#   sony/C0003.MP4  audio is clipped (above full scale) from 0.0 to 1.0 s
#   sony/C0004.MP4  camera A: clap at 1.00 s of its own timeline
#   dji/DJI_20261112120000_0005_D.MP4  camera B: clap at 2.25 s, so B is 1.250 s behind A
set -eu

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/tests/fixtures/generated}"
FF="ffmpeg -hide_banner -loglevel error -y -fflags +bitexact -flags:v +bitexact -flags:a +bitexact"
SONY_META="-movflags use_metadata_tags -metadata make=Sony -metadata model=ILME-FX30 -metadata creation_time=2026-11-12T10:00:00.000000Z"
DJI_META="-movflags use_metadata_tags -metadata make=DJI -metadata model=Osmo_Action_5_Pro -metadata creation_time=2026-11-12T10:00:00.000000Z"
TC="-timecode 10:00:00:00"

rm -rf "$OUT"
mkdir -p "$OUT/giro00/raw/sony" "$OUT/giro00/raw/dji" "$OUT/giro00/raw/phone"
SONY="$OUT/giro00/raw/sony"
DJI="$OUT/giro00/raw/dji"
PHONE="$OUT/giro00/raw/phone"

# Sony-style sidecar next to the first clip (read by the sidecar parser later).
cat >"$SONY/C0001M01.XML" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<NonRealTimeMeta xmlns="urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.20" lastUpdate="2026-11-12T12:00:00+00:00">
  <Device manufacturer="Sony" modelName="ILME-FX30" serialNumber="FIXTURE"/>
  <CreationDate value="2026-11-12T12:00:00+00:00"/>
</NonRealTimeMeta>
XML

# Sony, 540p 25p, 4 s, timecode, stereo.
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -f lavfi -i "sine=frequency=440:sample_rate=48000" \
  -t 4 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $TC $SONY_META \
  "$SONY/C0001.MP4"

# Sony, 50p (intended slow motion only, R70), 2 s.
$FF -f lavfi -i testsrc2=size=960x540:rate=50 -f lavfi -i "sine=frequency=330:sample_rate=48000" \
  -t 2 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $TC $SONY_META \
  "$SONY/C0002.MP4"

# Sony, clipped audio: peaks above full scale in the first second, then normal level.
$FF -f lavfi -i testsrc2=size=960x540:rate=25 \
  -f lavfi -i "aevalsrc=if(lt(t\,1)\,clip(4*sin(2*PI*440*t)\,-1\,1)\,0.5*sin(2*PI*440*t)):s=48000:d=2:c=stereo" \
  -t 2 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $TC $SONY_META \
  "$SONY/C0003.MP4"

# Camera A of a known pair: clap at 1.00 s, 3 s long.
CLAP_A="aevalsrc=if(between(t\,1.00\,1.02)\,0.9*sin(2*PI*1500*t)\,0.05*sin(2*PI*220*t)):s=48000:d=3:c=stereo"
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -f lavfi -i "$CLAP_A" \
  -t 3 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $TC $SONY_META \
  "$SONY/C0004.MP4"

# HLG (arib-std-b67), 10-bit HEVC, 2 s: a log/HDR transfer the ingest flags (R69).
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -t 2 -c:v libx265 -pix_fmt yuv420p10le -crf 30 \
  -x265-params "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc" \
  -metadata creation_time=2026-11-12T10:00:00.000000Z "$SONY/C0005.MP4"

# 4K HEVC, 2 s (the one 4K clip; R64, R69).
$FF -f lavfi -i testsrc2=size=3840x2160:rate=25 -t 2 -c:v libx265 -preset ultrafast -pix_fmt yuv420p \
  -crf 38 -x265-params "log-level=error" -metadata creation_time=2026-11-12T10:00:00.000000Z "$SONY/C0007.MP4"

# DJI-like: 25p, 4 s, with a low-res proxy (.LRF) and a 48 kHz stereo WAV (the mic).
DJI_BASE="DJI_20261112120000_0001_D"
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -f lavfi -i "sine=frequency=880:sample_rate=48000" \
  -t 4 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $DJI_META \
  "$DJI/$DJI_BASE.MP4"
$FF -f lavfi -i testsrc2=size=480x270:rate=25 -t 4 -c:v libx264 -pix_fmt yuv420p -crf 40 -f mp4 \
  "$DJI/$DJI_BASE.LRF"
$FF -f lavfi -i "sine=frequency=880:sample_rate=48000" -t 4 -ac 2 -c:a pcm_s16le -f wav \
  "$DJI/$DJI_BASE.WAV"

# Camera B of the known pair: clap at 2.25 s, 3 s long.
CLAP_B="aevalsrc=if(between(t\,2.25\,2.27)\,0.9*sin(2*PI*1500*t)\,0.05*sin(2*PI*220*t)):s=48000:d=3:c=stereo"
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -f lavfi -i "$CLAP_B" \
  -t 3 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 35 -c:a aac -ac 2 $DJI_META \
  "$DJI/DJI_20261112120000_0005_D.MP4"

# Phone-like variable frame rate: most frames 25 fps, then a slower stretch (R69).
$FF -f lavfi -i testsrc2=size=960x540:rate=25 -t 2 \
  -vf "setpts='if(lt(N\,25)\,N/25\,1+(N-25)/10)/TB'" -fps_mode vfr \
  -c:v libx264 -pix_fmt yuv420p -crf 35 -movflags use_metadata_tags -metadata make=Apple -metadata creation_time=2026-11-12T10:00:00.000000Z \
  -metadata model=iPhone -f mov "$PHONE/VFR_0006.MOV"

for file in "$OUT"/giro00/raw/*/*; do
  size=$(wc -c <"$file")
  if [ "$size" -ge 5000000 ]; then
    echo "fixture too large (5 MB limit): $file" >&2
    exit 1
  fi
done
echo "fixtures written to $OUT"
