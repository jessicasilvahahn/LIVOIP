path=$1
path_container=$2
docker_image=$3
name=$4

docker run -it --name=$name -v $path:$path_container:rw $docker_image bash