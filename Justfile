build:
    docker build \
        --build-arg PIP_INDEX_URL=$(op item get 'Azure DevOps - Feed - Read PAT' --format=json | jq '.fields[] | select(.label=="url").value' -r) \
        --tag kiroshi:latest \
        --platform linux/amd64 \
        .
