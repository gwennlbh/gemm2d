import subprocess
import pandas as pd
from pathlib import Path
from time import time
import os

# Fonction pour exécuter une commande MPI
def run_mpi_command(m, n, i, k, b, p, q, algo, la, niter, output_file="bench.csv"):
    command = [
        "smpirun",
        "-np", str(p * q),
        "-trace",
        f"--cfg=smpi/tmpdir:{os.path.expanduser('~/')}/tmp_simgrid",
        "-platform",
        "../platforms/cluster_crossbar.xml",
        "-hostfile",
        "../hostfiles/cluster_hostfile.txt",
        "../build/bin/main",
        "-m", str(m),
        "-n", str(n),
        "-k", str(k),
        "-b", str(b),
        "-p", str(p),
        "-q", str(q),
        "--algorithm", algo,
        "--niter", str(niter),
    ]
    if algo == "p2p-i-la":
        command.extend(["--lookahead", str(la)])
    command.append("-c")

    # Exécuter la commande et récupérer la sortie
    try:
        print(' '.join(command))
        start = time()
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        duration = time() - start
        gflops = parse_output(result.stdout)
        save_to_csv(m, i, p, q, algo, la, gflops, output_file, duration)
        if Path(f"./smpi_simgrid.trace").exists():
            Path(f"./smpi_simgrid.trace").rename(f"../bench_traces/{algo}_{m}_{p}_{q}_{la}.trace")
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(f"Erreur lors de l'exécution de {algo}: {e.stderr}")

# Fonction pour extraire les GFLOPS de la sortie
def parse_output(output):
    for line in output.split("\n"):
        if "Gflop/s" in line:
            return float(line.split("|")[-1].strip().split()[0])
    return None

# Indice plus élevé = matrice plus grande et plus de processus
def configuration_index(i, p, q):
    # for i in [4, 6, 8, 10, 12, 14]:
    """
    match (p*q, i):
        case (4, 4): return 1
        case (8, 6): return 2
        case (12, 8): return 3
        case (16, 10): return 4
        case (24, 12): return 5
        case (36, 14): return 6
    """

    return {
        (4, 4): 1,
        (8, 6): 2,
        (12, 8): 3,
        (16, 10): 4,
        (24, 12): 5,
        (36, 14): 6,
    }.get((p*q, i), 0)
    

# Fonction pour sauvegarder les résultats dans un fichier CSV
def save_to_csv(m, i, p, q, algo, la, gflops, output_file, duration):
    df = pd.DataFrame([{
        "m": m,
        "p": p, "q": q, "algo": algo,
        "lookahead": la, "gflops": gflops,
        "process_count": p * q,
        "duration": duration,
        "configuration": configuration_index(i, p, q)
    }])

    if not os.path.exists(output_file):
        df.to_csv(output_file, index=False)
    else:
        df.to_csv(output_file, mode='a', header=False, index=False)

# Exécution des benchmarks
if __name__ == "__main__":
    b = 256
    niter = 5
    output_file = "bench.csv"
    Path("bench.csv").unlink(missing_ok=True)

    # Configurations des paramètres
    for p in [2, 4, 6]:
        for q in [2,4, 6]:
            for i in [4, 6, 8, 10, 12, 14]:
                n = m = k = i * b
                run_mpi_command(m, n,i, k, b, p, q, "bcast", la=0, niter=niter, output_file=output_file)
                run_mpi_command(m, n,i, k, b, p, q, "p2p", la=0, niter=niter, output_file=output_file)
                # for la in range(1, k // b + 1):
                run_mpi_command(m, n,i, k, b, p, q, "p2p-i-la", la=2, niter=niter, output_file=output_file)
