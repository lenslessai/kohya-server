# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/downloader.sh && chmod 777 downloader.sh && ./downloader.sh &&./start.sh'

# serverless
# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/downloader.sh && chmod 777 downloader.sh && ./downloader.sh &&./pre_stsart.sh && python ./rp_handler.py'

#curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/pre_start.sh && chmod 777 pre_start.sh
#curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/post_start.sh && chmod 777 post_start.sh 
#curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/start.sh && chmod 777 start.sh 
#curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/rp_handler.py
curl -o pre_start.sh -C - -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/pre_start.sh
curl -o rp_handler.py -C - -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/rp_handler.py
