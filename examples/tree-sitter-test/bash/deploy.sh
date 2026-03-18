#!/bin/bash

function log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

function log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

function check_dependencies() {
    for cmd in git docker kubectl; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd is not installed"
            return 1
        fi
    done
    log_info "All dependencies found"
}

function build_image() {
    local tag="$1"
    log_info "Building Docker image: $tag"
    docker build -t "$tag" . || {
        log_error "Build failed"
        return 1
    }
}

function push_image() {
    local tag="$1"
    log_info "Pushing image: $tag"
    docker push "$tag"
}

function deploy() {
    local environment="$1"
    local tag="$2"
    log_info "Deploying $tag to $environment"
    kubectl set image "deployment/app" "app=$tag" --namespace="$environment"
    kubectl rollout status "deployment/app" --namespace="$environment"
}

function rollback() {
    local environment="$1"
    log_info "Rolling back deployment in $environment"
    kubectl rollout undo "deployment/app" --namespace="$environment"
}

function main() {
    check_dependencies || exit 1
    local tag="app:$(git rev-parse --short HEAD)"
    build_image "$tag" || exit 1
    push_image "$tag" || exit 1
    deploy "${1:-staging}" "$tag"
}

main "$@"
