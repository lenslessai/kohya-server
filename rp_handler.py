import time
import os
import runpod
import requests
import boto3
import subprocess
import zipfile

# "--max_train_steps=6800",
command = [
    "accelerate", "launch",
    "--num_cpu_threads_per_process=2",
    "./kohya_ss/sdxl_train_network.py",
    "--pretrained_model_name_or_path=/sd-models/sd_xl_base_1.0.safetensors",
    "--train_data_dir=/job/input/img",
    "--reg_data_dir=/job/input/reg",
    "--resolution=1024,1024",
    "--output_dir=/job/output/model",
    "--logging_dir=/job/output/logs",
    "--network_alpha=1",
    "--save_model_as=safetensors",
    "--network_module=networks.lora",
    "--text_encoder_lr=0.0004",
    "--unet_lr=0.0004",
    "--network_dim=32",
    #"--output_name=runpod_model",
    #"--lr_scheduler_num_cycles=8", #epoch
    "--no_half_vae",
    "--learning_rate=0.0004",
    "--lr_scheduler=constant",
    "--train_batch_size=1",
    #"--max_train_steps=80",
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

def downloadImages(images_id, steps_per_image):
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
    bucket_name = os.environ.get('BUCKET_PHOTOS')
    region = 'us-east-1'

    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not found in environment variables.")

    if bucket_name is None:
        raise ValueError("S3 bucket name not found in environment variables.")

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )

    s3 = session.client('s3')
    local_directory = '/job/input/img/'+steps_per_image+'_ohwx man'
    os.makedirs(local_directory, exist_ok=True)
    bucket_path = f"photos/{images_id}/"
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=bucket_path)
    downloaded_count = 0
    for obj in objects.get('Contents', []):
        object_key = obj['Key']
        if object_key == bucket_path:
            continue
        local_file_path = os.path.join(local_directory, os.path.basename(object_key))
        s3.download_file(bucket_name, object_key, local_file_path)
        downloaded_count += 1

    list_directory_files(local_directory)
    print("Download photos from S3 complete")
    return downloaded_count

def uploadToS3(to_upload_path, s3_target_path):
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
    bucket_name = os.environ.get('BUCKET_PHOTOS')
    region = 'us-east-1'

    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not found in environment variables.")

    if bucket_name is None:
        raise ValueError("S3 bucket name not found in environment variables.")

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )

    s3 = session.client('s3')
    for root, dirs, files in os.walk(to_upload_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_object_key = os.path.join(s3_target_path, os.path.relpath(local_file_path, to_upload_path))

            # Upload the file to S3
            s3.upload_file(local_file_path, bucket_name, s3_object_key)

            print(f'{local_file_path} has been uploaded to {bucket_name}/{s3_object_key}')

 

def download_and_process_reg_images(url, target_directory):
    print("starting to download reg images")
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    file_name = os.path.join(target_directory, os.path.basename(url))

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Reg images file downloaded to {file_name}")

        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(target_directory)
        print("Reg images file unzipped")
        os.remove(file_name)
        os.rename(target_directory+"/man_4321_imgs_1024x1024px", target_directory+"/1_man")
        count_directory_files(target_directory+"/1_man")

        print("Downloaded Reg images file removed")
    else:
        raise ValueError(f"Failed to download reg images. Status code: {response.status_code}")


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
                runpod.serverless.progress_update(event, f"Progress {update_number}/8")

            process.wait()

            if process.returncode == 0:
                print("Command executed successfully")
            else:
                raise Exception("accelerate command failed with return code: " + process.returncode)


def add_parameter_to_command(command, steps_per_image, epochs, image_amount, model_name):
    command.append("--lr_scheduler_num_cycles="+epochs)
    command.append("--max_train_steps="+str(int(steps_per_image)*int(epochs)*int(image_amount)*2))
    command.append("--output_name="+model_name)



def run_inference(event):
    '''
    Run inference on a request.
    '''
    user_id = event["input"]["user_id"]
    steps_per_image = event["input"]["steps_per_image"]
    epochs = event["input"]["epochs"]
    images_id = event["input"]["images_id"]
    model_name =  event["input"]["model_name"]

    download_reg_imgs_url = "https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/man_4321_imgs_1024x1024px.zip"
    reg_imgs_target_directory = "/job/input/reg"

    image_amount = downloadImages(images_id, steps_per_image)
    download_and_process_reg_images(download_reg_imgs_url, reg_imgs_target_directory)
    add_parameter_to_command(command, steps_per_image, epochs, image_amount, model_name)
    execute_command_and_log_output(event, command)
    runpod.serverless.progress_update(event, f"Progress 8/8")
    uploadToS3("/job/output/model", "models/"+user_id)

    return "{}"


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event)

    return {"refresh_worker": True, "job_results": json}


if __name__ == "__main__":
    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
