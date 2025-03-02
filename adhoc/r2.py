import s3fs
from dotenv import dotenv_values

c = dotenv_values(".env")

s3 = s3fs.S3FileSystem(
    endpoint_url="https://18fee802749992d5fac53a9656f63cd5.r2.cloudflarestorage.com",
    key=c["cf_key"],
    secret=c["cf_secret"],
)

print(s3.ls("notedwin"))

# copy over docker volumes
# postgres backup latest keep 2
