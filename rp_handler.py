import time
import os
import runpod
import requests
import boto3
import subprocess
import zipfile
import sys
from tools import crop_and_resize

command = [
    "accelerate", "launch",
    "--num_cpu_threads_per_process=2",
    "./kohya_ss/sdxl_train_network.py",
    "--pretrained_model_name_or_path=/sd-models/sd_xl_base_1.0.safetensors",
    "--train_data_dir=/job/input/img",
    "--resolution=1024,1024",
    "--output_dir=/job/output/model",
    "--logging_dir=/job/output/logs",
    "--network_alpha=1",
    "--save_model_as=safetensors",
    "--network_module=networks.lora",
    "--text_encoder_lr=0.0004",
    "--unet_lr=0.0004",
    "--network_dim=32",
    "--no_half_vae",
    "--learning_rate=0.0004",
    "--lr_scheduler=constant",
    "--train_batch_size=1",
    "--save_every_n_epochs=1",
    "--mixed_precision=bf16",
    "--save_precision=bf16",
    "--cache_latents",
    "--cache_latents_to_disk",
    "--optimizer_type=Adafactor",
    "--optimizer_args",
    "scale_parameter=False",
    "relative_step=False",
    "warmup_init=False",
    "--max_data_loader_n_workers=0",
    "--bucket_reso_steps=64",
    "--gradient_checkpointing",
    "--xformers",
    "--bucket_no_upscale",
    "--noise_offset=0.0"
]


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #

def getAWSSession():
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
    region = 'us-east-1'

    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not found in environment variables.")

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )
    return session


def list_directory_files(path='.'):
    print("content of " + path +":")    
    try:
      directory_contents = os.listdir(path)
      for item in directory_contents:
        print(item)
    except FileNotFoundError:
        print(f"Directory '{path}' not found.")

def count_directory_files(path='.'):
    print("size of " + path +":")    
    try:
      print(len(os.listdir(path)))
    except FileNotFoundError:
      print(f"Directory '{path}' not found.")

def downloadImagesFromS3(photos_directory, steps_per_image, kind, bucket_name):
    if bucket_name is None:
        raise ValueError("S3 bucket name not found in environment variables.")

    s3 = getAWSSession().client('s3')
    local_directory = ""
    if kind == "man":
      local_directory = '/job/input/img/'+steps_per_image+'_ohwx man'
    elif kind == "woman":
      local_directory = '/job/input/img/'+steps_per_image+'_ohwx woman'
    os.makedirs(local_directory, exist_ok=True)
    bucket_path = f"{photos_directory}/"
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=bucket_path)
    downloaded_count = 0
    for obj in objects.get('Contents', []):
        object_key = obj['Key']
        if object_key == bucket_path:
            continue
        local_file_path = os.path.join(local_directory, os.path.basename(object_key))
        s3.download_file(bucket_name, object_key, local_file_path)
        crop_and_resize(local_file_path, (1024, 1024))
        downloaded_count += 1

    list_directory_files(local_directory)
    print("Download photos from S3 complete")
    return downloaded_count

def uploadFilesToS3(to_upload_path, s3_target_path, bucket_name):
    if bucket_name is None:
        raise ValueError("S3 bucket name not found in environment variables.")

    s3 = getAWSSession().client('s3')
    for root, dirs, files in os.walk(to_upload_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_object_key = os.path.join(s3_target_path, os.path.relpath(local_file_path, to_upload_path))

            # Upload the file to S3
            s3.upload_file(local_file_path, bucket_name, s3_object_key)

            print(f'{local_file_path} has been uploaded to {bucket_name}/{s3_object_key}')

def count_files_with_extension(directory, extension):
    try:
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    count += 1
        return count
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return -1 


def execute_command_and_log_output(event, command, log_file="accelerate_launch.log"):
    print("executing command:")
    print(command)
    with open(log_file, "w") as log:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout:
                log.write(line)
                print(line, end="")
                update_number = count_files_with_extension("/job/output/model", "safetensors")
                #runpod.serverless.progress_update(event, f"Progress {update_number}/8")

            process.wait()

            if process.returncode == 0:
                print("accelerate command executed successfully")
            else:
                raise Exception("accelerate command failed with return code: " + process.returncode)


def add_parameter_to_command(command, steps_per_image, epochs, image_amount, model_name, kind, enable_bucket):
    command.append("--lr_scheduler_num_cycles="+epochs)
    command.append("--max_train_steps="+str(int(steps_per_image)*int(epochs)*int(image_amount)*2))
    command.append("--output_name="+model_name)
    if enable_bucket == "true":
      command.append("--enable_bucket")
    
    if kind == "man":
      command.append("--reg_data_dir=job/input/man/reg")
    elif kind == "woman":
      command.append("--reg_data_dir=/job/input/woman/reg")

def run_inference(event):
    '''
    Run inference on a request.
    '''
    steps_per_image = event["input"]["steps_per_image"]
    epochs = event["input"]["epochs"]
    kind =  event["input"]["kind"]
    enable_bucket = event["input"]["enable_bucket"]
    if kind != "man" and kind != "woman":
        raise Exception("kind is incorrect")
    
    # input
    photos_bucket = event["input"]["photos_bucket"]
    photos_directory = event["input"]["photos_directory"]

    # output
    models_bucket = event["input"]["models_bucket"]
    models_directory = event["input"]["models_directory"] 
    model_name = event["input"]["model_name"]

    image_amount = downloadImagesFromS3(photos_directory, steps_per_image, kind, photos_bucket)
    add_parameter_to_command(command, steps_per_image, epochs, image_amount, model_name, kind, enable_bucket)
    execute_command_and_log_output(event, command)
    uploadFilesToS3("/job/output/model", models_directory, models_bucket)

    return "{}"


def stop_pod(pod_id):
    print("stopping pod with id=" + pod_id)
    stop_pod_command = ["runpodctl", "remove", "pod", pod_id]
    result = subprocess.run(stop_pod_command, check=True)
    if result.returncode == 0:
        print("'runpodctl remove pod' command executed successfully")
        print("Output:\n", result.stdout)
    else:
        print("'runpodctl remove pod' command")
        print("Error message:\n", result.stderr)

# ---------------------------------------------------------------------------- #
#                                Server Handler                                #
# ---------------------------------------------------------------------------- #

def server_handler():
    event = {}
    event["input"] = {}

    # parameters
    event["input"]["steps_per_image"] = os.environ.get('STEPS_PER_IMAGE')
    event["input"]["epochs"] =  os.environ.get('EPOCHS')
    event["input"]["kind"] = os.environ.get('KIND')
    event["input"]["enable_bucket"] = os.environ.get('ENABLE_BUCKET')

    # input
    event["input"]["photos_bucket"] = os.environ.get('PHOTOS_BUCKET')
    event["input"]["photos_directory"] = os.environ.get('PHOTOS_DIRECTORY') # user_hash/photos_hash

    # output
    event["input"]["models_bucket"] = os.environ.get('MODELS_BUCKET')
    event["input"]["models_directory"] = os.environ.get('MODELS_DIRECTORY')
    event["input"]["model_name"] = os.environ.get('MODEL_NAME')


    print("steps_per_image: " + event["input"]["steps_per_image"])
    print("epochs: " + event["input"]["epochs"])
    print("kind: " + event["input"]["kind"])
    print("enable_bucket: " + event["input"]["enable_bucket"])

    print("photos_bucket: " + event["input"]["photos_bucket"])
    print("photos_directory: " + event["input"]["photos_directory"])

    print("models_bucket: " + event["input"]["models_bucket"])
    print("models_directory: " + event["input"]["models_directory"])
    print("model_name: " + event["input"]["model_name"])

    print("RUNPOD_POD_ID: " + os.environ.get('RUNPOD_POD_ID'))

    run_inference(event)
    stop_pod(os.environ.get('RUNPOD_POD_ID'))


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def serverless_handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event)

    return {"refresh_worker": True, "job_results": json}


if __name__ == "__main__":
    print("WebUI API Service is ready. Starting RunPod...")
    if os.environ.get('SERVERLESS') == 'true':
      runpod.serverless.start({"handler": serverless_handler})
    else:
      server_handler()
