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

# NeuroBehavioral Analytics Suite (NBAS)
### Gire Lab, University of Washington
  <p align="center">
    NeuroBehavioral Analytics Suite (NBAS) is a collection of tools developed in Python with a focus on the aggregation and analysis of neurobehavioral data deriving from a multitude of input sources across professional and academic neuroscientific research projects. 
    <br /> Author: <a href="#contact">Lane</a> (Gire Lab, University of Washington)
    <br />
    <br /> Prototype for NBAS was written in MATLAB & can be found at <a href="https://github.com/lane-neuro/RealTimeOdorNavigation">lane-neuro/RealTimeOdorNavigation</a>
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
      <a href="#about-the-project">About The Project</a>
      <!-- <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul> -->
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <!-- <li><a href="#roadmap">Roadmap</a></li> -->
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <!-- <li><a href="#acknowledgments">Acknowledgments</a></li> -->
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
NeuroBehavioral Analytics Suite (NBAS) is designed to be the primary interface for neuroscientific analysis with (3) components/branches:
* Data Management Engine (DME) - allows for filtering and aggregation of large, complex datasets from multiple sources (i.e., pixel-tracking technology, accelerometer readings, voltage-output from analog sources, etc.)
* Analytics - provides a suite of tools for the analysis of neurobehavioral data from the DME, including statistical analysis, machine learning, and data visualization
  * Preloaded Functions
  * Custom / User-Defined Functions - allows for the development & implementation of custom functions developed by the user
* Future Integration with other tools (i.e., [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut))

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ### Built With
...
* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites
Once you have cloned the repo (see <a href="#installation">Installation</a>), you will need to install the required packages. This can be done in one of two ways:
* If you are using <a href="https://www.anaconda.com/">Anaconda</a> as a virtual environment, you can use the supplied `environment.yml` file to create a new environment with all the required packages. To do this, run the following command in the terminal:
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



<!-- USAGE EXAMPLES -->
## Usage
> <i>To be implemented at a later date.</i>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP
## Roadmap



<p align="right">(<a href="#readme-top">back to top</a>)</p>
 -->


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



<!-- ACKNOWLEDGMENTS
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->


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
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
