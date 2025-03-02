rsync -avz src/ notedwin@spark:/home/notedwin/scheduled
rsync -avz uv.lock pyproject.toml dockerfile .env notedwin@spark:/home/notedwin/scheduled


ssh notedwin@spark "docker ps -q --filter "name=scheduled" | xargs -r docker stop"
ssh notedwin@spark "docker ps -aq --filter "name=scheduled" | xargs -r docker rm"

ssh notedwin@spark "cd /home/notedwin/scheduled && sudo docker build -t scheduled ."
ssh notedwin@spark "sudo docker run -d -v /etc/timezone:/etc/timezone -v /etc/localtime:/etc/localtime --name scheduled scheduled"