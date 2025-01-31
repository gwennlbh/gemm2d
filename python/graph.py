import pandas as pd

def read_timings_from_csv(filename = "bench.csv"):
    return pd.read_csv(filename)

def plot_timings(df, x, y, style,  title, xlabel, ylabel, output_file):
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(10, 6))
    if style is None:
        sns.lineplot(ci=None, data=df, x=x, y=y)
    else:
        sns.lineplot(ci=None, data=df, x=x, y=y, style=style)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    df = read_timings_from_csv()
    for algo in {"p2p", "bcast", "p2p-i-la"}:
        plot_timings(df[df["algo"] == algo], "process_count", "duration", "m", f"Performance de {algo}", "Nombre de processus", "Temps [s]", f"{algo}_scalabilité_forte.png")
        plot_timings(df[df["algo"] == algo], "configuration", "gflops", None, f"Performance de {algo}", "Configurations (m*p*q)", "Temps [s]", f"{algo}_scalabilité_faible.png")
    # plot_timings(df, "process_count", "duration", "algo", "lookahead", "Performance des algorithmes", "Taille des matrices", "GFLOPS", "performance.png")
