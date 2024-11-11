import os, shutil, subprocess

# Name of the volume which will contain markdown etc
FOLDER_NAME = "documents"
FOLDER_DIRECTORY = f"{os.getcwd()}/{FOLDER_NAME}"

# General config name
D2DS_CONFIG_NAME = "d2ds.cfg"
# Always used Pandoc commands
ALWAYS_USED_PANDOC_COMMANDS = ["--filter mermaid-filter", "--filter pandoc-plantuml", "--filter pandoc-crossref", "--data-dir=/opt/pandoc" , "--lua-filter tables-rules.lua", "-C"]
# Custom commands that alter the document in some way
ALL_CUSTOM_COMMANDS = dict([("solo_cover", "\\newpage"), ("references", "\n\n\\newpage\n# References")])
# Dynamic Pandoc commands
PANDOC_COMMANDS = dict([("template", "--template $"), ("number-sections", "--number-sections"), ("toc-depth", "--toc-depth $"), 
            ("listings", "--listings=$"), ("highlight-style", "--highlight-style $"), ("toc", "--toc=$"), ("bibliography", f"--bibliography={FOLDER_DIRECTORY}/$"),
            ("csl", f"--csl {FOLDER_DIRECTORY}/$")])


# Default config
DEFAULT_CONFIG = "default_d2ds.cfg"

# Read configuration file and return all key-value pairs
def read_config(file_name, directory):
    try:
        # Get a list of files in the FOLDER_NAME directory
        files = os.listdir(directory)

        # Find the correct file name case-insensitively
        matched_file = next((f for f in files if f.lower() == file_name.lower()), None)

        if not matched_file:
            print(f"Error: The file '{file_name}' was not found.")
            return
        
        file_path = os.path.join(directory, matched_file)

        metadata = [] # List to store metadata variables and their values
        custom_commands = [] # List with all the custom commands
        commands = [] # List with all arguments to be added to the pandoc command
        
        # Open and read the file
        with open(file_path, 'r') as config:
            for line in config:
                # Strip whitespace and check if the line starts with '#' or is empty
                line = line.strip()
                if not line.startswith('#') and line != '':
                    # Split the line by '=' to get the variable and its value
                    if '=' in line:
                        var, value = map(str.strip, line.split('=', 1))
                        # Only add to list if both variable and value are present
                        if var and value:
                            if var in PANDOC_COMMANDS:
                                commands.append(PANDOC_COMMANDS[var].replace("$", value))                            
                            elif var in ALL_CUSTOM_COMMANDS:
                                custom_commands.append((var, value))
                            else:
                                # If not a pandoc command, it will be added as metadata
                                metadata.append((var, value))
        return metadata, custom_commands, commands

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    

# Generates the metadatablock 
def generate_metadata_block(variables, filename):
    metadata_block = "---\n"
    
    # Iterate all variables and add them
    for var, value in variables:
        if var == "titlepage-logo" or var == "titlepage-background" or var == "page-background":
            metadata_block += f"{var}: {FOLDER_DIRECTORY}/{value}\n"
        elif value == "/filename":
            metadata_block += f"{var}: {filename}\n"
        else:
            metadata_block += f"{var}: {value}\n"

    metadata_block += "...\n"    
    return metadata_block

# Generates the pandoc command used to run pandoc
def generate_pandoc_command(commands, input_filename):
    commands.extend(ALWAYS_USED_PANDOC_COMMANDS)

    # Join all commands into a single string
    all_commands = " ".join(commands)
    pandoc_cmd = f"pandoc {FOLDER_NAME}/{input_filename} {all_commands} -o {FOLDER_NAME}/output/{input_filename.replace('-temp', '').replace('.md', '.pdf')}"
    return pandoc_cmd

# Finds all markdown files in the directory
def get_markdowns_and_configs():    
    markdown_files = []
    
    # Iterate through all files in the directory
    for filename in os.listdir(FOLDER_NAME):
        # Check if the file has a .md extension
        if filename.endswith(".md"):
            config = get_config(filename + ".cfg")
            markdown_files.append((filename, config))
    return markdown_files

# Find the corresponding config file for the markdown
def get_config(config_file):
    # Check if the config file exists in the current directory
    if os.path.exists(os.path.join(FOLDER_DIRECTORY, config_file)):
        # If it exists, append it to the configs list
        return config_file    
    return None

# Handle the different custom commands
def handle_custom_command(variable, value, metadata_block, file):
    match variable:
        case "solo_cover":
            if value == "true":
                metadata_block = metadata_block + f"\n{ALL_CUSTOM_COMMANDS['solo_cover']}"
        case "references":
            if value == "true":
                append_at_end(f"{FOLDER_DIRECTORY}/{file}", ALL_CUSTOM_COMMANDS['references'])
    return metadata_block

def append_metadata_block(filename, metadata_block):
    # Open the file in read mode and store its current content
    with open(filename, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    # Open the file in write mode and write the metadata block followed by the original content
    with open(filename, 'w') as file:
        file.write(metadata_block + '\n' + content)
    
def append_at_end(file, cmd):
    # Open the file in append mode and write the string at the end
    with open(file, 'a') as file:
        file.write(cmd)

def get_all_pandoc_commands():    
    # Create FOLDER for documents if not exists
    if not os.path.exists(FOLDER_DIRECTORY) or not os.path.isdir(FOLDER_DIRECTORY):
        os.makedirs(f"{os.getcwd}/{FOLDER_NAME}")

    # Create output folder if it doesn't exist
    if (not os.path.exists(FOLDER_DIRECTORY + "/output")):
        subprocess.run(f"mkdir {FOLDER_DIRECTORY}/output", check=True, shell=True)

    # Check if d2ds.cfg exists
    d2ds_config = get_config(D2DS_CONFIG_NAME)

    # Get all markdown files (and corresponding configs, if any)
    markdowns = get_markdowns_and_configs()

    # Create a list of all pandoc commands that should be run
    pandoc_commands = []

    for (file, cfg) in markdowns:
        directory = FOLDER_DIRECTORY
        backup_file = f"{file}.bak"
        shutil.copyfile(f"{FOLDER_NAME}/{file}", f"{FOLDER_NAME}/{backup_file}")
        if cfg is None:
            cfg = d2ds_config if d2ds_config is not None else DEFAULT_CONFIG
            if (cfg == DEFAULT_CONFIG):
                directory = os.getcwd()
        metadata, custom_commands, commands = read_config(cfg, directory)
        metadata_block = generate_metadata_block(metadata, file.split(".")[0])
        for variable, value in custom_commands:
            metadata_block = handle_custom_command(variable, value, metadata_block, file)
        append_metadata_block(f"{FOLDER_DIRECTORY}/{file}", metadata_block)
        pandoc_commands.append(generate_pandoc_command(commands, file))

    # Return all pandoc commands and a list of all files
    files = [m[0] for m in markdowns]
    return pandoc_commands, files

def main():
    if (not os.path.exists(f"{os.getcwd()}/{FOLDER_NAME}")):
        subprocess.run(f"mkdir {FOLDER_NAME}", check=True, shell=True)

    number_of_outputs = 0
    pandoc_commands, files = get_all_pandoc_commands()
    for cmd in pandoc_commands:
        number_of_outputs += 1
        print(f"\nRunning: {cmd}")
        subprocess.run(cmd, check=True, shell=True)

    print(f"Done running D2DS. \nGenerated {number_of_outputs} outputs.")
    print("Restoring markdowns")

    for file in files:
        shutil.move(f"{FOLDER_DIRECTORY}/{file}.bak", f"{FOLDER_DIRECTORY}/{file}")

    print("Successfully restored all markdowns")

if __name__ == "__main__":
    main()