# D2DS
D2DS is an open-source doc-to-doc system that converts your markdown files into better looking PDF-files.

## How it works
The script is designed to systematically scan all markdown files located at the root of your project or repository. It identifies the corresponding configurations for each markdown file and reads them. Subsequently, the script prepares the files, applies the configurations, and generates the final output in PDF format. This process is executed using Python, leveraging Pandoc to facilitate the conversion of markdown to PDF via \LaTeX.

### Configuration
The output can be configured using a configuration file. There are three levels of configuration: the markdown-specific configuration file, the general configuration file, and the default configuration that is applied if no configuration files are found in the root folder. You can use the default_d2ds.cfg as a template for your own configuration files.

#### Markdown specific configuration file
The markdown-specific configuration file is created by appending ".cfg" to the markdown file name. For instance, if you have a file named "Installation_guide.md," the corresponding configuration file would be "Installation_guide.md.cfg" (case-sensitive). This file contains the same data as the general configuration file, but if both files exist, the markdown-specific configuration file takes precedence.

#### General configuration file
The general configuration file is applied universally to all outputs unless a markdown-specific configuration file is present. This configuration file should be named "d2ds.cfg."

#### Default configuration file
The default configuration file is utilized when neither a general configuration file nor a markdown-specific configuration file is found. While this file provides a fallback option, it is recommended to use a configuration file to avoid reliance on the default settings.

### Requirements
- [Docker Desktop](https://www.docker.com/)

### Step by step guide
1.  Clone this repository

2.  Create a docker image from the Dockerfile:
    `docker build -t <name> .`
    (replace `.` with the path to the Dockerfile, if you run the command from the same directory as the Dockerfile, then `.` works)
    (replace `<name>` with the resulting name you want the image to have, e.g. `d2ds`)

3.  Run the docker container to generate your documents, supply the markdown files through the use of volumes:
    `docker run -v <path>:/data/documents <name>`

    Where `<path>` is the relative path to your folder containing markdown files, config for D2DS, images, .bib file etc. (Keep a backup of this folder)
    Where `<name>` is the name of the image you just built
    You can also add the `--rm` flag to remove the container after the documentation has been generated.

4.  If successful, your folder should now contain a new folder "output" with the generated PDFs.

    If there were any errors in your markdown or errors in your config, e.g. wrong path, then D2DS won't produce any PDFs.
    And since the python script did not finish running you might have some remnants from the run, with data appended to your
    markdown files and some .bak files created. Either manually restore the files by editing them, or replace them with your backup.
    Check the docker container logs for more info about what went wrong if an error happened.

### D2DS User guide
For more instructions on how to use the new features available through D2DS, there's a user guide. The user guide can be made into a PDF using D2DS by following the step by step instructions. At step 4, if the terminal current directory is the cloned d2ds folder, the command would look like this: `docker run --rm -v ./user_guide/:/data/documents -dit d2ds`