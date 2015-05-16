# ml-bench

Attempt to create a tool able to benchmark and compare the performance of different machine learning algorithm.

This tool intend to provide a comprehensive interface to implements many different algorithms, and run them on different problems and with different datasets. The types that will be handled are:
* Optimization
* Clustering
* Classification

## Setup the environment

You will need to install **python** in version 2.7 and **pip**. Then, run the following commands:

```
> pip install virtualenv
> virtualenv .env --no-site-package
> ./go.sh
```

The last command will install all required packages, then run the server of the application.

## Launch the application

The following command will start the application's server:
```
> ./go.sh
```

Then, access to the url: `localhost:5000` in your browser to display the main UI.
