rsync -avz src/ notedwin@spark:/home/notedwin/scheduled
rsync -avz uv.lock pyproject.toml dockerfile notedwin@spark:/home/notedwin/scheduled

ssh notedwin@spark "cd /home/notedwin/scheduled && sudo docker build -t scheduled ."

ssh notedwin@spark "sudo docker run -d --name scheduled scheduled"