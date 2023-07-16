from matplotlib import pyplot as plt
import argparse
import pandas as pd
from glob import glob
from os import path


def main(logdir, show=True, save=False, savefile="power.png"):
    """
        log format
    time,cpu-gpu,soc,total,DLA0,DLA1
    1.102278,1066,1146,5415,False,False
    """
    # find *.csv in logdir
    logdir = path.join(logdir, "*.csv")
    logfiles = glob(logdir)

    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    # read log
    for logfile in logfiles:
        df = pd.read_csv(logfile)
        # plot
        # ax.plot(df["time"], df["cpu-gpu"], label="CPU+GPU")
        # ax.plot(df["time"], df["soc"], label="SOC")
        label = path.basename(logfile).split(".")[0]
        ax.plot(df["time"], df["total"], label=label)
    ax.legend()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Power (mW)")
    ax.set_title("Power consumption")
    if save:
        plt.savefig(savefile)
    if show:
        plt.show()


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Make graph from log file")
    parser.add_argument("-d", "--dir", help="Log file dir to plot", default="log")
    parser.add_argument("-s", "--save", help="Save graph to file", action="store_true")
    parser.add_argument(
        "--savefile",
        help="File to save graph",
        default="summary.png",
    )
    parser.add_argument(
        "-n",
        "--noshow",
        help="Do not show graph",
        action="store_true",
    )
    args = parser.parse_args()
    main(args.dir, show=not args.noshow, save=args.save, savefile=args.savefile)
