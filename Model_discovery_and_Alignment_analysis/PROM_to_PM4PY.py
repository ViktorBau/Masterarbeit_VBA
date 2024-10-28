import json
import os
import pickle
import re

def read_json_to_dict(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def PROM_result_list_to_PM4PY_alignment(result_list):
    alignments = []
    test = set()
    for result in result_list.values():
        alignment = {'alignment':[]}
        step_types = [s.strip() for s in result["stepTypes"][1:-1].split(",")]
        node_instances = [n.strip() for n in result["nodeInstance"][1:-1].split(",")]
        for step_type, node_instance in zip(step_types, node_instances):
            test.add(step_type)
            if step_type =="Sync move" or step_type == " Sync move":
                move = tuple([node_instance, node_instance])
                alignment['alignment'].append(move)
            elif step_type == "Model move" or step_type == " Model move":
                move = tuple([">>",node_instance])
                alignment['alignment'].append(move)
            elif step_type == "Log move" or step_type == " Log move":
                move = tuple([re.sub(r'\+complete', '', node_instance, flags=re.IGNORECASE), ">>"])
                alignment['alignment'].append(move)
            elif step_type == "Invisible step" or step_type == " Invisible step":
                move = tuple([">>",None])
                alignment['alignment'].append(move)

        alignments.append(alignment)

    return alignments


def PROM_result_list_to_PM4PY_alignment_for_all_in_folder(path_to_event_log, algorithm_names):
    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        path_to_PROM_alignments = os.path.join(path_to_model, "PROM_alignment_results")
        for algorithm in algorithm_names:
            file_name = f"resultList_{algorithm}.json"
            with open(os.path.join(path_to_PROM_alignments, file_name), "r") as json_file:
                alignment = json.load(json_file)
                sorted_alignemnt = {k: alignment[k] for k in sorted(alignment.keys(), key=lambda x: int(x))}

                PM4PY_alignment = PROM_result_list_to_PM4PY_alignment(sorted_alignemnt)

                with open(os.path.join(path_to_model, f"alignment_{algorithm}.pickle"), "wb") as file:
                    pickle.dump(PM4PY_alignment, file)

def PROM_planning_based_variants_to_PM4PY(planning_based_alignment):
    """
       Converts the planning-based alignment variants from ProM format to PM4PY format.


       Parameters:
       planning_based_alignment (dict): JSON output from PROM planning-based alignment.
       Returns:
       dict: A dictionary with an example trace for each variant. and its alignment in PM4PY format.
       """
    alignments_variants = {}
    test = set()
    for trace_name,result in zip(planning_based_alignment.keys(),planning_based_alignment.values()):
        alignments_variants[trace_name] = []
        alignment = []
        step_types = [s.strip() for s in result["stepTypes"][1:-1].split(",")]
        stepLabels = result["stepLabels"]
        for step_type, node_instance in zip(step_types, stepLabels):
            test.add(step_type)
            if step_type == "Move in Both":
                event_name = node_instance.split("P: ", 1)[1].split(" {}  L:")[0]
                move = tuple([event_name, event_name])
                alignment.append(move)
            elif step_type == "Move in Model":
                event_name = node_instance.split("P: ", 1)[1].split(" {}  L:")[0]
                move = tuple([">>", event_name])
                alignment.append(move)
            elif step_type == "Move in Log":
                event_name = re.split(r'\+complete \{\}', node_instance, flags=re.IGNORECASE)[0].split("L: ", 1)[1]
                move = tuple([event_name, ">>"])
                alignment.append(move)
            elif step_type == "Invisible Move":
                move = tuple([">>", None])
                alignment.append(move)

        alignments_variants[trace_name] = alignment

    return alignments_variants

def PROM_planning_based_variants_to_all_alignments_PM4PY(planning_based_variants_PM4PY ,mapping, event_log):
    """
    Converts the planning-based alignment variants from ProM format to PM4PY format for all traces in the event log.

    Parameters:
    planning_based_variants_PM4PY (dict): Output from PROM_planning_based_variants_to_PM4PY.
    mapping (dict): JSON output from PROM planning-based alignment mapping variants to traces
    Returns:
    list: A list that includes all traces and their alignments in PM4PY format.
    """
    alignments = []
    number_of_events = len(event_log)
    for _ in range(number_of_events):
        alignments.append(None)
    for variant in planning_based_variants_PM4PY.keys():
        for trace in mapping[f'{variant}']:
            alignments[trace-1] = {"alignment":planning_based_variants_PM4PY[variant]}
    if None in alignments:
        print("Something went wrong with the mapping")





    return alignments

def PROM_planing_based_to_PM4PY_alignment_for_all_in_folder(path_to_event_log):
    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]


    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        path_to_PROM_alignments = os.path.join(path_to_model, "PROM_alignment_results")

        file_name_alignment = f"planning_based_alignment.json"
        with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
            event_log = pickle.load(file)
        with open(os.path.join(path_to_PROM_alignments, file_name_alignment), "r") as json_file:
            planning_based_alignment = json.load(json_file)

        file_name_mapping = f"planning_based_alignment_mapping_variant_traces.json"
        with open(os.path.join(path_to_PROM_alignments, file_name_mapping), "r") as json_file:
            mapping = json.load(json_file)
        planning_based_variants_PM4PY = PROM_planning_based_variants_to_PM4PY(planning_based_alignment)
        planning_based_alignment_PM4PY = PROM_planning_based_variants_to_all_alignments_PM4PY(
            planning_based_variants_PM4PY, mapping, event_log)

        with open(os.path.join(path_to_model, f"alignment_PROM_planing_based.pickle"), "wb") as file:
            pickle.dump(planning_based_alignment_PM4PY, file)

def PROM_all_optimal_varaints_to_PM4PY(all_optimal_alignments,mapping_variants_traces, event_log):
    """
          Converts all optimal alignments from ProM format to PM4PY format.


          Parameters:
          all_optimal_alignments (dict): JSON output from PROM all_optimal_alignments.
          Returns:
          dict: A dictionary with an example trace for each variant. And all of its possible alignments in PM4PY format.
          And for each trace variant their trece indicies.
          """




    alignments_variants = {}
    test = set()
    all_optimal_alignments_sorted = {k: all_optimal_alignments[k] for k in
                                     sorted(all_optimal_alignments.keys(), key=lambda x: x)}

    mapping_sorted = {k: mapping_variants_traces[k] for k in
                                     sorted(mapping_variants_traces.keys(), key=lambda x: x)}

    if (not mapping_sorted.keys() == all_optimal_alignments_sorted.keys()):
        raise ValueError("The keys of the mapping and the all_optimal_alignments are not the same")
    for trace_variant,key in zip(all_optimal_alignments_sorted.values(),all_optimal_alignments_sorted.keys()):

        alignments_variants[key] = {"trace_indicies":mapping_sorted[key], "info":trace_variant["info"],"alignments":[]}
        for stepTypes,nodeInstances in zip(trace_variant["stepTypes"],trace_variant["nodeInstance"]):
            alignment = []
            for step_type, node_instance in zip(stepTypes, nodeInstances):

                test.add(step_type)
                if step_type == "Sync move":
                    move = tuple([node_instance, node_instance])
                    alignment.append(move)
                elif step_type == "Model move":
                    move = tuple([">>", node_instance])
                    alignment.append(move)
                elif step_type == "Log move":
                    move = tuple([re.sub(r'\+complete', '', node_instance, flags=re.IGNORECASE), ">>"])
                    alignment.append(move)
                elif step_type == "Invisible step":
                    move = tuple([">>", None])
                    alignment.append(move)

            alignments_variants[key]["alignments"].append(alignment)

    return alignments_variants

def PROM_all_optimal_varaints_to_PM4PY_alignment_for_all_in_folder(path_to_event_log):
    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        path_to_PROM_alignments = os.path.join(path_to_model, "PROM_alignment_results")

        with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
            event_log = pickle.load(file)

        file_name_alignment = f"PROM_all_optimal.json"
        with open(os.path.join(path_to_PROM_alignments, file_name_alignment), "r") as json_file:
            all_optimal_alignments = json.load(json_file)

        file_name_mapping = f"all_optimal_alignments_mapping_variant_traces.json"
        with open(os.path.join(path_to_PROM_alignments, file_name_mapping), "r") as json_file:
            mapping_variants_traces = json.load(json_file)

        all_optimal_variants = PROM_all_optimal_varaints_to_PM4PY(all_optimal_alignments, mapping_variants_traces ,event_log)

        path_to_all_optimal = os.path.join(path_to_model, 'all_optimal_alignments')

        if not os.path.exists(path_to_all_optimal):
            os.makedirs(path_to_all_optimal)

        with open(os.path.join(path_to_all_optimal, 'all_optimal_variants_PM4PY.pickle'), 'wb') as file:
            pickle.dump(all_optimal_variants, file)
