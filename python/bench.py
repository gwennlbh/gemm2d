import subprocess
import pandas as pd
import os

# Fonction pour exécuter une commande MPI
def run_mpi_command(m, n, k, b, p, q, algo, la, niter, output_file="bench.csv"):
    command = [
        "mpirun",
        "-np", str(p * q),
        "./build/bin/main",
        "-m", str(m),
        "-n", str(n),
        "-k", str(k),
        "-b", str(b),
        "-p", str(p),
        "-q", str(q),
        "--algorithm", algo,
        "--niter", str(niter)
    ]
    if algo == "p2p-i-la":
        command.extend(["--lookahead", str(la)])
    command.append("-c")

    # Exécuter la commande et récupérer la sortie
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        gflops = parse_output(result.stdout)
        save_to_csv(m, n, k, b, p, q, algo, la, gflops, output_file)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de {algo}: {e.stderr}")

# Fonction pour extraire les GFLOPS de la sortie
def parse_output(output):
    for line in output.split("\n"):
        if "Gflop/s" in line:
            return float(line.split("|")[-1].strip().split()[0])
    return None

# Fonction pour sauvegarder les résultats dans un fichier CSV
def save_to_csv(m, n, k, b, p, q, algo, la, gflops, output_file):
    df = pd.DataFrame([{
        "m": m, "n": n, "k": k, "b": b,
        "p": p, "q": q, "algo": algo,
        "lookahead": la, "gflops": gflops
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

    # Configurations des paramètres
    for p in [2, 4]:
        for q in [2, 4]:
            for i in [4, 8, 12]:
                n = m = k = i * b
                for algo in ["p2p", "bcast"]:
                    run_mpi_command(m, n, k, b, p, q, algo, la=0, niter=niter, output_file=output_file)
                for la in range(1, k // b + 1):
                    run_mpi_command(m, n, k, b, p, q, "p2p-i-la", la, niter, output_file)
