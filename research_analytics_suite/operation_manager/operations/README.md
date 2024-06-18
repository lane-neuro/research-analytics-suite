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
    <img src="../../../research_analytics_suite/images/centered_banner_white_black_text_1800x700.png" alt="Research Analytics Suite Banner" style="max-width: 75%; height: auto;">
  </a>
  <p>Author: <a href="#contact">Lane</a></p>
</div>


# /operation_manager/operations
### Part of Research Analytics Suite (RAS)
<div>
  <p align="left">
The `operation_manager/operations` subpackage handles the definition and management of operations within the RAS.
<br />
<br />
    <!-- <a href="https://github.com/lane-neuro/research-analytics-suite"><strong>Explore the docs »</strong></a> -->
    <br />
    <!-- <a href="https://github.com/lane-neuro/research-analytics-suite">View Demo</a>
    ·
    <a href="https://github.com/lane-neuro/research-analytics-suite/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/lane-neuro/research-analytics-suite/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
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

The `operations` subpackage within the `operation_manager` module defines and manages various operations in the Research Analytics Suite (RAS). The key components of this subpackage include:

- **BaseOperation**: An abstract base class that provides a common interface for all operations. It defines methods like `execute`, `start`, `pause`, `stop`, `resume`, and others which must be implemented by any subclass.
- **Operation**: A concrete implementation of the `BaseOperation` class, responsible for managing tasks, tracking progress, and handling exceptions during execution.
- **CustomOperation**: A subclass of `Operation` that handles custom operations requiring function processing. It allows setting the function to be processed and managing its execution.

### BaseOperation
The `BaseOperation` class provides a common interface for all operations in the RAS, requiring child classes to implement essential methods for operation management, such as `execute`, `start`, `pause`, `stop`, `resume`, etc.

### Operation
The `Operation` class represents a task that can be managed through various states like started, stopped, paused, resumed, and reset. It tracks the progress of the task and handles any exceptions that occur during execution.

### CustomOperation
The `CustomOperation` class extends `Operation` to handle custom operations that require function processing. It allows users to set a function to be executed and manages its execution, including handling exceptions and tracking the status and result of the operation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

For getting started instructions, including prerequisites and installation steps, please refer to the [Getting Started section](https://github.com/lane-neuro/research-analytics-suite#getting-started) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Usage instructions for the Operations subpackage will be provided at a later date.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such a great place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

For contributing guidelines, please refer to the [Contributing section](https://github.com/lane-neuro/research-analytics-suite#contributing) of the main repository README.

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

Project Link: [Research Analytics Suite](https://github.com/lane-neuro/research-analytics-suite)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
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
