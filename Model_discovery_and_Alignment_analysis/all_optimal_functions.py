
import os
import pandas as pd
import pickle
import random
# from functions import *
from functions import color_cells
from functions import read_and_save_event_log

from functions import _get_move_type
from PROM_to_PM4PY import PROM_all_optimal_varaints_to_PM4PY_alignment_for_all_in_folder
######### Visualization for all optimal alignments #########

def create_df_with_all_optimal(path_to_model, return_variant_trace_mapping = False, specific_trace = None,filter_tau =True, filter_duplicates_after_tau= True):
    """
        This function creates a DataFrame wiht the first column being the trace name of an example trace for each variant
        and the following columns being optimal alignments for the tace variant.

        Filter_tau: If True, the function filters the tau events from the alignments
        Filter_duplicates_after_tau: If the tau envents are filtered out many possbile alignemnts are the same, they only differ in ordering of the tau events.


        """
    path_to_all_optimal = os.path.join(path_to_model, 'all_optimal_alignments', 'all_optimal_variants_PM4PY.pickle')

    with open(path_to_all_optimal, 'rb') as file:
        all_optimal_variants = pickle.load(file)

    if return_variant_trace_mapping:
        variant_trace_mapping = {}
    list_alignments = []
    if specific_trace != None:
        all_optimal_variants = {specific_trace: all_optimal_variants[specific_trace]}
    for variant,key in zip(all_optimal_variants.values(), all_optimal_variants.keys()):
        set_of_alignments = set()
        for alignment in variant["alignments"]:
            if filter_tau:
                alignment = [event for event in alignment if event != tuple(['>>', None])]
            if filter_duplicates_after_tau:
                string_of_alignment = "".join([str(tup) for tup in alignment])
                if string_of_alignment in set_of_alignments:
                    continue
                set_of_alignments.add(string_of_alignment)
            row = [key,len(variant["trace_indicies"])]
            if return_variant_trace_mapping:
                variant_trace_mapping[key] = variant["trace_indicies"]
            row.extend(alignment)
            list_alignments.append(row)



    # Create a DataFrame
    all_optimal_df = pd.DataFrame(list_alignments).rename( columns={0: "Trace Variant", 1: "Frequency"})

    if return_variant_trace_mapping:
        return all_optimal_df, variant_trace_mapping
    return all_optimal_df

def row_borders(row, index, df):
    if index > 0 and df.loc[index, "Trace Variant"] != df.loc[index - 1, "Trace Variant"]:
        return ['border-top: 10px solid white' for _ in row]
    else:
        return ['' for _ in row]
def create_html_with_all_optimal_for_all_in_folder(path_to_event_log):
    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]
    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        all_optimal_df = create_df_with_all_optimal(path_to_model)
        all_optimal_df_filtered = all_optimal_df.groupby('Trace Variant').filter(lambda x: len(x) > 1)
        all_optimal_styled_df = all_optimal_df_filtered.fillna("").style.map(color_cells)
        all_optimal_styled_df = all_optimal_styled_df.apply(
            lambda row: row_borders(row, row.name,all_optimal_df ), axis=1)

        all_optimal_styled_html = all_optimal_styled_df.to_html()
        with open(os.path.join(path_to_model, "all_optimal_alignments","all_optimal_alignments.html"), "w") as file:
            file.write(all_optimal_styled_html)

def from_all_optimal_alignments_choose_random(path_to_model,len_event_log, all_optimal_df, variant_trace_mapping):
    all_optimal_df = all_optimal_df.drop(columns=['Frequency'])

    alignment_list = [None] * len_event_log

    grouped_df = all_optimal_df.groupby('Trace Variant')


    for trace_variant, group in grouped_df:
        random_row = group.sample(n=1)
        alignment_dict = {"alignment": random_row.drop(columns=['Trace Variant']).values.tolist()[0]}
        indices = variant_trace_mapping[trace_variant]
        for index in indices:
            alignment_list[index-1] = alignment_dict

    # Save the list as a pickle
    with open(os.path.join(path_to_model, "alignment_ALL_OPTIMAL_random.pickle"), "wb") as file:
        pickle.dump(alignment_list, file)

def from_all_optimal_alignments_choose_sync_model_log(path_to_model, len_event_log, all_optimal_df, variant_trace_mapping):
    all_optimal_df = all_optimal_df.drop(columns=['Frequency'])

    alignment_list = [None] * len_event_log

    grouped_df = all_optimal_df.groupby('Trace Variant')

    for trace_variant, group in grouped_df:
        trace = group.drop(columns=['Trace Variant']).reset_index(drop=True)
        for col in trace.columns:
            if trace.shape[0] <= 1:
                break

            move_types = trace[col].apply(_get_move_type)

            if "sync_move" in move_types.values:
                trace = trace[move_types == "sync_move"]
            elif "model_move" in move_types.values:
                trace = trace[move_types == "model_move"]


        alignment_dict = {"alignment": trace.values.tolist()[0]}
        indices = variant_trace_mapping[trace_variant]
        for index in indices:
            alignment_list[index - 1] = alignment_dict

    # Save the list as a pickle
    with open(os.path.join(path_to_model, "alignment_ALL_OPTIMAL_sync_model_log.pickle"), "wb") as file:
        pickle.dump(alignment_list, file)

def from_all_optimal_alignments_choose_sync_model_log_for_all_in_folder(path_to_event_log):

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
            event_log = pickle.load(file)

        len_event_log = len(event_log)
        all_optimal_df, variant_trace_mapping = create_df_with_all_optimal(path_to_model, return_variant_trace_mapping=True)

        from_all_optimal_alignments_choose_sync_model_log(path_to_model, len_event_log, all_optimal_df, variant_trace_mapping)

def from_all_optimal_alignments_choose_random_for_all_in_folder(path_to_event_log):


    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]



    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
            event_log = pickle.load(file)

        len_event_log = len(event_log)
        all_optimal_df, variant_trace_mapping = create_df_with_all_optimal(path_to_model, return_variant_trace_mapping=True)


        from_all_optimal_alignments_choose_random(path_to_model, len_event_log, all_optimal_df, variant_trace_mapping)

def from_all_optimal_read_and_save_event_log_excluded(path_to_event_log):

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]


    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        read_and_save_event_log(path_to_model, "Event_log_excluded_traces.xes")

def calculate_jaccard(all_optimal_df):
    all_optimal_df = all_optimal_df.drop(columns=['Frequency'])

    grouped_df = all_optimal_df.groupby('Trace Variant')


    all_optimal_jaccard = {}

    for trace_variant, group in grouped_df:
        if len(group) == 1:
            continue
        move_occourance = {}
        trace = group.drop(columns=['Trace Variant']).reset_index(drop=True)

        for col in trace.columns:
            for row in trace.index:
                move = trace.loc[row, col]
                if move == None:
                    continue
                if not move_occourance.__contains__(move) :
                    zeros_list = [0] * len(trace)
                    move_occourance[move] = zeros_list

                move_occourance[move][row] += 1

        sum_of_max_occurance = 0
        sum_of_min_occurance = 0
        for key, value in move_occourance.items():
            sum_of_max_occurance += max(value)
            sum_of_min_occurance += min(value)

        jaccard_distance = sum_of_min_occurance / sum_of_max_occurance

        all_optimal_jaccard[trace_variant] = {"jaccard_distance" : jaccard_distance, "number_of_alignments": len(trace)}

        df = pd.DataFrame(all_optimal_jaccard).transpose().sort_values(by="jaccard_distance")


    return df

def calculate_jaccard_for_all_in_folder(path_to_event_log):

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        all_optimal_df = create_df_with_all_optimal(path_to_model)
        jaccard = calculate_jaccard(all_optimal_df)

        jaccard.to_html(os.path.join(path_to_model, "all_optimal_alignments","jaccard_distance.html"))


