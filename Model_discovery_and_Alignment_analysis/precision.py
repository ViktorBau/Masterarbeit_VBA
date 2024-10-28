import pm4py
import pm4py.algo.conformance.alignments
import pm4py.algo.evaluation.precision
import os
import pickle
import pandas as pd

def alignment_to_event_log(alignment):
    """
        takes the alignments of an event log and filters out all taus and log moves and creates a new event log
        """
    event_log = []

    for align_dict in alignment:
        align_dict_filtered = {}
        align_dict_filtered["alignment"]= [item for item in align_dict["alignment"] if item is not None]
        filtered_tuples = [tup for tup in align_dict_filtered['alignment'] if tup[1] != '>>' and tup[1] != None]
        inner_list = [{'concept:name': tup[1]} for tup in filtered_tuples]
        event_log.append(inner_list)

    return event_log


path_to_model = r"C:\Users\bauma\Desktop\Masterarbeit\Alignments\sepsis_cases\Model_PN_inductive_noise_treshold_0.4"
algorithm_names = [ "PROM_AStar", "PROM_planing_based", "ALL_OPTIMAL_random", "ALL_OPTIMAL_sync_model_log"]
# Assume you already have the process model (petri net, initial marking, final marking)
net, initial_marking, final_marking = pm4py.read.read_pnml(os.path.join(path_to_model, "Petri_net.pnml"))

# Load the event log
with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
    log = pickle.load(file)

precision_results = {}
log_tests = []



def calculate_precission_for_all_alignments (path_to_event_log, algorithm_names):
    """
            calculates the precision for each alignment of each model in the folder path_to_event_log
            a repaired log is created from the alignment and the precision is calculated
         """

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    precision_df = pd.DataFrame(index=all_models, columns=algorithm_names)

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        net, initial_marking, final_marking = pm4py.read.read_pnml(os.path.join(path_to_model, "Petri_net.pnml"))

        for algorithm in algorithm_names:
             if os.path.isfile(os.path.join(path_to_model, f"alignment_{algorithm}.pickle")):
                            file_name = f"alignment_{algorithm}.pickle"

                            with open(os.path.join(path_to_model, file_name), "rb") as file:
                                alignment = pickle.load(file)


                            repaired_log = alignment_to_event_log(alignment)
                            precision = pm4py.algo.evaluation.precision.algorithm.apply(repaired_log, net, initial_marking,
                                                                                        final_marking)
                            precision_df.loc[dir_model, algorithm] = precision

    latex_filename_txt = os.path.join(path_to_model, "precision.txt")
    latex_filename_html = os.path.join(path_to_model, "precision.html")

    # Generate LaTeX code
    latex_code = precision_df.to_latex()

    # Save LaTeX code as .txt file
    with open(latex_filename_txt, 'w') as f:
        f.write(latex_code)

    # Save DataFrame as .html file
    precision_df.to_html(latex_filename_html)

