import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def create_performance_graph(csv_file_path, output_image_path=None):
    """
    Generates a graph from benchmark data.

    Args:
        csv_file_path (str): The path to the CSV file.
        output_image_path (str, optional): Path to save the graph image.
                                           If None, displays the plot.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Calculate 'petitions'
        df['petitions'] = df['clients'] * df['requests']

        # Create the plot
        plt.figure(figsize=(12, 8))

        # Group by service and protocol, then plot
        for (service, protocol, servers), group in df.groupby(['service', 'protocol', 'servers']):
            # Sort by petitions to ensure lines are drawn correctly
            group = group.sort_values(by='petitions')
            plt.plot(group['petitions'], group['time'], marker='o', linestyle='-', label=f'{service} - {protocol} - {servers}')

        # Set labels and title
        plt.xlabel("Total Petitions (Clients * Requests)")
        plt.ylabel("Time (seconds)")
        plt.title("Performance Benchmark: Time vs. Petitions")

        # Format x-axis (formerly y-axis) to avoid scientific notation and show integers
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))

        plt.legend()
        plt.grid(True)
        plt.tight_layout()  # Adjust layout to prevent labels from overlapping

        if output_image_path:
            plt.savefig(output_image_path)
            print(f"Graph saved to {output_image_path}")
        else:
            plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    # Example usage:
    # Replace 'your_file.csv' with the actual path to your CSV file.
    # For example, if your file is 'Benchmarks/single_node_stress.csv'
    csv_input_file = '../Benchmarks/single_node_stress.csv'
    # You can also specify a path to save the image, e.g., 'performance_graph.png'
    # output_file = 'performance_graph_inverted.png'
    # create_performance_graph(csv_input_file, output_file)
    create_performance_graph(csv_input_file)

    # If you want to plot the multiple_node_static.csv as well:
    # csv_input_file_multi = 'Benchmarks/multiple_node_static.csv'
    # output_file_multi = 'performance_graph_multi_node_inverted.png'
    # create_performance_graph(csv_input_file_multi, output_file_multi)