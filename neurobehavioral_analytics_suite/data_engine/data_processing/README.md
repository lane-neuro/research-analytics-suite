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
<div align="center">
  <p align="center">
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/network/members">
      <img src="https://img.shields.io/github/forks/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="Forks">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/stargazers">
      <img src="https://img.shields.io/github/stars/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="Stars">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/issues">
      <img src="https://img.shields.io/github/issues/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="Issues">
    </a>
    <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/lane-neuro/neurobehavioral-analytics-suite.svg?style=for-the-badge" alt="License">
    </a>
    <a href="https://linkedin.com/in/lane14">
      <img src="https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555" alt="LinkedIn">
    </a>
  </p>

  <!-- PROJECT LOGO -->
  <a href="https://github.com/lane-neuro/neurobehavioral-analytics-suite">
    <img src="../../images/centered_banner_white_black_text_1800x700.png" alt="NBAS" style="max-width: 75%; height: auto;">
  </a>
  <p>Author: <a href="#contact">Lane</a></p>
</div>



# /data_engine/data_processing
### Part of NeuroBehavioral Analytics Suite (NBAS)
<div>
  <p align="left">
The 'data_engine/data_processing' subpackage handles data extraction, transformation, and loading operations using Dask within the NeuroBehavioral Analytics Suite (NBAS).
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

The `data_processing` subpackage within the Data Engine package defines and manages various data processing operations used in the NeuroBehavioral Analytics Suite (NBAS). The key components of this subpackage include:

- **DataExtractor**: A class to extract data from various sources using Dask.
- **DataLoader**: A class to load transformed data to a destination using Dask.
- **DataTransformer**: A class to transform data using various functions and Dask.

### DataExtractor
The `DataExtractor` class is used to extract data from various sources using Dask. It initializes the data source and format, uses Dask for parallel data extraction, and handles different data formats such as JSON and CSV.

### DataLoader
The `DataLoader` class loads transformed data to a specified destination using Dask. It initializes the transformed data and destination, validates the data, and uses Dask to perform the loading operation efficiently.

### DataTransformer
The `DataTransformer` class transforms data using specified functions and Dask. It initializes the data and transformation function, applies the transformation using Dask, and handles various transformation functions like map, filter, reduce, and more.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

For getting started instructions, including prerequisites and installation steps, please refer to the [Getting Started section](https://github.com/lane-neuro/neurobehavioral-analytics-suite#getting-started) of the main repository README.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Usage instructions for the Data Processing subpackage will be provided at a later date.

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
