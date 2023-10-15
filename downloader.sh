# bash -c 'curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/downloader.sh && chmod 777 downloader.sh && ./start.sh'

curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/pre-start.sh && chmod 777 pre-start.sh
curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/post-start.sh && chmod 777 post-start.sh 
curl -O -L https://raw.githubusercontent.com/lenslessai/start-model-creator-pod/main/start.sh && chmod 777 start.sh 
./start.sh

