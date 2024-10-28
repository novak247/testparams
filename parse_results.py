import re

def parse_and_sort_results(input_file_path, output_file_path):
    results = []
    
    # Regular expressions to capture parameters and values
    params_pattern = r"Parameters: alp0=(.*?), alp1=(.*?), alp2=(.*?), bet0=(.*?), bet1=(.*?), bet2=(.*?)\n"
    overlap_pattern = r"Average Overlap: (.*)\n"

    with open(input_file_path, 'r') as file:
        content = file.read()

    # Find all blocks with parameters and overlap values
    entries = re.findall(r"(Parameters: .*?Average Overlap: .*?Max of Largest Subgroup: \d+)", content, re.DOTALL)
    
    for entry in entries:
        # Extract parameters
        params_match = re.search(params_pattern, entry)
        if params_match:
            params = {
                'alp0': float(params_match.group(1)),
                'alp1': float(params_match.group(2)),
                'alp2': float(params_match.group(3)),
                'bet0': float(params_match.group(4)),
                'bet1': float(params_match.group(5)),
                'bet2': float(params_match.group(6))
            }
        
        # Extract Average Overlap
        overlap_match = re.search(overlap_pattern, entry)
        if overlap_match:
            average_overlap = float(overlap_match.group(1))
            # Add the entire entry as a tuple (params, overlap, full text block) for easy sorting
            results.append((params, average_overlap, entry.strip()))

    # Sort by "Average Overlap" value
    results.sort(key=lambda x: x[1])

    # Write sorted results to the output file
    with open(output_file_path, 'w') as output_file:
        for params, average_overlap, entry_text in results:
            output_file.write(f"{entry_text}\n\n")

    print(f"Sorted results written to {output_file_path}")

# Example usage
input_file_path = 'metrics_results.txt'
output_file_path = 'sorted_metrics_results.txt'
parse_and_sort_results(input_file_path, output_file_path)
