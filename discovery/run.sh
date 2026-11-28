#!/usr/bin/env bash
mkdir -p discovery/out/h
for u in "https://web.archive.org/web/2025id_/https://www.hcf.com.au/content/dam/hcf/images/placeholder/logo_hcf1.png" "https://web.archive.org/web/2025id_/https://www.hcf.com.au/etc.clientlibs/hcf-digital/clientlibs-assets/resources/img/icons/logo_hcf-footer.png"; do
  n=$(basename "$u"); curl -s -L -f -A "Mozilla/5.0" "$u" -o "discovery/out/h/$n" && echo "GOT $n $(stat -c%s discovery/out/h/$n)"
done
