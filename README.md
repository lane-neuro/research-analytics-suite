<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">
  <p align="center">
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/network/members">
      <img src="https://img.shields.io/github/forks/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="GitHub Forks">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/stargazers">
      <img src="https://img.shields.io/github/stars/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="GitHub Stars">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/issues">
      <img src="https://img.shields.io/github/issues/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="GitHub Issues">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="GitHub License">
    </a>
    <a href="https://linkedin.com/in/lane14">
      <img src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555" alt="LinkedIn">
    </a>
  </p>

  <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite">
    <img src="neurobehavioral_analytics_suite/images/centered_banner_white_black_text_1800x700.png" alt="NeuroBehavioral Analytics Suite Banner" style="max-width: 75%; height: auto;">
  </a>
  <p>Author: <a href="#contact">Lane</a></p>
</div>

<div>
  <p align="left">
    The <strong>NeuroBehavioral Analytics Suite (NBAS)</strong>, developed within Gire Lab at the University of Washington, is a comprehensive, open-source platform written in Python for aggregating and analyzing scientific data from diverse sources. Unlike MATLAB and SPSS, NBAS is designed to be free and accessible, addressing financial and accessibility barriers in scientific research.
    <br /><br />
    <strong>Key Features:</strong>
    <ul>
      <li><strong>Data Management Engine (DME)</strong>: Filters and aggregates large, complex datasets from multiple sources.</li>
      <li><strong>Analytics Suite</strong>: Includes tools for neurobehavioral data analysis, advanced statistics, machine learning algorithms, and data visualization.</li>
      <li><strong>Preloaded Functions</strong>: Ready-to-use functions for common analysis tasks.</li>
      <li><strong>Custom Functions</strong>: Allows users to create and implement custom analysis functions.</li>
      <li><strong>Future Integration</strong>: Designed for compatibility with tools like <a href="https://github.com/DeepLabCut/DeepLabCut">DeepLabCut</a>.</li>
    </ul>
    <br /><br />
    <strong>NBAS</strong> aims to foster a collaborative research community, enabling scientists and researchers to share their analytic workflows and contribute to a repository of shared knowledge, accelerating scientific discovery and innovation.
  </p>
</div>

<br />
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#project-structure">Project Structure</a>
      <ul>
        <li><a href="#operation-manager">Operation Manager</a>
          <ul>
            <li><a href="#operation-manager-task">Task</a></li>
            <li><a href="#operation-manager-operations">Operations</a>
              <ul>
                <li><a href="#operations-computation">Computation</a></li>
                <li><a href="#operations-persistent">Persistent</a></li>
                <li><a href="#operations-project">Project</a></li>
              </ul>
            </li>
          </ul>
        </li>
        <li><a href="#gui">GUI</a>
          <ul>
            <li><a href="#gui-modules">Modules</a></li>
          </ul>
        </li>
        <li><a href="#data-engine">Data Engine</a>
          <ul>
            <li><a href="#data-engine-data-processing">Data Processing</a></li>
            <li><a href="#data-engine-data-structures">Data Structures</a></li>
            <li><a href="#data-engine-project">Project</a></li>
          </ul>
        </li>
        <li><a href="#analytics">Analytics</a>
          <ul>
            <li><a href="#preloaded">Preloaded</a>
              <ul>
                <li><a href="#preloaded-transformations">Transformations</a></li>
              </ul>
            </li>
          </ul>
        </li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

The **NeuroBehavioral Analytics Suite (NBAS)** is a cutting-edge, open-source platform meticulously crafted in Python to address the diverse needs of neuroscientific data analysis. NBAS stands out by offering a comprehensive suite of tools for data aggregation, management, and analysis, derived from various input sources such as pixel-tracking technology, accelerometers, and analog voltage outputs.

NBAS aims to democratize access to powerful data analysis tools traditionally dominated by commercial software like MATLAB and SPSS. By eliminating financial barriers, NBAS empowers researchers, educators, and industry professionals to conduct sophisticated analyses without the associated costs.

### Key Features:
* **Data Management Engine (DME)**: A robust system for filtering and aggregating large, complex datasets from multiple sources. The DME ensures seamless integration and handling of diverse data types, facilitating comprehensive and efficient data analysis.
* **Analytics Suite**: Offers an extensive array of tools for neurobehavioral data analysis, including advanced statistical methods, machine learning algorithms, and data visualization techniques. The analytics suite is designed to be both powerful and flexible, catering to the specific needs of each user.
  * **Preloaded Functions**: A library of ready-to-use functions for common analysis tasks, enabling users to quickly apply standard methods without extensive setup.
  * **Custom / User-Defined Functions**: Allows users to create and implement their own analysis functions, fostering innovation and customization in research workflows.
* **Future Integration**: NBAS is designed with future compatibility in mind, aiming to integrate seamlessly with other leading tools in the field, such as [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut), to expand its capabilities further.

In addition, NBAS aspires to cultivate a collaborative research community. It envisions a platform where scientists and researchers can share their analytic workflows, collaborate on projects, and contribute to a growing repository of shared knowledge and resources. This collaborative spirit aims to accelerate scientific discovery and innovation by leveraging the collective expertise of the global research community.

By providing a versatile and accessible toolset, NBAS not only enhances the efficiency and effectiveness of data analysis but also fosters a culture of open collaboration and shared progress in the scientific community.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running, follow these simple example steps.

### Prerequisites
Once you have cloned the repo (see [Installation](#installation)), you will need to install the required packages. This can be done in one of two ways:
* If you are using [Anaconda](https://www.anaconda.com/) as a virtual environment, you can use the supplied `environment.yml` file to create a new environment with all the required packages. To do this, run the following command in the terminal:
  ```sh
  conda env create --file environment.yml
  conda activate nbas
  ```
* <i>Alternatively</i>, you can install the required packages globally <i>(typically not recommended)</i> using the following command:
    ```sh
    pip install -r requirements.txt
  ```
<br />

### Installation
1. Clone the repo
   ```sh
   git clone https://github.com/lane-neuro/neurobehavioral-analytics-suite.git
   ```
2. Refer to <a href="#prerequisites">Prerequisites</a> and install the required packages.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

  
<!-- PROJECT STRUCTURE -->
## Project Structure

### Operation Manager
The `operation_manager` package orchestrates and manages data processing operations within NBAS.
- **[Task](operation_manager/task/README.md)**
- **[Operations](operation_manager/operations/README.md)**
  - **[Computation](operation_manager/operations/computation/README.md)**
  - **[Persistent](operation_manager/operations/persistent/README.md)**
  - **[Project](operation_manager/operations/project/README.md)**

### GUI
The `gui` package provides graphical user interfaces for interacting with NBAS.
- **[Modules](gui/modules/README.md)**

### Data Engine
The `data_engine` package handles the primary functionality for data processing and management within a project.
- **[Data Processing](data_engine/data_processing/README.md)**
- **[Data Structures](data_engine/data_structures/README.md)**
- **[Project](data_engine/project/README.md)**

### Analytics
The `analytics` package handles the application and visualization of data transformations within a project.
- **[Preloaded](analytics/preloaded/README.md)**
  - **[Transformations](analytics/preloaded/transformations/README.md)**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage
> <i>To be implemented at a later date.</i>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

### Lane
Neurobiological Researcher
<br /><i>Gire Lab, University of Washington</i>
<br />email: [justlane@uw.edu](mailto:justlane@uw.edu)
<br /><a href="https://linkedin.com/in/lane14"><img align="center" height="25" src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555"></a>
<br />
<br />
### David H. Gire, Ph.D.
Associate Professor, Principal Investigator
<br /><i>Gire Lab, University of Washington</i>
<br />email: [dhgire@uw.edu](mailto:dhgire@uw.edu)
<br /><a href="https://psych.uw.edu/people/6312"><img align="center" height="15" src="https://uw-s3-cdn.s3.us-west-2.amazonaws.com/wp-content/uploads/sites/230/2023/11/02134822/Wordmark_center_Purple_Hex.png"></a>
<br /><br /><br /><br /><br />Project Link: [https://github.com/lane-neuro/neurobehavioral-analytics-suite](https://github.com/lane-neuro/neurobehavioral-analytics-suite)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge
[contributors-url]: https://github.com/lane-neuro/neurobehavioral-analytics-suite/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge
[forks-url]: https://github.com/lane-neuro/neurobehavioral-analytics-suite/network/members
[stars-shield]: https://img.shields.io/github/stars/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge
[stars-url]: https://github.com/lane-neuro/neurobehavioral-analytics-suite/stargazers
[issues-shield]: https://img.shields.io/github/issues/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge
[issues-url]: https://github.com/lane-neuro/neurobehavioral-analytics-suite/issues
[license-shield]: https://img.shields.io/github/license/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge
[license-url]: https://github.com/lane-neuro/neurobehavioral-analytics-suite/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/lane14
