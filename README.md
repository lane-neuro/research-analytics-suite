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

![Ubuntu](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/test-ubuntu-latest.yml/badge.svg)
![macOS](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/test-macos-latest.yml/badge.svg)
![Windows](https://github.com/lane-neuro/research-analytics-suite/actions/workflows/test-windows-latest.yml/badge.svg)


  <a href="https://github.com/lane-neuro/research-analytics-suite">
    <img src="research_analytics_suite/gui/assets/images/centered_banner_white_black_text_1200x467.png" alt="Research Analytics Suite Banner" style="max-width: 75%; height: auto;">
  </a>
</div>

<!-- WELCOME -->
# Research Analytics Suite

<p>Author: <a href="#contact">Lane</a></p>

The **Research Analytics Suite (RAS)** is a free, open-source platform for managing and analyzing scientific data.  
RAS removes financial and technical barriers by providing a user-friendly desktop application for researchers, educators, and professionals.

> **Note:** RAS is now available in packaged releases for **Windows** and **macOS**. You no longer need to install Python or any dependencies manually.

---

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#research-analytics-suite">Welcome</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
      <ul>
        <li><a href="#windows-installation">Windows Installation</a></li>
        <li><a href="#macos-installation">macOS Installation</a></li>
      </ul>
    <li><a href="#running-ras">Running RAS</a></li>
    <li><a href="#examples">Examples</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#developer-setup">Developer Setup</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

---

<!-- GETTING STARTED -->
# Getting Started

Download the latest release for your operating system from the  
👉 [**RAS Releases Page**](https://github.com/lane-neuro/research-analytics-suite/releases)

## Windows Installation
1. Download the `.zip` file from the releases page.  
2. Extract the folder to your preferred location.  
3. Double-click **ResearchAnalyticsSuite.exe** to launch.  

_No further installation required._

## macOS Installation
1. Download the `.dmg` file from the releases page.  
2. Open the `.dmg` and drag **ResearchAnalyticsSuite.app** into your **Applications** folder.  
3. Launch RAS from **Applications** (you may need to allow it in **System Settings → Privacy & Security**). 

<p align="right">(<a href="#readme-top">back to top</a>)</p> 

---

<!-- RUNNING RAS -->
# Running RAS

Once installed, simply open the program:
- **Windows**: double-click the `.exe`
- **macOS**: launch the `.app`

Advanced users can also run RAS with custom command-line arguments:

   ```sh
   ResearchAnalyticsSuite -o ~/workspaces/new_project -g false
   ```
- `-g true/false` → enable or disable GUI
- `-o PATH` → open or create a workspace at PATH

Reference the [**Getting Started Tutorial**](https://github.com/lane-neuro/research-analytics-suite/docs/Getting_Started_Tutorial.md) for more details on using RAS.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- EXAMPLES -->
# Examples
## Create or Open a Workspace
   ```sh
   ResearchAnalyticsSuite -o ~/Research-Analytics-Suite/workspaces/my_project
   ```
- Creates a new workspace if it doesn’t exist.
- Opens the existing one if it does.

## Launch in Command Line Only
   ```sh
   ResearchAnalyticsSuite -g false
   ```
- Disables the GUI and runs RAS in command-line mode.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- PROJECT STRUCTURE -->
# Project Structure
<i>Fluid and subject to change as the project evolves. Developers should see the code for the latest details.</i>
- operation_manager/ → data processing orchestration
- gui/ → graphical user interface
- data_engine/ → data ingestion, streams, and integration
- analytics/ → models, stats, and visualization
- hardware_manager/ → device interfacing and control *(in-development)*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- DEVELOPER SETUP -->
# Developer Setup
If you want to build from source instead of using the packaged release:
   ```sh
   git clone https://github.com/lane-neuro/research-analytics-suite.git
   cd research-analytics-suite
   conda env create -f environment_win_linux.yml   # or environment_osx.yml
   conda activate research-analytics-suite
   python ResearchAnalyticsSuite.py
   ```

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

## Lane (B.Sc.)
Neurobiological Research Technologist
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
