#!/bin/bash
#set -e  # Exit the script if any statement returns a non-true return value
# https://github.com/ashleykleynhans/kohya-docker/tree/main
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/pre-start.sh && chmod 777 pre-start.sh && ./start.sh'

# $AWS_SECRET_ACCESS_KEY
# $AWS_ACCESS_KEY
# $BUCKET_MODELS
# $BUCKET_PHOTOS
# $GENERATION_ID

: '
export AWS_SECRET_KEY="mjJshBQYPW49rhOZFgrUrGi4kdpya+G+N83JS1pk"
export AWS_ACCESS_KEY="AKIA5UTHMH6PFNCIQJME"
export BUCKET_MODELS="Hello, World!"
export BUCKET_PHOTOS="lenslessai"
export GENERATION_ID="123"
'

apt-get update && apt install -y awscli
pip install --upgrade 'urllib3<2'
echo "Configure aws"
aws configure set aws_access_key_id $AWS_ACCESS_KEY && aws configure set aws_secret_access_key $AWS_SECRET_KEY && aws configure set region "us-east-1" && aws configure set output "text" 

echo "Download photos from s3"
mkdir -p '/job/input/img/25_ohwx man'
aws s3 sync s3://$BUCKET_PHOTOS/photos/$GENERATION_ID/ '/job/input/img/25_ohwx man'

# regularization images
DOWNLOAD_REG_URL="https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/man_4321_imgs_1024x1024px.zip"
INPUT_REG_DIR="/job/input/reg/1_man"
mkdir -p "$INPUT_REG_DIR"
wget "$DOWNLOAD_REG_URL" -P "$INPUT_REG_DIR"
unzip -j "$INPUT_REG_DIR/man_4321_imgs_1024x1024px.zip" -d "$INPUT_REG_DIR"
rm "$INPUT_REG_DIR/man_4321_imgs_1024x1024px.zip"


cd /kohya_ss
mkdir -p /output/model
mkdir -p /output/logs

source venv/bin/activate

: 'accelerate launch \
    --num_cpu_threads_per_process=2 \
    "./sdxl_train_network.py" \
    --pretrained_model_name_or_path="/sd-models/sd_xl_base_1.0.safetensors" \
    --train_data_dir="/job/input/img" \
    --reg_data_dir="/job/input/reg" \
    --resolution="1024,1024" \
    --output_dir="/output/model" \
    --logging_dir="/job/output/logs" \
    --network_alpha="1" \
    --save_model_as=safetensors \
    --network_module=networks.lora \
    --text_encoder_lr=0.0004 \
    --unet_lr=0.0004 \
    --network_dim=32 \
    --output_name="runpod_model" \
    --lr_scheduler_num_cycles="8" \
    --no_half_vae \
    --learning_rate="0.0004" \
    --lr_scheduler="constant" \
    --train_batch_size="1" \
    --max_train_steps="6800" \
    --save_every_n_epochs="1" \
    --mixed_precision="bf16" \
    --save_precision="bf16" \
    --cache_latents \
    --cache_latents_to_disk \
    --optimizer_type="Adafactor" \
    --optimizer_args scale_parameter=False relative_step=False warmup_init=False \
    --max_data_loader_n_workers="0" \
    --bucket_reso_steps=64 \
    --gradient_checkpointing \
    --xformers \
    --bucket_no_upscale \
    --noise_offset=0.0
'