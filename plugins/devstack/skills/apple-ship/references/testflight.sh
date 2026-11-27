#!/usr/bin/env bash
# Archive Apple apps and upload them to TestFlight. Save as scripts/testflight.sh and run
# from anywhere in the repo:
#   scripts/testflight.sh              # every scheme in SCHEMES
#   scripts/testflight.sh MyApp        # just these
# Needs: Xcode signed in to the paid team, and an App Store Connect record for each bundle ID.
# Works with macOS's built-in bash 3.2.
set -euo pipefail
cd "$(dirname "$0")/.."

# ---- edit these --------------------------------------------------------------------------
PROJECT="MyApp.xcodeproj"      # the .xcodeproj, or leave empty and set WORKSPACE
WORKSPACE=""                   # e.g. MyApp.xcworkspace (CocoaPods, or several projects)
# One entry per scheme: "scheme:platform" or "scheme:platform:unsigned".
# platform is iOS, tvOS, watchOS, macOS or visionOS. "unsigned" archives without signing and
# lets the export sign it for the App Store (use it for a TV app when no Apple TV is
# registered for development).
SCHEMES=(
  "MyApp:iOS"
  # "MyAppTV:tvOS:unsigned"
)
WATCH_IN=""                    # scheme whose archive must contain an embedded Watch app, if any
PRECHECK=""                    # command that must pass before uploading, e.g. "swift test --package-path MyKit"
TEAM_ID="${TEAM_ID:-}"         # read from the project below if not set
# ------------------------------------------------------------------------------------------

if [[ -n $WORKSPACE ]]; then src=(-workspace "$WORKSPACE"); else src=(-project "$PROJECT"); fi

# Regenerate the project if it's defined with XcodeGen.
if [[ -f project.yml ]]; then
  command -v xcodegen >/dev/null || { echo "project.yml found but xcodegen is not installed (brew install xcodegen)" >&2; exit 1; }
  xcodegen -q
fi

if [[ -n $PRECHECK ]]; then
  echo "==> precheck: $PRECHECK"
  bash -c "$PRECHECK"
fi

# Pick the schemes to build: all, or the ones named on the command line.
selected=()
for entry in "${SCHEMES[@]}"; do
  name="${entry%%:*}"
  if (($# == 0)); then selected+=("$entry"); continue; fi
  for want in "$@"; do [[ $want == "$name" ]] && selected+=("$entry"); done
done
((${#selected[@]})) || { echo "no matching scheme; known: ${SCHEMES[*]}" >&2; exit 1; }

if [[ -z $TEAM_ID ]]; then
  first="${selected[0]%%:*}"
  TEAM_ID="$(xcodebuild "${src[@]}" -scheme "$first" -showBuildSettings 2>/dev/null \
    | awk '$1 == "DEVELOPMENT_TEAM" {print $3; exit}')"
fi
[[ -n $TEAM_ID ]] || { echo "no Team ID: set DEVELOPMENT_TEAM in the project, or run with TEAM_ID=..." >&2; exit 1; }

build="$(date +%Y%m%d%H%M)"    # every upload needs a new, higher build number
out="build/testflight-$build"  # add /build/ to .gitignore
mkdir -p "$out"

cat >"$out/export.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>method</key><string>app-store-connect</string>
  <key>destination</key><string>upload</string>
  <key>teamID</key><string>$TEAM_ID</string>
</dict></plist>
EOF

for entry in "${selected[@]}"; do
  IFS=: read -r scheme platform flag <<<"$entry"
  sign=()
  [[ ${flag:-} == unsigned ]] && sign=(CODE_SIGNING_ALLOWED=NO)
  archive="$out/$scheme.xcarchive"

  echo "==> $scheme ($platform, build $build)"
  xcodebuild archive "${src[@]}" -scheme "$scheme" -configuration Release \
    -destination "generic/platform=$platform" -archivePath "$archive" \
    CURRENT_PROJECT_VERSION="$build" ${sign[@]+"${sign[@]}"} \
    -allowProvisioningUpdates -skipPackagePluginValidation -skipMacroValidation -quiet

  # Catch broken archives before Apple does.
  ls -d "$archive/Products/Applications/"*.app >/dev/null 2>&1 \
    || { echo "archive for $scheme has no app (check SKIP_INSTALL on the app target)" >&2; exit 1; }
  if [[ $scheme == "$WATCH_IN" ]]; then
    ls -d "$archive/Products/Applications/"*.app/Watch/*.app >/dev/null 2>&1 \
      || { echo "$scheme archive has no embedded Watch app" >&2; exit 1; }
  fi

  xcodebuild -exportArchive -archivePath "$archive" \
    -exportOptionsPlist "$out/export.plist" -exportPath "$out/$scheme" -allowProvisioningUpdates
done
echo "Uploaded. Builds appear in App Store Connect > TestFlight after ~10-30 min of processing."
