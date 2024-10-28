import subprocess
import time
import threading
import yaml
import itertools

file_path = "/home/michalnovak/skola/mrs/mrs_apptainer/user_ros_workspace/src/mrs_multirotor_simulator/config/multirotor_simulator.yaml"

def run_simulation(t):
    # Start the tmux session via xterm
    try:    
        subprocess.run(['xterm', '-geometry', '100x40', '-fa', 'Monospace', '-fs', '14', '-e', 'bash', '-c', '/home/michalnovak/skola/mrs/mrs_apptainer/testparams/run_sim.sh'], timeout=t+20)
        # Add a short delay to allow the tmux session to start
        time.sleep(2)
    except subprocess.TimeoutExpired:
        print(f"xterm process exceeded {t} seconds and was terminated.")

def wait_for_tmux_session(session_name, socket_name, timeout=60, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check if the session exists using the specified socket
            subprocess.run(['tmux', '-L', socket_name, 'has-session', '-t', session_name], check=True)
            print(f"Session '{session_name}' exists.")
            return True
        except subprocess.CalledProcessError:
            # Session doesn't exist yet, wait and retry
            print(f"Waiting for session '{session_name}' to exist...")
            list_tmux_sessions(socket_name)
            time.sleep(interval)
    
    print(f"Timeout reached. Session '{session_name}' does not exist.")
    return False

def list_tmux_sessions(socket_name):
    try:
        # Run 'tmux list-sessions' with the correct socket
        result = subprocess.run(['tmux', '-L', socket_name, 'list-sessions'], capture_output=True, text=True, check=True)
        # Print the available sessions
        print("Available tmux sessions:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error listing tmux sessions:")
        print(e.stderr)

def turn_off_tmux_sim(session_name, socket_name):
    try:
        # Send 'kill-session' command to the tmux session
        subprocess.run(['tmux', '-L', socket_name, 'kill-session', '-t', session_name], check=True)
        print(f"Session '{session_name}' on socket '{socket_name}' has been terminated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill session '{session_name}' on socket '{socket_name}': {e}")

def check_tmux_panes_for_done(session_name, window_name, socket_name, num_panes):
    all_done = False

    while not all_done:
        all_done = True  # Assume all are done initially
        
        for pane_index in range(num_panes):
            try:
                # Capture output from the pane
                result = subprocess.run([
                    'tmux', '-L', socket_name, 'capture-pane', '-t', f'{session_name}:{4}.{pane_index}', 
                    '-p'
                ], capture_output=True, text=True, check=True)

                # Get the pane output
                output = result.stdout.strip().split('\n')

                # Check if the last line ends with "mrs_more_drones$"
                if output and not output[-1].endswith("$"):
                    all_done = False  # At least one pane is not showing the expected prompt
                    # print(f"Pane {pane_index} output: {output[-1]}")  # Print the last line for debugging
                # else:
                #     print(f"Pane {pane_index} has shown the expected prompt.")

            except subprocess.CalledProcessError as e:
                print(f"Error capturing output from pane {pane_index}: {e}")

        if not all_done:
            # print("Not all panes are done yet. Checking again...")
            time.sleep(1)  # Wait before checking again

    print("All panes have completed.")

def rosservice_call_activate_sim(session_name, window_name, socket_name):
    try:
        # Construct the target for the tmux send-keys command
        target = f'{session_name}:{window_name}'

        # Call the ROS service
        result = subprocess.run(['tmux', '-L', socket_name, 'send-keys', '-t', target, 
                                 'rosservice call /multirotor_simulator/activation', 'C-m'], 
                                capture_output=True, text=True, check=True)

        # Optionally print the output for debugging
        print("Service call output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Error calling the service:", e.stderr)

def run_session(t):
    session_name = "simulation"
    socket_name = "mrs"
    num_panes = 10
    
    th_run_sim = threading.Thread(target=run_simulation, args=(t,))
    th_run_sim.start()
    
    # Wait for the tmux session to appear on the correct socket
    wait_for_tmux_session(session_name, socket_name, timeout=60, interval=1)
    check_tmux_panes_for_done(session_name, "automatic_start", socket_name, num_panes)
    time.sleep(2)
    print("___________________________calling rosservice___________________________")
    rosservice_call_activate_sim(session_name, "activation", socket_name)
    time.sleep(t)
    turn_off_tmux_sim(session_name, socket_name)

def change_session_params(ALP0, ALP1, ALP2, BET0, BET1, BET2):
    try:
        # Load the YAML file
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)

        # Modify the parameters if new values are provided
        if ALP0 is not None:
            config['fish_model_params']['ALP0'] = ALP0
        if ALP1 is not None:
            config['fish_model_params']['ALP1'] = ALP1
        if ALP2 is not None:
            config['fish_model_params']['ALP2'] = ALP2
        if BET0 is not None:
            config['fish_model_params']['BET0'] = BET0
        if BET1 is not None:
            config['fish_model_params']['BET1'] = BET1
        if BET2 is not None:
            config['fish_model_params']['BET2'] = BET2

        # Write the changes back to the YAML file
        with open(file_path, 'w') as file:
            yaml.dump(config, file)

        print(f"Parameters updated in {file_path}:")
        print(config['fish_model_params'])

    except Exception as e:
        print(f"Error updating parameters: {e}")

def write_params_to_file(file_path, alp0, alp1, alp2, bet0, bet1, bet2):
    """Write the parameter values to the text file."""
    with open(file_path, 'a') as file:
        file.write(f"Parameters: alp0={alp0}, alp1={alp1}, alp2={alp2}, bet0={bet0}, bet1={bet1}, bet2={bet2}\n")


# fish_model_params:
#   GAM: 0.1
#   ALP0: 1
#   ALP1: 0.08 
#   ALP2: 0.5
#   BET0: 0.5
#   BET1: 0.08    
#   BET2: 0.5
#   V0: 1 # [m/s]
#   R: 1   # [m]  
#   VIS_FIELD_SIZE: 4096 #16384


if __name__ == "__main__":
    alp0_comb = [0.05, 0.2]
    alp1_comb = [0.08]
    alp2_comb = [0]
    bet0_comb = [0.01]
    bet1_comb = [0.08]
    bet2_comb = [0]
    results_file_path = '/home/michalnovak/skola/mrs/mrs_apptainer/testparams/metrics_results.txt'
    parameter_combinations = list(itertools.product(alp0_comb, alp1_comb, alp2_comb, bet0_comb, bet1_comb, bet2_comb))
    for alp0, alp1, alp2, bet0, bet1, bet2 in parameter_combinations:
        if alp1 != bet1:
            continue    # only want beta1 and alpha1 to be the same (as discussed in the original paper)
        write_params_to_file(results_file_path, alp0, alp1, alp2, bet0, bet1, bet2)
        change_session_params(alp0, alp1, alp2, bet0, bet1, bet2)
        run_session(120) #runs session for 2 mins   
        subprocess.run(["python3", "parse_and_clear_csv.py"])
