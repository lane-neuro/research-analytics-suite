<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url] -->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![BSD-3 License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center"> 
<!--
  <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->

# Data Engine Project
### Part of NeuroBehavioral Analytics Suite (NBAS)
Author: [Lane](#contact)
  <p align="left">
The Project subpackage within the Data Engine package handles project management functionalities within the NeuroBehavioral Analytics Suite (NBAS).
<br />
<br />
    <!-- <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite"><strong>Explore the docs »</strong></a> -->
    <br />
    <!-- <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite">View Demo</a>
    ·
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
    -->
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-subpackage">About The Subpackage</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE SUBPACKAGE -->
## About The Subpackage

The `project` subpackage within the Data Engine package defines and manages functionalities for handling projects in the NeuroBehavioral Analytics Suite (NBAS). The key components of this subpackage include:

- **load_project**: Function to load a project from a given file path using the pickle module to decode the DataEngine object from the file.
- **save_project**: Function to save the active project to a file using the pickle module to serialize the DataEngine object.
- **new_project**: Function to create a new project, save it to disk, reload it, and return it as a DataEngine object.
- **ProjectMetadata**: Class to store project metadata for the active project, including methods for initializing and representing the metadata.

### load_project
The `load_project` function loads the active project from a file. It uses the pickle module to decode the DataEngine object from the file and returns it.

### save_project
The `save_project` function saves the active project to a file. It uses the pickle module to serialize the DataEngine object and write it to a file.

### new_project
The `new_project` function creates a new project, saves it to disk, reloads it, and returns it as a DataEngine object. It initializes the base DataEngine object with provided parameters, saves the project, and then reloads it.

### ProjectMetadata
The `ProjectMetadata` class stores project metadata for the active project. It includes methods for initializing the metadata and providing a string representation of the metadata. Attributes include directory, user, subject, framerate, and analytics for the active project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

For getting started instructions, including prerequisites and installation steps, please refer to the [Getting Started section](https://github.com/lane-neuro/neurobehavioral-analytics-suite#getting-started) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Usage instructions for the Data Engine Project subpackage will be provided at a later date.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such a great place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

For contributing guidelines, please refer to the [Contributing section](https://github.com/lane-neuro/neurobehavioral-analytics-suite#contributing) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

**Lane**  
Neurobiological Researcher  
Gire Lab, University of Washington  
Email: [justlane@uw.edu](mailto:justlane@uw.edu)

**David H. Gire, Ph.D.**  
Associate Professor, Principal Investigator  
Gire Lab, University of Washington  
Email: [dhgire@uw.edu](mailto:dhgire@uw.edu)

Project Link: [NeuroBehavioral Analytics Suite](https://github.com/lane-neuro/neurobehavioral-analytics-suite)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
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
