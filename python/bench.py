import subprocess
import pandas as pd
from pathlib import Path
from time import time
import os

# Fonction pour exécuter une commande MPI
def run_mpi_command(m, n, k, b, p, q, algo, la, niter, output_file="bench.csv"):
    command = [
        "smpirun",
        "-np", str(p * q),
        "-trace",
        "--cfg=smpi/tmpdir:/home/aki1207/tmp_simgrid",
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
        save_to_csv(m, p, q, algo, la, gflops, output_file, duration)
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(f"Erreur lors de l'exécution de {algo}: {e.stderr}")

# Fonction pour extraire les GFLOPS de la sortie
def parse_output(output):
    for line in output.split("\n"):
        if "Gflop/s" in line:
            return float(line.split("|")[-1].strip().split()[0])
    return None

# Fonction pour sauvegarder les résultats dans un fichier CSV
def save_to_csv(m, p, q, algo, la, gflops, output_file, duration):
    df = pd.DataFrame([{
        "m": m,
        "p": p, "q": q, "algo": algo,
        "lookahead": la, "gflops": gflops,
        "process_count": p * q,
        "duration": duration
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
    for p in [2, 4]:
        for q in [2, 4]:
            for i in [4, 8, 12]:
                n = m = k = i * b
                run_mpi_command(m, n, k, b, p, q, "bcast", la=0, niter=niter, output_file=output_file)
                run_mpi_command(m, n, k, b, p, q, "p2p", la=5, niter=niter, output_file=output_file)
                # for la in range(1, k // b + 1):
                run_mpi_command(m, n, k, b, p, q, "p2p-i-la", la=2, niter=niter, output_file=output_file)
