import subprocess
from app import folder_data_dir

def execute_file(folder, current_user, selectedOption):
    combined_script_content = ""
    for option in selectedOption:
        script_path = f"{option}.sh"
        try:
            with open(script_path, 'r') as file:
                combined_script_content += file.read() + "\n"
        except FileNotFoundError as e:
            print(f"File ${script_path} not found")
        except Exception as e:
            print("Error: "+e)
    
    combined_script_path = f"{folder_data_dir}/{current_user.username}/script.sh"
    try:
        with open(combined_script_path, "w") as file:
            file.write(combined_script_content)
    except Exception as e:
        print(f"An error occurred while writing to {combined_script_path}: {e}")
        
    command = f"screen -dmS {folder.name} bash {combined_script_path} {folder.path} {folder_data_dir}/{current_user.username}"
    print(command)
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing {command}: {e}")
    # for option in selectedOption:
    #     script_path = f"{option}.sh"
    #     command = f"screen -dmS {folder.name}_{option} bash {script_path} {folder.path} {folder_data_dir}/{current_user.username}"
    #     try:
    #         subprocess.run(command, shell=True, check=True)
    #     except subprocess.CalledProcessError as e:
    #         print(f"An error occurred while executing {command}: {e}")

    
    # command = f"{folder_data_dir}/{current_user.username}/whole_genome_script_for_server.sh {folder.path}"
    # command = f"screen -dm -S {folder.name} bash -c '{command}'"
    # # Execute the command
    # subprocess.run(command, shell=True, check=True)
