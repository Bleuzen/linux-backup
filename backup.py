#!/usr/bin/python3

import shlex
import os
import subprocess
import time


def main():
    input_dirs: list[str] = []
    excludes: list[str] = []
    target_dir: str = ""

    with open("backup.conf") as f:
        for line in f.read().splitlines():
            if len(line) > 0:
                if line[0] == "+":
                    input_dirs.append(line[1:].strip())
                elif line[0] == "-":
                    excludes.append(line[1:].strip())
                elif line[0] == ">":
                    target_dir = line[1:].strip()

    if len(input_dirs) == 0 or len(excludes) == 0 or len(target_dir) == 0:
        print("ERROR: Invalid config. It needs to include at least one input directory, exclude and the target directory!")
        return

    if not os.path.exists(target_dir):
        print("ERROR: Target directory \n>> " + target_dir +
              " <<\nis not available!")
        return

    subprocess.run(generate_command(
        input_dirs, excludes, target_dir, False), shell=True, check=True)


def generate_command(input_dirs: list[str], excludes: list[str], target_dir: str, multi_snapshots: bool):
    includes: list[str] = []
    parent_includes: list[str] = []

    if target_dir[-1] != "/":
        target_dir += "/"

    for dir in input_dirs:
        if dir[-1] != "/":
            dir += "/"
        includes.append(dir)
        parts = list(filter(None, dir.split('/')))
        for x in range(len(parts)):
            path = '/'.join(parts[:x])
            if len(path) > 0:
                path = f"/{path}/"
                if not path in parent_includes:
                    parent_includes.append(path)

    rsync_options = []
    rsync_options.append("--archive")
    rsync_options.append("--verbose")
    rsync_options.append("--progress")
    rsync_options.append("--human-readable")
    rsync_options.append("--delete")
    rsync_options.append("--delete-excluded")
    rsync_options.append("--protect-args")

    if multi_snapshots:
        current_time = int(time.time())

        try:
            latest_backup = max(os.listdir(target_dir))
            rsync_options.append("--link-dest")
            rsync_options.append(shlex.quote(latest_backup))
        except:
            pass

        target_dir += f"{current_time}/"

    return f"rsync {' '.join(rsync_options)} {' '.join([('--include ' + shlex.quote(x)) for x in parent_includes])} {' '.join([('--exclude ' + shlex.quote(x)) for x in excludes])} {' '.join([('--include ' + shlex.quote(x + '***')) for x in includes])} --exclude '*' / {shlex.quote(target_dir)}"


if __name__ == "__main__":
    main()
