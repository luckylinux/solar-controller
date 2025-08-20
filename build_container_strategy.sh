#!/bin/bash

# Determine toolpath if not set already
relativepath="./" # Define relative path to go from this script to the root level of the tool
if [[ ! -v toolpath ]]; then scriptpath=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ); toolpath=$(realpath --canonicalize-missing ${scriptpath}/${relativepath}); fi

# Load Configuration
libpath=$(readlink --canonicalize-missing "${toolpath}/includes")
source ${libpath}/functions.sh

# Optional argument
engine=${1-"podman"}

# Check if Engine Exists
engine_exists "${engine}"
if [[ $? -ne 0 ]]
then
    # Error
    echo "[CRITICAL] Neither Podman nor Docker could be found and/or the specified Engine <$engine> was not valid."
    echo "ABORTING !"
    exit 9
fi

# Run a Local Registry WITHOUT Persistent Data Storage
# run_local_registry "${engine}"

# Image Name
name="solar-strategy"

# Options
opts=()

# Use --no-cache when e.g. updating docker-entrypoint.sh and images don't get updated as they should
#opts+=("--no-cache")

# Podman 5.x with Pasta doesn't handle Networking Correctly
# Force to use slirp4netns
opts+=("--network=slirp4netns")

# Add Capacilities
opts+=("--cap-add")
opts+=("LINUX_IMMUTABLE")

# NOT WORKING
#opts+=("--log-level=debug")
#opts+=("--network=host")
#opts+=("--dns=192.168.1.3")
#opts+=("--network=pasta:--ipv4-only,--dns-forward,192.168.1.3,--dns,192.168.1.3,--dhcp-dns,--search,none")
#opts+=("--network=pasta:--ipv4-only,--dns-forward,192.168.1.3,--dns,192.168.1.3,-a,192.168.8.26,-n,20,-g,192.168.1.1")
#opts+=("--network=pasta:-a,192.168.8.26,-n,20,-g,192.168.1.1")
#opts+=("--network=pasta:--ipv6-only,-t,2XXX:XXXX:XXXX:X::X:XX/80")
#opts+=("--network=pasta")

# Base Image
# "Alpine" or "Debian"
bases=()
#bases+=("Alpine")
bases+=("Debian")

# Mandatory Tag
#tag=$(cat ./tag.txt)
tag=$(date +%Y%m%d)

# General Tag
general_tag="latest"

# Select Platform
# Not used for now
#platform="linux/amd64"
#platform="linux/arm64/v8"

# Iterate over Image Base
for base in "${bases[@]}"
do
    # Select Dockerfile
    buildfile="Dockerfile-Strategy-${base}"

    # Create Cache Directory
    mkdir -p cache/${base,,}

    # Check if they are set
    if [[ ! -v name ]] || [[ ! -v tag ]]
    then
       echo "Both Container Name and Tag Must be Set" !
    fi

    # Define Tags to attach to this image
    imagetags=()
    imagetags+=("${name}:${base,,}-${tag}")
    imagetags+=("${name}:${base,,}-${general_tag}")

    # Copy requirements into the build context
    # cp <myfolder> . -r docker build . -t  project:latest

    # For each image tag
    tagargs=()
    images=""
    for imagetag in "${imagetags[@]}"
    do
       # Echo
       echo "Processing Image Tag <${imagetag}> for Container Image <${name}>"

       # Check if Image with the same Name already exists
       remove_image_already_present "${imagetag}" "${engine}"

       # Add Argument to tag this Image too when running Container Build Command
       tagargs+=("-t")
       tagargs+=("${imagetag}")

       # Automatically Populate list of Images to be uploaded to Local Registry
       if [[ -z "${images}" ]]
       then
           images="${imagetag}"
       else
           images="${images},${imagetag}"
       fi
    done

    # Build Container Image
    ${engine} build ${opts[*]} ${tagargs[*]} -f ${buildfile} .

    # Upload to local Registry
    #source ./upload.sh "${images}"
done
