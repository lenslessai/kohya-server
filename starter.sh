#!/usr/bin/env bash
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/downloader.sh && chmod 777 downloader.sh && ./downloader.sh &&./start.sh'

# serverless
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/starter.sh && chmod 777 starter.sh && ./starter.sh

export PYTHONUNBUFFERED=1
echo "Container is running"

curl https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/rp_handler.py > rp_handler.py 

# Configure accelerate
echo "Configuring accelerate..."
mkdir -p /root/.cache/huggingface/accelerate
mv /accelerate.yaml /root/.cache/huggingface/accelerate/default_config.yaml

source /kohya_ss/venv/bin/activate
python rp_handler.py 