#!/usr/bin/env bash
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/downloader.sh && chmod 777 downloader.sh && ./downloader.sh &&./start.sh'

# serverless
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/starter.sh && chmod 777 starter.sh && ./starter.sh

export PYTHONUNBUFFERED=1
echo "Container is running"

curl https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/rp_handler.py > rp_handler.py 
ls -la /
cat /accelerate.yaml
# Configure accelerate
echo "Configuring accelerate..."
mkdir -p /root/.cache/huggingface/accelerate
mv /accelerate.yaml /root/.cache/huggingface/accelerate/default_config.yaml

echo "configuring cuda libs"
apt update && apt install -y libcudnn8=8.9.5.29-1+cuda11.8 libcudnn8-dev=8.9.5.29-1+cuda11.8

source /kohya_ss/venv/bin/activate
python rp_handler.py 