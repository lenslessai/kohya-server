#!/usr/bin/env bash
export PYTHONUNBUFFERED=1

echo "Container is running"

# Sync Kohya_ss to workspace to support Network volumes
echo "No Syncing Kohya_ss to workspace, please wait..."

# Link model
ln -s /sd-models/sd_xl_base_1.0.safetensors /workspace/sd_xl_base_1.0.safetensors

# Configure accelerate
echo "Configuring accelerate..."
mkdir -p /root/.cache/huggingface/accelerate
mv /accelerate.yaml /root/.cache/huggingface/accelerate/default_config.yaml

if [[ ${DISABLE_AUTOLAUNCH} ]]
then
    echo "Auto launching is disabled so the application will not be started automatically"
    echo "You can launch them it using the launcher script:"
    echo ""
    echo "   cd /workspace/kohya_ss"
    echo "   source /workspace/kohya_ss/venv/bin/activate"
    echo "   ./gui.sh --listen 0.0.0.0 --server_port 3001 --headless"
else
    echo "Starting Kohya_ss Web UI"
    mkdir -p /logs
    cd /kohya_ss
    source venv/bin/activate
    nohup ./gui.sh --listen 0.0.0.0 --server_port 3001 --headless > /logs/kohya_ss.log 2>&1 &
    echo "Kohya_ss started"
    echo "Log file: /logs/kohya_ss.log"
fi

echo "All services have been started"