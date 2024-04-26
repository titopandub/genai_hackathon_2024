#!/bin/bash

curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
"https://discoveryengine.googleapis.com/v1alpha/projects/328583281153/locations/global/collections/default_collection/dataStores/film-metadata-2024-03-19_1710826473633/servingConfigs/default_search:search" \
-d '{"query":"ratu adil","pageSize":10,"queryExpansionSpec":{"condition":"AUTO"},"spellCorrectionSpec":{"mode":"AUTO"}}'
