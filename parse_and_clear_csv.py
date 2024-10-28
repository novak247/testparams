import csv

def parse_metrics(file_path):
    total_polarization = 0.0
    total_mean_distance = 0.0
    total_overlap = 0.0
    max_largest_subgroup = 0
    count = 0

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 5:
                continue  # Skip rows with insufficient data
            
            try:
                polarization = float(row[1])
                mean_distance = float(row[2])
                overlap = float(row[3])
                largest_subgroup = int(row[4])
                
                total_polarization += polarization
                total_mean_distance += mean_distance
                total_overlap += overlap
                max_largest_subgroup = max(max_largest_subgroup, largest_subgroup)
                count += 1
            except ValueError:
                print(f"Skipping invalid row: {row}")

    # Calculate averages
    average_polarization = total_polarization / count if count > 0 else 0.0
    average_mean_distance = total_mean_distance / count if count > 0 else 0.0
    average_overlap = total_overlap / count if count > 0 else 0.0

    return average_polarization, average_mean_distance, average_overlap, max_largest_subgroup

def clear_csv(file_path):
    """Clear the contents of the CSV file."""
    with open(file_path, 'w') as file:
        file.truncate()

def write_results_to_file(file_path, avg_polarization, avg_mean_distance, avg_overlap, max_largest_subgroup):
    """Write the calculated metrics to a text file."""
    with open(file_path, 'a') as file:
        file.write(f"Total Average Polarization: {avg_polarization}\n")
        file.write(f"Total Average Mean Distance: {avg_mean_distance}\n")
        file.write(f"Average Overlap: {avg_overlap}\n")
        file.write(f"Max of Largest Subgroup: {max_largest_subgroup}\n")

if __name__ == "__main__":
    csv_file_path = "/home/michalnovak/skola/mrs/mrs_apptainer/user_ros_workspace/src/mrs_multirotor_simulator/tmux/mrs_more_drones/simulation_metrics.csv"
    results_file_path = "/home/michalnovak/skola/mrs/mrs_apptainer/testparams/metrics_results.txt"
    
    avg_polarization, avg_mean_distance, avg_overlap, max_largest_subgroup = parse_metrics(csv_file_path)
    
    # Write the results to a .txt file
    write_results_to_file(results_file_path, avg_polarization, avg_mean_distance, avg_overlap, max_largest_subgroup)
    print(f"Results written to {results_file_path}")
    
    # Clear the contents of the CSV after parsing
    clear_csv(csv_file_path)
    print(f"Cleared contents of {csv_file_path}")
