#!/bin/bash

# Release script for Anniversaries Home Assistant custom component
# Usage: ./release.sh [version]
# Example: ./release.sh 1.2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_DIR="$SCRIPT_DIR/custom_components/anniversaries"
CONST_FILE="$COMPONENT_DIR/const.py"
OUTPUT_DIR="$SCRIPT_DIR/dist"

# Get current version from const.py
get_current_version() {
    sed -n 's/.*VERSION = "\([^"]*\)".*/\1/p' "$CONST_FILE"
}

# Validate semantic version format (allows optional pre-release suffix like -beta, b, -rc1, etc.)
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9._-]*$ ]]; then
        echo -e "${RED}Error: Invalid version format. Use semantic versioning (e.g., 1.2.0 or 1.2.0b)${NC}"
        exit 1
    fi
}

# Update version in const.py
update_const_version() {
    local version=$1
    sed -i.bak "s/VERSION = \".*\"/VERSION = \"$version\"/" "$CONST_FILE"
    rm -f "$CONST_FILE.bak"
    echo -e "${GREEN}Updated const.py version to $version${NC}"
}

# Update version in manifest.json
update_manifest_version() {
    local version=$1
    local manifest_file="$COMPONENT_DIR/manifest.json"
    sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$version\"/" "$manifest_file"
    rm -f "$manifest_file.bak"
    echo -e "${GREEN}Updated manifest.json version to $version${NC}"
}

# Create the release zip file
create_zip() {
    local version=$1
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Zip file name
    local zip_file="$OUTPUT_DIR/anniversaries.zip"
    local versioned_zip="$OUTPUT_DIR/anniversaries-$version.zip"
    
    # Remove old zip files
    rm -f "$zip_file" "$versioned_zip"
    
    # Verify component directory exists
    if [[ ! -d "$COMPONENT_DIR" ]]; then
        echo -e "${RED}Error: Component directory not found: $COMPONENT_DIR${NC}"
        exit 1
    fi
    
    # Create zip from component directory
    cd "$COMPONENT_DIR"
    zip -r "$zip_file" . -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x "*.bak"
    
    cd "$SCRIPT_DIR"
    
    # Verify zip was created successfully
    if [[ ! -f "$zip_file" ]]; then
        echo -e "${RED}Error: Failed to create zip file: $zip_file${NC}"
        exit 1
    fi
    
    # Check zip file is not empty
    local zip_size=$(stat -f%z "$zip_file" 2>/dev/null || stat -c%s "$zip_file" 2>/dev/null)
    if [[ "$zip_size" -lt 1000 ]]; then
        echo -e "${RED}Error: Zip file appears to be empty or too small: $zip_file (${zip_size} bytes)${NC}"
        exit 1
    fi
    
    # Also create a versioned copy
    cp "$zip_file" "$versioned_zip"
    
    echo -e "${GREEN}Created release zip files:${NC}"
    echo "  - $zip_file ($(du -h "$zip_file" | cut -f1))"
    echo "  - $versioned_zip"
}

# Commit changes, create tag, and push
git_operations() {
    local version=$1
    
    echo ""
    
    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo "Committing changes..."
        git add -A
        git commit -m "Release v$version"
        echo -e "${GREEN}Changes committed${NC}"
    else
        echo "No changes to commit"
    fi
    
    # Check if tag already exists
    if git rev-parse "v$version" >/dev/null 2>&1; then
        echo -e "${YELLOW}Tag v$version already exists, skipping tag creation${NC}"
    else
        echo "Creating git tag..."
        git tag -a "v$version" -m "Release v$version"
        echo -e "${GREEN}Created git tag v$version${NC}"
    fi
    
    # Push commits and tag
    echo "Pushing to origin..."
    git push origin HEAD
    git push origin "v$version" 2>/dev/null || echo -e "${YELLOW}Tag already exists on remote${NC}"
    echo -e "${GREEN}Pushed to origin${NC}"
}

# Create GitHub release with zip file
create_github_release() {
    local version=$1
    local zip_file="$OUTPUT_DIR/anniversaries.zip"
    
    echo ""
    
    # Verify zip file exists before attempting upload
    if [[ ! -f "$zip_file" ]]; then
        echo -e "${RED}Error: Zip file not found: $zip_file${NC}"
        echo "Run the script again to create the zip file."
        exit 1
    fi
    
    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}GitHub CLI (gh) not found. Skipping GitHub release creation.${NC}"
        echo "Install it with: brew install gh"
        echo "Then manually create a release at: https://github.com/chaimt/Anniversaries/releases"
        echo "Don't forget to upload: $zip_file"
        return
    fi
    
    # Check if release already exists
    if gh release view "v$version" &>/dev/null; then
        echo -e "${YELLOW}GitHub release v$version already exists${NC}"
        echo "Uploading zip file to existing release..."
        if gh release upload "v$version" "$zip_file" --clobber; then
            echo -e "${GREEN}Successfully uploaded anniversaries.zip${NC}"
        else
            echo -e "${RED}Failed to upload zip file${NC}"
            exit 1
        fi
    else
        echo "Creating GitHub release..."
        if gh release create "v$version" "$zip_file" \
            --title "v$version" \
            --notes "Release v$version"; then
            echo -e "${GREEN}Created GitHub release v$version with anniversaries.zip${NC}"
        else
            echo -e "${RED}Failed to create GitHub release${NC}"
            exit 1
        fi
    fi
    
    # Verify the asset was uploaded
    echo "Verifying release assets..."
    if gh release view "v$version" --json assets -q '.assets[].name' | grep -q "anniversaries.zip"; then
        echo -e "${GREEN}Verified: anniversaries.zip is attached to the release${NC}"
    else
        echo -e "${RED}Warning: anniversaries.zip may not have been uploaded correctly${NC}"
    fi
    
    # Get and display release URL
    local release_url=$(gh release view "v$version" --json url -q .url)
    echo -e "${GREEN}Release URL: $release_url${NC}"
}

# Main script
main() {
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Anniversaries Release Script${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    
    # Get current version
    current_version=$(get_current_version)
    echo -e "Current version: ${GREEN}$current_version${NC}"
    
    # Get new version from argument or prompt
    if [[ -n $1 ]]; then
        new_version=$1
    else
        read -p "Enter new version (or press Enter to keep $current_version): " new_version
        if [[ -z $new_version ]]; then
            new_version=$current_version
        fi
    fi
    
    # Validate version
    validate_version "$new_version"
    
    echo ""
    echo -e "New version: ${GREEN}$new_version${NC}"
    echo ""
    
    # Update version if changed
    if [[ $new_version != $current_version ]]; then
        echo "Updating version numbers..."
        update_const_version "$new_version"
        update_manifest_version "$new_version"
        echo ""
    fi
    
    # Create zip
    echo "Creating release zip..."
    create_zip "$new_version"
    
    # Git operations (commit, tag, push)
    git_operations "$new_version"
    
    # Create GitHub release
    create_github_release "$new_version"
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Release $new_version complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main "$@"
