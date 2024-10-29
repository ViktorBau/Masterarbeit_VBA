# Masterarbeit_VBA
This Repo contains the code and suplementary resulst for my Master Thesis tilted: Assessing the Disagreement between Alignment Algorithms and their Impact on Process Analysis

# Model Discovery and Alignment

The process first performs model discovery, then takes the alignment results calculated by the PROM plugins and converts them to a harmonized format. These harmonized results are then used for analysis and visualization of the alignment results. The script [full_pipeline.py](./Model_discovery_and_Alignment_analysis/full_pipeline.py) contains the necessary functions to recreate the results presented in the thesis.

## Project Structure

The project is based on a hierarchical folder structure that the functions iterate through:

1. **Event Log**: Start with a folder containing the event log.
2. **Model Discovery**:  create_save_PN_Alignment_inductive(path_to_event_log) creates a separate folder for each discovered model.
3. **Alignment results**: The alignemtns calculated for each model by the Jave code are saved in its respective folder.
4. **Analysis&Visualization**: The functions in [full_pipeline.py](./Model_discovery_and_Alignment_analysis/full_pipeline.py) also save their results in the models folders



# Alignment Calculation with Prom Plugins

This module uses plugins from the PROM framework to execute tasks without the need for the PROM interface. It offers the following packages/plugins:

- **Alignment Package**: Calculates one optimal alignment using the class:
  [One_optimal_alignments.java](./Alignment_calculation_with_Prom/src/alignment_calculation/One_optimal_alignments.java)

- **Planning-Based Alignment**: Calculates one optimal alignment based on a PDDL and a planner.
  [Planning_based_one_optimal.java](./Alignment_calculation_with_Prom/src/alignment_calculation/Planning_based_one_optimal.java)

- **Replay a Log on Petri Net for All Optimal Alignments**: This plugin was initially used with a worker that sends SLURM jobs to a university cluster, but it can also be used independently.
  [All_optimal_alignments.java](./Alignment_calculation_with_Prom/src/alignment_calculation/All_optimal_alignments.java)


# Project Setup Guide

## Model dicovery and alignment analysis- Python

1. Clone the repository
2. Install the requirements

## Alignment calculation  with Prom plugins- Java

The Java project requires additional setup steps before execution:

1. **Dependency Management with Ivy for PROM**
   - Ivy dependency management (IvyDE) is no longer actively developed and isn’t available in the Eclipse Marketplace. You will need to install it from an archived source.
     - In Eclipse, go to `Help -> Install Software`.
     - Enter the following URL to install IvyDE: [https://archive.apache.org/dist/ant/ivyde/updatesite/](https://archive.apache.org/dist/ant/ivyde/updatesite/)
   - After installation, in Eclipse:
     - Right-click on `ivy.xml` and select "Add Ivy Library."
   - The dependencies should begin installing automatically.

2. **Add Native Library Directory**
   - The `native_lib` directory needs to be added to the build path.

3. **Planning-Based Algorithm Requirements**
   - This algorithm relies on an older version of Fast Downward and requires Python 2.7.
     - Install Python 2.7.
     - Add the path to the Python interpreter in the following class:  
       `Alignment_calculation_with_Prom/src/alignment_calculation/Planning_based_one_optimal.java`
