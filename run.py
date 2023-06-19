import os, sys
import time
import copy
import random
import numpy as np
from sklearn.utils import shuffle
import pandas as pd

with open("./test/llvmpasses.txt", mode="r") as f:
    PASSES = [x.strip() for x in f.readlines()]

# pg_path = "polybench/linear-algebra/blas/symm/symm.c"
# pg_name = "symm"

ini_cmd1 = 'clang -O0 -emit-llvm -I ./polybench/utilities -I ./polybench/datamining/correlation/correlation -c {path} -o {name}.bc'
ini_cmd2 = 'clang -O0 -emit-llvm -I ./polybench/utilities -I ./polybench/datamining/correlation/correlation -c ./polybench/utilities/polybench.c -o polybench.bc;'
cmd1 = ' -S polybench.bc -o polybench.opt.bc; llc -O0 -filetype=obj polybench.opt.bc -o polybench.o'
cmd2 = ' -S {name}.bc -o {name}.opt.bc; llc -O0 -filetype=obj {name}.opt.bc -o {name}.o'
cmd3 = 'clang -O0 -no-pie -lm *.o -o {name}'
cmd4 = './{name}'
clean_cmd = 'rm -rf *bc *.o *.I *.S {name}'

if __name__ == '__main__':
    res = []
    pg_path = sys.argv[1]
    pg_name = sys.argv[2]
    option = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    if option == 1:
        with open("./llvm_func_passes.txt", mode="r") as f:
            PASSES = [x.strip() for x in f.readlines()]
    for iter in range(10):
        rand_passes = shuffle(PASSES)
        if option == 1:
            rand_passes = [x[1:] for x in rand_passes]
            passes_str = f'-passes="{",".join(rand_passes)}"'
        else:
            passes_str = " ".join(rand_passes)
        print(f"Iteration {iter + 1}:", passes_str)
        print("*" * 5)
        os.system(clean_cmd.format(name=pg_name))
        os.system(ini_cmd1.format(path=pg_path, name=pg_name))
        os.system(ini_cmd2)
        os.system("opt " + passes_str + cmd1)
        os.system("opt " + passes_str + cmd2.format(name=pg_name))
        print(cmd3.format(name=pg_name))
        if os.system(cmd3.format(name=pg_name)) == 0:
            print("Compiled! Measuring execution time...")
        exe_times = []
        for rtime in range(10):
            begin = time.time()
            ret = os.system(cmd4.format(name=pg_name))
            if ret > 0:
                continue
            end = time.time()
            print(f"R{rtime + 1}:", end - begin)
            exe_times.append(end - begin)
        print(exe_times)
        print(f"Std: {np.std(exe_times)}; Median: {np.median(exe_times)}; Mean: {np.mean(exe_times)}; Min: {np.min(exe_times)}; Max: {np.max(exe_times)}")
        print("=" * 20)
        res.append({
            "rtime": exe_times,
            "std": np.std(exe_times),
            "median": np.median(exe_times),
            "mean": np.mean(exe_times),
            "min": np.min(exe_times),
            "max": np.max(exe_times)
        })

    pd.DataFrame(res).to_csv(f"./res/{pg_name}.csv", index=False)




