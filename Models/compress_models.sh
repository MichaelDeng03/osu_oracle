#!/bin/bash
# Unfortunately, even post-compression, the models are too large to upload to GitHub. 

for dir in */; do
    if [[ $dir == w2v_model*/ ]]; then
        # Remove the trailing slash from directory name
        dir_name=${dir%/}

        # Compress the directory into a tar.gz file
        tar -cf - "$dir_name" | gzip -9 > "${dir_name}.tar.gz"

        echo "Compressed $dir_name"
    fi
done
