import pandas as pd
import os
import matplotlib.pyplot as plt


def calculate_speedup_for_file(filepath):
    """
    Reads a CSV file, calculates speedup, and returns data for plotting.
    """
    print(f"Processing file: {filepath}...")
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return []

    try:
        expected_col_names = ['service', 'architecture', 'num_clients', 'iterations_per_client', 'num_servers',
                              'elapsed_time']
        df = pd.read_csv(filepath, header=None, skiprows=1, names=expected_col_names, skipinitialspace=True)

        for col in ['num_clients', 'iterations_per_client', 'num_servers', 'elapsed_time']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['num_clients', 'iterations_per_client', 'num_servers', 'elapsed_time'], inplace=True)

        for col in ['num_clients', 'iterations_per_client', 'num_servers']:
            if col in df.columns:
                df[col] = df[col].astype(int)

    except pd.errors.EmptyDataError:
        print(f"Warning: File {filepath} is empty or contains only a header. No data to process.")
        return []
    except Exception as e:
        print(f"Error reading or processing {filepath}: {e}")
        return []

    if df.empty:
        print(f"No valid data rows found in {filepath} after parsing.")
        return []

    grouped = df.groupby(['service', 'architecture', 'num_clients', 'iterations_per_client'])

    if grouped.ngroups == 0:
        print(f"No data groups found in {filepath} for speedup calculation. Check data consistency.")
        return []

    collected_data_for_plotting = []
    overall_speedup_data_found_for_file = False

    for name, group_data in grouped:
        service, architecture, num_clients, iterations = name
        group_data = group_data.sort_values(by='num_servers').reset_index(drop=True)
        baseline_run = group_data[group_data['num_servers'] == 1]

        if baseline_run.empty:
            continue

        baseline_time = baseline_run['elapsed_time'].iloc[0]
        parallel_runs = group_data[group_data['num_servers'] > 1]

        if not parallel_runs.empty:
            if not overall_speedup_data_found_for_file:
                print(f"\nSpeedup Calculation Results for: {os.path.basename(filepath)}")
                overall_speedup_data_found_for_file = True

            print(
                f"\n  Scenario: Service={service}, Arch={architecture}, Clients={num_clients}, Iterations={iterations}")
            print(f"    Baseline (1 server) Time: {baseline_time:.4f}s")

            for _, row in parallel_runs.iterrows():
                num_servers = int(row['num_servers'])
                time_parallel = row['elapsed_time']
                if time_parallel > 0:
                    speedup = baseline_time / time_parallel
                    print(f"    Speedup with {num_servers} servers: {speedup:.2f} (Time: {time_parallel:.4f}s)")
                    collected_data_for_plotting.append({
                        'filepath_name': os.path.basename(filepath),
                        'service': service,
                        'architecture': architecture,
                        'num_clients': num_clients,
                        'iterations_per_client': iterations,
                        'num_servers': num_servers,
                        'speedup': speedup,
                        'baseline_time': baseline_time,
                        'time_parallel': time_parallel
                    })
                else:
                    print(
                        f"    Cannot calculate speedup with {num_servers} servers: time is zero or invalid ({time_parallel:.4f}s)")

    if not overall_speedup_data_found_for_file and not df.empty:
        print(f"No applicable data for speedup calculation found in {filepath}.")
        print("(This means no scenarios with both a 1-server baseline and multi-server results were found).")

    return collected_data_for_plotting


def plot_speedup_graphs(all_speedup_data):
    if not all_speedup_data:
        print("No speedup data available to plot.")
        return

    df_plot = pd.DataFrame(all_speedup_data)

    # Create a directory for graphs if it doesn't exist
    # Assumes script is run from its own directory or 'generated_graphs' is relative to CWD
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_dir = os.path.join(script_dir, 'generated_graphs')
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
        print(f"Created directory for graphs: {graph_dir}")

    # Group by scenario for plotting
    grouped_for_plot = df_plot.groupby(
        ['filepath_name', 'service', 'architecture', 'num_clients', 'iterations_per_client'])

    for name, group in grouped_for_plot:
        filepath_name, service, architecture, num_clients, iterations = name

        # Add baseline data (1 server, speedup = 1.0) for plotting
        plot_servers = [1] + group['num_servers'].tolist()
        plot_speedups = [1.0] + group['speedup'].tolist()

        # Sort by number of servers for consistent plotting order
        sorted_plot_data = sorted(zip(plot_servers, plot_speedups))
        plot_servers_sorted = [item[0] for item in sorted_plot_data]
        plot_speedups_sorted = [item[1] for item in sorted_plot_data]

        plt.figure(figsize=(10, 6))
        bars = plt.bar([str(s) for s in plot_servers_sorted], plot_speedups_sorted, color='skyblue', zorder=2)

        plt.xlabel("Number of Servers")
        plt.ylabel("Speedup (vs. 1 Server)")
        title_str = (
            f"Speedup: {service} on {architecture} ({os.path.splitext(filepath_name)[0].replace('_data', '')})\n"
            f"{num_clients} Client(s) x {iterations} Iterations/Client")
        plt.title(title_str)
        plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=1)
        plt.ylim(bottom=0)  # Ensure y-axis starts at 0

        # Add text labels on bars
        for bar_item in bars:
            yval = bar_item.get_height()
            plt.text(bar_item.get_x() + bar_item.get_width() / 2.0, yval + 0.05 * max(plot_speedups_sorted),
                     f'{yval:.2f}', ha='center', va='bottom')

        # Sanitize filename
        safe_filename_parts = [
            os.path.splitext(filepath_name)[0],
            service,
            architecture,
            str(num_clients) + "clients",
            str(iterations) + "iter"
        ]
        safe_filename = "_".join(
            part.replace(" ", "_").replace("/", "_") for part in safe_filename_parts) + "_speedup.png"

        save_path = os.path.join(graph_dir, safe_filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Saved graph: {save_path}")


def main():
    # Files relevant for speedup calculation
    # Paths are relative to the script's location if run directly,
    # or relative to CWD if imported.
    # For robustness, construct absolute paths or ensure CWD.
    # Assuming script is in 'graphs/' and data in 'Benchmarks/' at the same level as 'graphs/' parent.

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    files_to_process = [
        os.path.join(script_dir, '../Benchmarks/xmlrpc_data.csv'),
        os.path.join(script_dir, '../Benchmarks/pyro_data.csv')
    ]

    all_plot_data = []
    for f_path in files_to_process:
        plot_data = calculate_speedup_for_file(f_path)
        if plot_data:
            all_plot_data.extend(plot_data)
        print("-" * 40)

    if all_plot_data:
        plot_speedup_graphs(all_plot_data)
    else:
        print("No data collected from any file for plotting.")


if __name__ == '__main__':
    try:
        import matplotlib

        matplotlib.use('Agg')  # Use a non-interactive backend, suitable for saving files
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib is not installed. Please install it to generate graphs (e.g., pip install matplotlib).")
        exit()
    main()