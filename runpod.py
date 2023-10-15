import subprocess

command = [
    "accelerate", "launch",
    "--num_cpu_threads_per_process=2",
    "./sdxl_train_network.py",
    "--pretrained_model_name_or_path=/sd-models/sd_xl_base_1.0.safetensors1111",
    "--train_data_dir=/job/input/img",
    "--reg_data_dir=/job/input/reg",
    "--resolution=1024,1024",
    "--output_dir=/output/model",
    "--logging_dir=/job/output/logs",
    "--network_alpha=1",
    "--save_model_as=safetensors",
    "--network_module=networks.lora",
    "--text_encoder_lr=0.0004",
    "--unet_lr=0.0004",
    "--network_dim=32",
    "--output_name=runpod_model",
    "--lr_scheduler_num_cycles=8",
    "--no_half_vae",
    "--learning_rate=0.0004",
    "--lr_scheduler=constant",
    "--train_batch_size=1",
    "--max_train_steps=6800",
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

log_file = "accelerate_launch.log"

with open(log_file, "w") as log:
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Read and write the output to the log file
        for line in process.stdout:
            log.write(line)
            print(line, end="")

        # Wait for the process to complete
        process.wait()

        if process.returncode == 0:
            print("Command executed successfully")
        else:
            print("Command failed with return code:", process.returncode)
    except Exception as e:
        print("An error occurred:", str(e))
