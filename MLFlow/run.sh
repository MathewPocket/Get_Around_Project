docker build . -t getaroundmlflow

docker run -it\
 -v "$(pwd):/home/app"\
 -p 4002:4002\
 -e PORT=4002\
 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID\
 -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY\
 -e BACKEND_STORE_URI=$BACKEND_STORE_URI\
 -e ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI\
 getaroundmlflow