from jtop import jtop, JtopException
import os
import csv
import subprocess
import argparse
from typing import Literal, List, Optional
from datetime import datetime
from time import sleep

processes = []

start_time = datetime.now()
datakeys = ["time", "cpu-gpu", "soc", "total", "DLA0", "DLA1", "GPU"]
log = []


def make_command(
    cmd: str = "./lightNet-TRT",
    flagfile: str = "../configs/lightNet-BDD100K-det-semaseg-1280x960.txt",
    dla: Optional[Literal[0, 1]] = None,
    precision: Literal["kINT8", "kHALF", "kFLOAT"] = "kINT8",
    dont_show: bool = True,
    prof: bool = True,
    imgdir: str = "./images",
) -> List[str]:
    return [
        cmd,
        "--flagfile",
        flagfile,
        "--precision",
        precision,
        "--dla" if dla is not None else "",
        str(dla) if dla is not None else "",
        "--d",
        imgdir,
        "--dont_show" if dont_show else "",
        "--prof" if prof else "",
    ]


def powerlog(jetson):
    try:
        stats = jetson.stats
        power = jetson.power
        time = stats["time"] - start_time
        time = time.total_seconds()
        cpu_gpu = power["rail"]["VDD_CPU_GPU_CV"]["power"]
        soc = power["rail"]["VDD_SOC"]["power"]
        total = power["tot"]["power"]
        dla0 = False if stats["DLA0_CORE"] == "OFF" else True
        dla1 = False if stats["DLA1_CORE"] == "OFF" else True
        gpu = stats["GPU"]
        data = [time, cpu_gpu, soc, total, dla0, dla1, gpu]
        log.append(data)
    except:
        print("Error on powerlog")
        raise


# main power logging function
def main(logfile: str):
    try:
        os.remove(logfile)
    except:
        pass
    print("Simple jtop logger")
    print("Saving log on {file}".format(file=logfile))

    try:
        with jtop(interval=0.05) as jetson:
            while True:
                sleep(0.01)
                powerlog(jetson)
                print("Log at {time}".format(time=log[-1][0]))
                # checck if all processes are running
                for command in commands:
                    if command["process"].poll() != None:
                        print(
                            "Process {command} finished".format(
                                command=command["command"]
                            )
                        )
                    else:
                        break
                else:
                    print("All processes finished")
                    break
        # save log
        with open(logfile, "w") as f:
            writer = csv.writer(f)
            writer.writerow(datakeys)
            writer.writerows(log)
            print("Log saved on {file}".format(file=logfile))
    except:
        print("Error on main")
        raise


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Simple jtop logger")
    parser.add_argument("--file", action="store", dest="file", default="log.csv")
    args = parser.parse_args()

    # make commands
    commands = [
        {
            "command": make_command(precision="kINT8"),
            "cwd": "build",
            "process": None,
        },
        {
            "command": make_command(dla=0, precision="kINT8"),
            "cwd": "build",
            "process": None,
        },
        {
            "command": make_command(dla=1, precision="kINT8"),
            "cwd": "build",
            "process": None,
        },
    ]

    # run main
    try:
        for command in commands:
            # print(*command["command"])
            cmd = " ".join(command["command"])
            command["process"] = subprocess.Popen(
                cmd,
                shell=True,
                cwd=command["cwd"],
            )
        main(args.file)
    except:
        print("Error on main")
        print(log)
