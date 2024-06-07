#!/bin/bash

TARGET_DIR=$1

pushd $TARGET_DIR
for file in $(ls);do
    if [ -h $file ]; then
        # replace link with model
        echo "Replacing softlink for file $file"
        cp --remove-destination `readlink $file` $file
    fi
done
popd