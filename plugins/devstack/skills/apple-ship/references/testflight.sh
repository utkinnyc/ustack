#!/usr/bin/env bash
# Archive the apps and upload them to TestFlight. Run from the folder with project.yml:
#   scripts/testflight.sh                 # all schemes
#   scripts/testflight.sh App AppTV       # just these
# Needs: Xcode signed in to the paid team, and the App Store Connect record (with tvOS added).
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT=App.xcodeproj                      # <- your project
ALL=(App AppTV)                            # <- your schemes (the Watch app is embedded in App)
TEAM_ID="$(grep -m1 -E '^\s*DEVELOPMENT_TEAM:' project.yml | awk '{print $2}')"

if (($#)); then schemes=("$@"); else schemes=("${ALL[@]}"); fi
build="$(date +%Y%m%d%H%M)"                # every upload needs a new, higher build number
out="build/testflight-$build"              # add /build/ to .gitignore
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

xcodegen -q
for s in "${schemes[@]}"; do
  case "$s" in
    App)      platform=iOS;     sign=() ;;
    # No Apple TV registered for development signing: archive unsigned; export signs for App Store.
    AppTV)    platform=tvOS;    sign=(CODE_SIGNING_ALLOWED=NO) ;;
    *) echo "unknown scheme $s" >&2; exit 1 ;;
  esac
  echo "==> $s (build $build)"
  xcodebuild archive -project "$PROJECT" -scheme "$s" -configuration Release \
    -destination "generic/platform=$platform" -archivePath "$out/$s.xcarchive" \
    CURRENT_PROJECT_VERSION="$build" ${sign[@]+"${sign[@]}"} \
    -allowProvisioningUpdates -skipPackagePluginValidation -skipMacroValidation -quiet
  ls "$out/$s.xcarchive/Products/Applications/"*.app >/dev/null \
    || { echo "archive for $s has no app (check SKIP_INSTALL)" >&2; exit 1; }
  [[ $s != App ]] || ls -d "$out/$s.xcarchive/Products/Applications/"*.app/Watch/*.app >/dev/null \
    || { echo "iPhone archive has no embedded Watch app" >&2; exit 1; }
  xcodebuild -exportArchive -archivePath "$out/$s.xcarchive" \
    -exportOptionsPlist "$out/export.plist" -exportPath "$out/$s" -allowProvisioningUpdates
done
echo "Uploaded. Builds appear in App Store Connect > TestFlight after ~10-30 min of processing."
