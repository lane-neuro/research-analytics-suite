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

# Operations Subpackage
### Part of NeuroBehavioral Analytics Suite (NBAS)
Author: [Lane](#contact)
  <p align="left">
The Operations subpackage within the `operation_manager` module handles the definition and management of operations within the NBAS.
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

The `operations` subpackage within the `operation_manager` module defines and manages various operations in the NeuroBehavioral Analytics Suite (NBAS). The key components of this subpackage include:

- **ABCOperation**: An abstract base class that provides a common interface for all operations. It defines methods like `execute`, `start`, `pause`, `stop`, `resume`, and others which must be implemented by any subclass.
- **Operation**: A concrete implementation of the `ABCOperation` class, responsible for managing tasks, tracking progress, and handling exceptions during execution.
- **CustomOperation**: A subclass of `Operation` that handles custom operations requiring function processing. It allows setting the function to be processed and managing its execution.

### ABCOperation
The `ABCOperation` class provides a common interface for all operations in the NBAS, requiring child classes to implement essential methods for operation management, such as `execute`, `start`, `pause`, `stop`, `resume`, etc.

### Operation
The `Operation` class represents a task that can be managed through various states like started, stopped, paused, resumed, and reset. It tracks the progress of the task and handles any exceptions that occur during execution.

### CustomOperation
The `CustomOperation` class extends `Operation` to handle custom operations that require function processing. It allows users to set a function to be executed and manages its execution, including handling exceptions and tracking the status and result of the operation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

For getting started instructions, including prerequisites and installation steps, please refer to the [Getting Started section](https://github.com/lane-neuro/neurobehavioral-analytics-suite#getting-started) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Usage instructions for the Operations subpackage will be provided at a later date.

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
