[![build-status-image]][travis]

# Overview

PyPlan is a Python library for building a planning engine to automatically decide the set of actions an agent should execute
in order to accomplish certain goal. Typical domains for application are autonomous robots, unmanned vehicles and
games.

# Requirements

No external libraries are required only Python3.

# Installation

The library is not ready to production, so it has not been added to the Python Package Index. Checkout the
repository and import it on your own projects.

# Current Status

The library is in early development and it is not ready for production use. This kind of libraries should be fast and 
Python does not help on this matter, also still no optimizations of the code have been made. 

For the moment the goal is to make the library extensible and easy to use. Another of the main goals is that the library 
can be integrated with external data sources for both querying required environmental data and also to save the nodes when 
big search spaces need to be explored.
 

# Roadmap

* Include the ability to perform logic unifications as next step towards building automatic planning engines.
* Integration with external data sources. Redis maybe the first candidate.
* Creation of an intermediate DSL language to define the domains and configure the solvers. The use of YAML could
  be a first approach.

# Credits

Oscar J. Garcia Perez, @oscgrc on Twitter.

# License

PyPlan is licensed under the terms of the MIT license (see the file LICENSE).
