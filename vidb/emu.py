#!/bin/env python3

import os, sys, traceback as tb, subprocess as sp
from vidb import ViDB


# let's create some cool aliases ;)
ANYTHING = lambda _item: True
def ANY(a, b):
    return lambda item: a(item) or b(item)
def ALL(a, b):
    return lambda item: a(item) and b(item)
def PARAM(a, b):
    return lambda item: item[a] == b 


def log(text):
    with open(sys.argv[2] + "/log.txt", "at") as f:
        f.write(text+"\n")

def puts(text):
    print(text, end="")

def move(x, y):
    if x < 0:
        left = True
        x = -x
    else:
        left = False
    
    if y < 0:
        up = True
        y = -y
    else:
        up = False
    
    string = "\033["
    if left:
        string += str(x)+"D"
    elif x:
        string += str(x)+"C"
    string += "\033["
    if up:
        string += str(y)+"A"
    elif y:
        string += str(y)+"B"
    puts(string)

def setpos(x, y):
    puts("\033["+str(y)+";"+str(x)+"H")


def main():
    if len(sys.argv) < 2:
        print("Usage: vidb start <directory>")
        return

    if sys.argv[1] != "start":
        print("Usage: vidb start <directory>")
        return
    
    if not os.path.exists(sys.argv[2]):
        print("\033[1;31mDirectory does not exist\033[0m")
        print("\r\033[31mEmulator stopped due to error\033[0m           ")
        return

    tput = sp.run(["tput", "cols"], stdout=sp.PIPE)
    cols = int(tput.stdout.decode().strip())

    tput = sp.run(["tput", "lines"], stdout=sp.PIPE)
    lines = int(tput.stdout.decode().strip())

    os.remove(sys.argv[2] + "/log.txt")
    
    with open(sys.argv[2] + "/log.txt", "wt") as f:
        f.write("Starting emulator\n")

    db = ViDB(sys.argv[2], log, cols)
    db.poll()

    while True:
        try:
            lines = []
            line = ""
            while 1:
                line = input("> ")
                lines.append(line)
                try:
                    compile("\n".join(lines), "<string>", "exec")
                    break
                except SyntaxError:
                    pass
                except Exception as e:
                    tb.print_exception(e)
                    break
            log("lines: " + "\n\t".join(lines) + "\n")
            try:
                exec("\n".join(lines))
                num = (cols-len("DONE"))//2
                print("\033[1;32m" + "─" * num + "DONE" + "─" * num + "\033[0m")
            except SystemExit:
                print("\r\033[1;32mEmulator stopped by script\033[0m")
                exit()
            except Exception as e:
                excname = e.__class__.__name__
                num = (cols-len(excname))//2
                print("\033[1;31m" + "─" * num + excname + "─" * num + "\033[0m")
                tb.print_exception(e)
                print("\r\033[1;31mEmulator stopped due to error\033[0m")
                exit()
            # print("\033[1A      \r", end="")
        except KeyboardInterrupt:
            print("\r\033[1;32mEmulator stopped by user\033[0m           ")
            break


if __name__ == "__main__":
    main()
