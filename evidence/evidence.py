import os
import plistlib
import subprocess

if __name__ == "__main__":
    loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "evid.sh")
    s = 60 * 60 * 12  # 12 hours
    d = {
        "Label": "io.evidence",
        "ProgramArguments": [loc],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StartOnMount": True,
        "StartInterval": s,
        "ThrottleInterval": s,
        # https://apple.stackexchange.com/questions/435496/launchd-service-logs
        "StandardErrorPath": "/tmp/ev.err",
        "StandardOutPath": "/tmp/ev.out",
    }
    file_ = os.path.join("/Users/edwinzamudio/Library/LaunchAgents/io.evidence.plist")
    print(f"Creating PLIST file {file_}")
    with open(file_, "wb+") as fp:
        plistlib.dump(d, fp)

    print("Loading job")
    command = f"launchctl unload -w {file_}"
    subprocess.run(command, shell=True)
    command = f"launchctl load -w {file_}"
    subprocess.run(command, shell=True)
