#!/usr/bin/env bash
# Re-render the appendix figures from the Overleaf sources into images/appendix/*.webp
#
#   tools/render_appendix_figs.sh              # re-render every appendix figure
#   tools/render_appendix_figs.sh task_range   # ...or only the named one(s)
#
# Browsers cannot show a PDF inside <img> (Safari is the lone exception), so each
# figure is rasterised to a 2400px-wide WebP (~2x the text column, retina-sharp).
# Needs:  brew install mupdf-tools webp
set -euo pipefail

cd "$(dirname "$0")/.."
SRC=paper_overleaf/images        # Overleaf figure folder (git-ignored)
OUT=images/appendix
WIDTH=2400
QUALITY=90

# Source files behind Figs. 5-12, in the order they appear in the appendix.
FIGS=(
	before_after_opt.pdf
	hand_occlusion.pdf
	refinement_baseline_weird_behaviour.pdf
	sim_to_real_result_per_task.png
	task_range.pdf
	baseline_failure.pdf
	obstacle_recons.pdf
	MP_result.pdf
)

mkdir -p "$OUT"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

for fig in "${FIGS[@]}"; do
	name=${fig%.*}
	if [ $# -gt 0 ] && [[ " $* " != *" $name "* ]]; then continue; fi

	if [[ $fig == *.pdf ]]; then
		# 400 dpi is wider than $WIDTH for every figure, so cwebp only ever downscales.
		mutool draw -q -r 400 -o "$tmp/$name.png" "$SRC/$fig" 1
	else
		cp "$SRC/$fig" "$tmp/$name.png"
	fi

	# Flatten any transparency onto white so the image also reads well when opened on its own.
	cwebp -quiet -q "$QUALITY" -m 6 -blend_alpha 0xffffff -noalpha \
		-resize "$WIDTH" 0 "$tmp/$name.png" -o "$OUT/$name.webp"
	echo "$OUT/$name.webp  $(( $(stat -f%z "$OUT/$name.webp") / 1024 )) KB"
done
