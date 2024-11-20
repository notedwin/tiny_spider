from fabric import Connection


def backup_openwrt():
    conn = Connection(
        host="192.168.0.1",
        user="root",
        connect_kwargs={
            "key_filename": "/Users/edwinzamudio/.ssh/id_rsa",
        },
    )
    r = conn.run("uname -s", hide=True)  # run
    # r.put("myfiles.tgz", remote="/opt/mydata/")
    print(f"Ran {r.command} on {conn.host}, got stdout:\n{r.stdout}")


# sysupgrade -b /tmp/backup-${HOSTNAME}-$(date +%F).tar.gz
# ls /tmp/backup-*.tar.gz

# # From the client, download backup
# scp root@openwrt.lan:/tmp/backup-*.tar.gz .
# # On recent clients, it may be necessary to use the -O flag for compatibility reasons
# scp -O root@openwrt.lan:/tmp/backup-*.tar.gz .

if __name__ == "__main__":
    backup_openwrt()
