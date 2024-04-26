#!/bin/bash

DATA_DIR="$(pwd)/data"

function install_cli() {
    curl https://us-apt.pkg.dev/doc/repo-signing-key.gpg | sudo apt-key add -
    sudo apt update
    echo "deb https://us-apt.pkg.dev/projects/alloydb-omni alloydb-omni-apt main" \
    | sudo tee -a /etc/apt/sources.list.d/artifact-registry.list
    sudo apt update
    sudo apt-get -y install alloydb-cli
}

function install_alloy() {
    sudo rm -f /var/alloydb/config/dataplane.conf
    sudo mount --make-shared /
    mkdir -p data
    sops -d service-account.json.enc > data/service-account.json
    sudo alloydb database-server install \
        --data-dir="${DATA_DIR}/alloydata" \
        --enable-alloydb-ai=true \
        --private-key-file-path="${DATA_DIR}/service-account.json" \
        --vertex-ai-region="asia-southeast1"
    docker stop ml-agent memory-agent pg-service
    sudo cp pg_hba.conf /var/alloydb/config/pg_hba.conf
}

alloydb || install_cli

docker start ml-agent memory-agent pg-service || install_alloy
docker start ml-agent memory-agent pg-service
