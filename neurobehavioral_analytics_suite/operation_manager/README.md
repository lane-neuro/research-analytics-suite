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

# Operation Manager Module/Package
### Part of NeuroBehavioral Analytics Suite (NBAS)
Author: [Lane](#contact)
  <p align="left">
The Operation Manager module orchestrates and manages data processing operations within the NBAS.
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
      <a href="#about-the-module">About The Module</a>
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

<!-- ABOUT THE MODULE -->
## About The Module

The `operation_manager` module within the NeuroBehavioral Analytics Suite (NBAS) is designed to manage and orchestrate various data processing operations. The primary components and responsibilities of the module include:

- **OperationManager**: Manages the creation, queuing, and control of operations. It provides methods to add, resume, pause, and stop operations.
- **OperationExecutor**: Handles the execution of operations in the queue and manages their status and logging.
- **OperationQueue**: Manages a queue of operations, providing methods to add, remove, move, and retrieve operations, ensuring efficient management and execution.
- **OperationChain**: Manages a chain of operations, allowing adding, removing, counting, and iterating over operations.
- **OperationNode**: Represents a node in an operation chain, containing an operation and a reference to the next node.
- **OperationStatusChecker**: Checks the status of operations, providing methods to get the status of specific or all operations in the queue.
- **PersistentOperationChecker**: Manages and checks persistent operations, ensuring that necessary operations like `ConsoleOperation` and `ResourceMonitorOperation` are running.
- **OperationLifecycleManager**: Manages the overall lifecycle of operations, handling starting, stopping, pausing, and resuming operations.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

For getting started instructions, including prerequisites and installation steps, please refer to the [Getting Started section](https://github.com/lane-neuro/neurobehavioral-analytics-suite#getting-started) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Usage instructions for the Operation Manager module will be provided at a later date.

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