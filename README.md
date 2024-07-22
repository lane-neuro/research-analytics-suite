<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">
  <p align="center">
    <a href="https://github.com/lane-neuro/research-analytics-suite/network/members">
      <img src="https://img.shields.io/github/forks/lane-neuro/research-analytics-suite.svg?style=for-the-badge" alt="GitHub Forks">
    </a>
    <a href="https://github.com/lane-neuro/research-analytics-suite/stargazers">
      <img src="https://img.shields.io/github/stars/lane-neuro/research-analytics-suite.svg?style=for-the-badge" alt="GitHub Stars">
    </a>
    <a href="https://github.com/lane-neuro/research-analytics-suite/issues">
      <img src="https://img.shields.io/github/issues/lane-neuro/research-analytics-suite.svg?style=for-the-badge" alt="GitHub Issues">
    </a>
    <a href="https://github.com/lane-neuro/research-analytics-suite/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/lane-neuro/research-analytics-suite.svg?style=for-the-badge" alt="GitHub License">
    </a>
    <a href="https://linkedin.com/in/lane14">
      <img src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555" alt="LinkedIn">
    </a>
  </p>

  <a href="https://github.com/lane-neuro/research-analytics-suite">
    <img src="research_analytics_suite/gui/assets/images/centered_banner_white_black_text_1200x467.png" alt="Research Analytics Suite Banner" style="max-width: 75%; height: auto;">
  </a>
  <p>Author: <a href="#contact">Lane</a></p>
</div>

![Ubuntu](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/python-app.yml/badge.svg?branch=main&job=ubuntu-latest)
![macOS](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/python-app.yml/badge.svg?branch=main&job=macos-latest)
![Windows](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/python-app.yml/badge.svg?branch=main&job=windows-latest)

<div>
  <p align="left">
    The <strong>Research Analytics Suite (RAS)</strong>, developed by <a href="#contact">Lane</a> within Gire Lab at the University of Washington, is a comprehensive, open-source platform written in Python for aggregating and analyzing scientific data from diverse sources. RAS is designed to be free and accessible, addressing financial and accessibility barriers in scientific research.
    <br /><br />
    <b>Please note: RAS is currently under active development and is not yet ready for public use. This repository is intended for demonstration purposes and to showcase the project's structure and features while it is being developed.</b>
    <br /><br />
    <strong>Key Features:</strong>
    <ul>
      <li><strong>Data Management Engine (DME)</strong>: Filters and aggregates large, complex datasets from multiple sources.</li>
      <li><strong>Analytics Suite</strong>: Includes tools for research data analysis, advanced statistics, machine learning algorithms, and data visualization.</li>
      <li><strong>Preloaded Functions</strong>: Ready-to-use functions for common analysis tasks.</li>
      <li><strong>Custom Functions</strong>: Allows users to create and implement custom analysis functions.</li>
      <li><strong>Future Integration</strong>: Designed for compatibility with tools like <a href="https://github.com/DeepLabCut/DeepLabCut">DeepLabCut</a>.</li>
    </ul>
    <br />
    <strong>RAS</strong> aims to foster a collaborative research community, enabling scientists and researchers to share their analytic workflows and contribute to a repository of shared knowledge, accelerating scientific discovery through open collaboration.
  </p>
</div>

---
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#research-analytics-suite">Welcome</a></li>
      <ul>
        <li><a href="#overall-mission">Overall Mission</a></li>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#developed-with">Developed With</a></li>
      </ul>
    <li><a href="#getting-started--prerequisites">Getting Started & Prerequisites</a></li>
        <ul>
            <li><a href="#python-311">Python</a></li>
            <li><a href="#clone-the-repository">Clone the Repository</a></li>
        </ul>
    <li><a href="#installation">Installation (Anaconda or Pip)</a></li>
      <ul>
        <li><a href="#windows">Windows</a></li>
        <li><a href="#linux">Linux</a></li>
        <li><a href="#macos">MacOS</a></li>
      </ul>
    <li><a href="#running-research-analytics-suite">Running Research Analytics Suite</a></li>
      <ul>
        <li><a href="#command-line-arguments">Command Line Arguments</a></li>
        <li><a href="#examples">Examples</a></li>
      </ul>
    <li><a href="#project-structure">Project Structure</a></li>
      <ul>
        <li><a href="#operation-manager">Operation Manager</a></li>
        <li><a href="#gui">GUI</a></li>
        <li><a href="#data-engine">Data Engine</a></li>
        <li><a href="#analytics">Analytics</a></li>
      </ul>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


---

<!-- ABOUT THE PROJECT --> 
# Research Analytics Suite

The **Research Analytics Suite (RAS)** is a cutting-edge, open-source platform developed in Python to address the diverse needs of scientific data analysis. RAS stands out by offering a comprehensive suite of tools for data aggregation, management, and analysis, derived from various input sources such as pixel-tracking technology, accelerometers, and analog voltage outputs.

RAS aims to democratize access to powerful data analysis tools traditionally dominated by commercial software. By eliminating financial barriers, RAS empowers researchers, educators, and industry professionals to conduct sophisticated analyses without the associated costs.

## Overall Mission
* The Research Analytics Suite aspires to cultivate a collaborative research community. It envisions a platform where scientists and researchers can share their analytic workflows, collaborate on projects, and contribute to a growing repository of shared knowledge and resources. This collaborative spirit aims to accelerate scientific discovery and innovation by leveraging the collective expertise of the global research community.
<br />

* By providing a versatile and accessible toolset, RAS not only enhances the efficiency and effectiveness of data analysis but also fosters a culture of open collaboration and shared progress in the scientific community.

---

## Key Features

### Data Management Engine (DME) 
* A robust system for filtering and aggregating large, complex datasets from multiple sources. The DME ensures seamless integration and handling of diverse data types, facilitating comprehensive and efficient data analysis.

### Analytics Suite 
* Offers an extensive array of tools for research data analysis, including advanced statistical methods, machine learning algorithms, and data visualization techniques. The analytics suite is designed to be both powerful and flexible, catering to the specific needs of each user.
* **Preloaded Functions**: A library of ready-to-use functions for common analysis tasks, enabling users to quickly apply standard methods without extensive setup.
* **Custom / User-Defined Functions**: Allows users to create and implement their own analysis functions, fostering innovation and customization in research workflows.

### Future Integration
* RAS is designed with future compatibility in mind, aiming to integrate seamlessly with other leading tools in the field, such as [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut), to expand its capabilities further.

---
## Developed With
RAS is built using a variety of powerful tools and libraries to ensure robust functionality and performance, including (but not limited to): <br />
<div align="center">

<table>
  <tr>
    <th style="text-align: center;">Package</th>
    <th style="text-align: left;">Description</th>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a></td>
    <td><a href="https://www.python.org/">Python</a>: The core programming language used for the development of RAS.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://dask.org/"><img src="https://img.shields.io/badge/-Dask-171A21?style=flat-square&logo=dask&logoColor=white" alt="Dask"></a></td>
    <td><a href="https://dask.org/">Dask</a>: A flexible parallel computing library for analytic computing.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://pytorch.org/"><img src="https://img.shields.io/badge/-PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"></a></td>
    <td><a href="https://pytorch.org/">PyTorch</a>: An open-source machine learning framework for deep learning.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://www.tensorflow.org/"><img src="https://img.shields.io/badge/-TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white" alt="TensorFlow"></a></td>
    <td><a href="https://www.tensorflow.org/">TensorFlow</a>: An end-to-end open-source platform for machine learning.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://distributed.dask.org/"><img src="https://img.shields.io/badge/-Distributed-3776AB?style=flat-square&logo=python&logoColor=white" alt="Distributed"></a></td>
    <td><a href="https://distributed.dask.org/">Distributed</a>: A library for distributed computing with Python.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://github.com/hoffstadt/DearPyGui"><img src="https://img.shields.io/badge/-DearPyGui-3776AB?style=flat-square&logo=python&logoColor=white" alt="DearPyGui"></a></td>
    <td><a href="https://github.com/hoffstadt/DearPyGui">DearPyGui</a>: An easy-to-use, high-performance GUI framework for Python.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://pypi.org/project/dearpygui-async/"><img src="https://img.shields.io/badge/-DearPyGui--Async-3776AB?style=flat-square&logo=python&logoColor=white" alt="DearPyGui-Async"></a></td>
    <td><a href="https://pypi.org/project/dearpygui-async/">DearPyGui-Async</a>: An extension for DearPyGui to support asynchronous operations.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://pypi.org/project/cachey/"><img src="https://img.shields.io/badge/-Cachey-3776AB?style=flat-square&logo=python&logoColor=white" alt="Cachey"></a></td>
    <td><a href="https://pypi.org/project/cachey/">Cachey</a>: A caching library for managing the lifecycle of cached objects.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://matplotlib.org/"><img src="https://img.shields.io/badge/-Matplotlib-3776AB?style=flat-square&logo=python&logoColor=white" alt="Matplotlib"></a></td>
    <td><a href="https://matplotlib.org/">Matplotlib</a>: A comprehensive library for creating static, animated, and interactive visualizations in Python.</td>
  </tr>
  <tr>
    <td style="text-align: center;"><a href="https://numpy.org/"><img src="https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white" alt="NumPy"></a></td>
    <td><a href="https://numpy.org/">NumPy</a>: The fundamental package for scientific computing with Python.</td>
  </tr>
</table>

</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- GETTING STARTED -->
# Getting Started & Prerequisites

To get a local copy up and running, follow the following steps.

## Python (3.11)
* You can check your Python version by running the following command in the terminal:
   ```sh
   python --version
   ```
* If not, you can download it [here](https://www.python.org/downloads/) or use [Anaconda](https://www.anaconda.com/).
  
## Clone the Repository
   ```sh
   git clone https://github.com/lane-neuro/research-analytics-suite.git
   ```
## Navigate to the project directory
   ```sh
   cd research-analytics-suite
   ```
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- INSTALLATION -->
# Installation
## Windows
### Anaconda
1. Create a new environment using the supplied `environment.yml` file:
   ```sh
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```sh
    conda activate research-analytics-suite
    ```
   > <i>Continue to [Running the Project](#running-the-project)</i>
   
### Pip
1. Install the required packages using the following command:
   ```sh
   pip install -r requirements.txt
   ```
   > <i>Continue to [Running the Project](#running-the-project)</i>
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Linux
### [Prerequisite] PortAudio
1. Install PortAudio using the following command in the terminal:
   ```sh
   sudo apt-get install -y portaudio19-dev
   ```
### Anaconda
1. Create a new environment using the supplied `environment.yml` file:
   ```sh
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```sh
    conda activate research-analytics-suite
    ```
   > <i>Continue to [Running the Project](#running-the-project)</i>
   
### Pip
1. Install the required packages using the following command:
   ```sh
   pip install -r requirements.txt
   ```
   > <i>Continue to [Running the Project](#running-the-project)</i>
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## MacOS
### [Prerequisite] Homebrew
1. You can install Homebrew using *one* [1] of the following methods:
   - Download the package installer from the [Homebrew GitHub](https://github.com/Homebrew/brew/releases/tag/4.3.10) page.
   
      **--- OR ---**
   - Run the following command in the terminal from the [Homebrew website](https://brew.sh/):
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Once [Homebrew](https://brew.sh/) is installed, install the required packages using the following commands:
   ```sh
   brew install portaudio
   ```
   ```sh
   brew install hdf5
   ```
3. Install RAS using Anaconda **OR** Pip (below).
   <br />

### Anaconda
1. Create a new environment using the supplied `environment.yml` file:
   ```sh
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```sh
   conda activate research-analytics-suite
   ```
   > <i>Continue to [Running the Project](#running-the-project)</i>

### Pip
1. Install the required packages using the following command:
   ```sh
    pip install -r requirements.txt
    ```
    > <i>Continue to [Running the Project](#running-the-project)</i>
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

---
# Running Research Analytics Suite
Launch the Research Analytics Suite (RAS) using the following command in the terminal:
   ```sh
   python ResearchAnalyticsSuite.py
   ```
   * This will launch RAS with the default settings.
> <i>See [Command Line Arguments](#command-line-arguments) for launch argument customization</i>
## Command Line Arguments
You can provide the following command line arguments to customize the behavior of the Research Analytics Suite:

- **`-g`, `--gui`**: Launches the Research Analytics Suite GUI 
   - default: `'true'`).
- **`-o`, `--open_workspace`**: Opens or creates a workspace at the specified directory. 
   - default: `'~/Research-Analytics-Suite/workspaces/default_workspace'`
> <i>See the [Examples](#examples) section below for implementation examples.</i> 
  <p align="right">(<a href="#readme-top">back to top</a>)</p>

---
# Examples
## Creating / Opening a RAS Workspace
You can specify the workspace to open or create using the `-o` or `--open_workspace` argument.
   ```sh
   python ResearchAnalyticsSuite.py -o ~/Research-Analytics-Suite/workspaces/a_new_workspace
   ```
   * This will create a new workspace at `~/Research-Analytics-Suite/workspaces/a_new_workspace` if it does not already exist. 
   * If it does exist, it will open the existing workspace at that location.
   * Note: The path must be a directory, not a file. 
     * So if you want to open a `'config.json'` file located at `~/Research-Analytics-Suite/workspaces/look_another_workspace/config.json`, you would instead use the following command:
        ```sh
        python ResearchAnalyticsSuite.py -o ~/Research-Analytics-Suite/workspaces/look_another_workspace
        ```
     * This will open the workspace configuration file located within the `~/Research-Analytics-Suite/workspaces/look_another_workspace` directory.

## Launching RAS with the GUI
The GUI is the default mode of operation for RAS. However, you can explicitly specify the GUI mode by using the following command:
   ```sh
   python ResearchAnalyticsSuite.py -g true
   ```
   * This will launch RAS with the GUI; this essentially has the same effect as running RAS without any command-line arguments.
   * This is the default mode of operation for RAS, providing an interactive interface for data analysis and visualization.

## Launching RAS in Command-Line / Headless Mode
The GUI is the default mode of operation for RAS. However, you can run RAS in command-line mode only by using the following command:
   ```sh
   python ResearchAnalyticsSuite.py -g false
   ```
   * This will launch RAS without the GUI, running in command-line mode only.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- PROJECT STRUCTURE -->
# Project Structure
<i>Fluid and subject to change as the project is developed further. Refer to the code for the most up-to-date information.</i>

## Operation Manager
The `operation_manager` package orchestrates and manages data processing operations within RAS.
- **chains**: Handles sequences of operations.
- **control**: Manages control mechanisms.
- **execution**: Handles operation execution.
- **lifecycle**: Manages the lifecycle of operations.
- **management**: Includes operation management functionalities.
- **nodes**: Manages operation nodes.
- **operations**:
  - **computation**: Includes computational operations.
  - **core**: Provides core functionalities for operations.
    - **inheritance**: Provides functionalities for managing child operations in a parent operation.
    - **control**: Provides control functionalities for operations including start, pause, resume, and stop.
    - **execution**: Provides execution functionalities for operations including preparation and execution of actions.
    - **progress**: Provides functionalities for tracking and updating the progress of operations.
    - **workspace**: Provides functionalities for workspace interactions, loading, and saving operations.
  - **system**: Includes common system operations, such as ```ResourceMonitorOperation``` and ```ConsoleOperation```
- **task**: Manages all tasks associated with operations.

## GUI
The `gui` package provides graphical user interfaces for interacting with RAS.
<br />

```Note: The GUI package will be optional in future distributions, given RAS has real-time command-line interface integration.```
- **assets**: Contains GUI assets, such as images and icons.
- **base**: Base GUI components.
- **dialogs**: Contains dialog components, divided into subcategories:
  - **data_handling**: Dialogs related to data handling.
  - **visualization**: Dialogs for data visualization.
  - **settings**: Settings-related dialogs.
  - **management**: Management-related dialogs.
- **launcher**: GUI launcher scripts.
- **modules**: Different GUI modules.
- **utils**: Utility scripts for GUI components.

## Data Engine
The `data_engine` package handles the primary functionality for data processing and management within a project.
- **core**: Core data processing modules.
- **data_streams**: Handles live data input streams.
- **engine**: Data engine implementations.
- **integration**: Integration with external data sources, such as Amazon S3.
- **utils**: Utility scripts for data handling.
- **variable_storage**: Manages variable storage.
  - **storage**: Different storage backends for variables.

## Analytics
The `analytics` package handles the application and visualization of data transformations within a project.
- **core**: Core analytical processing and transformations.
- **custom_user**: Custom user-defined transformations and configurations.
- **evaluation**: Metrics and evaluation scripts for model performance.
- **models**: Machine learning and statistical models.
- **prediction**: Modules for making predictions using trained models.
- **preloaded**: Preloaded transformations and configurations.
  - **transformations**: Preloaded transformation modules.
- **preprocessing**: Data preprocessing modules.
- **training**: Modules for training machine learning models.
- **utils**: Utility functions and common metrics.
- **visualization**: Display and visualization of analytical transformations.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- USAGE EXAMPLES -->
# Usage
> <i>To be implemented at a later date.</i>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- CONTRIBUTING -->
# Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. 

Open-source contributions will be available in the near future. Star & watch the project to stay tuned for updates!

<!--
Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
-->

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- LICENSE -->
# License

Distributed under the [BSD-3-Clause License](https://github.com/lane-neuro/research-analytics-suite/blob/main/LICENSE). See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- CONTACT -->
# Contact

## Lane (B.S.)
Neurobiological Research Technician
<br /><i>Gire Lab, University of Washington</i>
<br />email: [justlane@uw.edu](mailto:justlane@uw.edu)
<br /><a href="https://linkedin.com/in/lane14"><img align="center" height="25" src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555"></a>
<br />
<br />
## Dr. David H. Gire (Ph.D.)
Associate Professor, Principal Investigator
<br /><i>Gire Lab, University of Washington</i>
<br />email: [dhgire@uw.edu](mailto:dhgire@uw.edu)
<br /><a href="https://psych.uw.edu/people/6312"><img align="center" height="15" src="https://uw-s3-cdn.s3.us-west-2.amazonaws.com/wp-content/uploads/sites/230/2023/11/02134822/Wordmark_center_Purple_Hex.png"></a>
<br /><br /><br /><br /><br />Project Link: [https://github.com/lane-neuro/research-analytics-suite](https://github.com/lane-neuro/research-analytics-suite)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/lane-neuro/research-analytics-suite.svg?style=for-the-badge
[contributors-url]: https://github.com/lane-neuro/research-analytics-suite/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/lane-neuro/research-analytics-suite.svg?style=for-the-badge
[forks-url]: https://github.com/lane-neuro/research-analytics-suite/network/members
[stars-shield]: https://img.shields.io/github/stars/lane-neuro/research-analytics-suite.svg?style=for-the-badge
[stars-url]: https://github.com/lane-neuro/research-analytics-suite/stargazers
[issues-shield]: https://img.shields.io/github/issues/lane-neuro/research-analytics-suite.svg?style=for-the-badge
[issues-url]: https://github.com/lane-neuro/research-analytics-suite/issues
[license-shield]: https://img.shields.io/github/license/lane-neuro/research-analytics-suite.svg?style=for-the-badge
[license-url]: https://github.com/lane-neuro/research-analytics-suite/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/lane14
