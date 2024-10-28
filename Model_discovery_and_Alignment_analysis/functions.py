import os
import pandas as pd
import pm4py
import re
import pickle



def read_and_save_event_log(path_to_event_log, name_event_log_file):
    path_event_log = os.path.join(path_to_event_log, name_event_log_file)

    if name_event_log_file.endswith(".xes"):
        log = pm4py.read_xes(path_event_log)
    else:
        raise Exception("Event Log file is not in xes format")

    log = pm4py.convert_to_event_log(log)

    with open(os.path.join(path_to_event_log, "Event_log.pickle"), "wb") as file:
        pickle.dump(log, file)

def create_save_PN_Alignment_inductive(path_to_event_log, noise_threshold=0.2):
    # Load the event log
    with open(os.path.join(path_to_event_log, "Event_log.pickle"), "rb") as file:
        log = pickle.load(file)


    name_model = "Model_PN_inductive_noise_treshold_" + str(noise_threshold)
    new_folder = os.path.join(path_to_event_log, name_model)
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)

    # Mine Process-Model with inductive Miner

    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold=noise_threshold)

    # Save the Petri net model
    pm4py.write.write_pnml(net, initial_marking, final_marking,
                           os.path.join(new_folder, "Petri_net.pnml"))

    pm4py.save_vis_petri_net(net, initial_marking, final_marking, os.path.join(new_folder, f"Petri_net{name_model}.svg"))

def read_PN_and_save_svg(path_to_event_log, noise_threshold):
    name_model = "Model_PN_inductive_noise_treshold_" + str(noise_threshold)
    new_folder = os.path.join(path_to_event_log, name_model)
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)

    # Mine Process-Model with inductive Miner

    net, initial_marking, final_marking = pm4py.read_pnml(os.path.join(new_folder, f"petri_net.pnml"))

    pm4py.save_vis_petri_net(net, initial_marking, final_marking, os.path.join(new_folder, f"Petri_net{name_model}.svg"))
def create_trace_variant_to_alignemnt_dict(log, alignments, filter_tau=True):
    ### This function create a dict {Trace_varaint: { Alignment : [], frequency: X, trace_names [...]}}

    trace_variant_alignment = {}
    if type(alignments) == tuple:
        alignments = alignments[0]
    for trace, alignment in zip(log, alignments):
        trace_str = ""
        trace_name = trace.attributes["concept:name"]                                                                                                           
        for event in trace._list:
            if trace_str == "":
                trace_str = event['concept:name']
            else:
                trace_str += ", " + event['concept:name']
        if trace_str in trace_variant_alignment:
            trace_variant_alignment[trace_str]["frequency"] += 1
            trace_variant_alignment[trace_str]["trace_names"].append(trace_name)
        else:
            trace_variant_alignment[trace_str] = {"alignment": alignment['alignment'], "frequency": 1,
                                                  "trace_names": [trace_name]}

    if filter_tau:
        for trace_variant in trace_variant_alignment.keys():
            trace_variant_alignment[trace_variant]["alignment"] = [event for event in
                                                                   trace_variant_alignment[trace_variant]["alignment"]
                                                                   if event != tuple(['>>', None]) and event !=  None]

    return trace_variant_alignment
def _get_move_type(move):
    move = str(move)
    if move == "('>>', None)":
        return "invisible_move"
    elif move.startswith("('>>',"):
        return "model_move"
    elif move.endswith(", '>>')"):
        return "log_move"
    elif move.startswith("(") and move.endswith(")") and '>>' not in move:
        return "sync_move"
def color_cells(val):
    val = str(val)
    if isinstance(val, str):
        if _get_move_type(val) == "invisible_move":
            color = '#808080'
        elif  _get_move_type(val) == "model_move":
            color = '#BF40BF'
        elif  _get_move_type(val) == "log_move":
            color = '#FFFF00'
        elif  _get_move_type(val) == "sync_move":
            color = '#90EE90'
        elif val == "":
            color = 'white'
        else:
            color = '#ADD8E6'
    else:
        color = 'black'
    return 'background-color:' + color

def row_borders(row, index, num_algos=3):
    if index % num_algos == (num_algos-1):
        return ['border-bottom: 10px solid white' for _ in row]
    else:
        return ['' for _ in row]
def compare_alignments(path_to_event_log, algorithm_names):
    from all_optimal_functions import create_df_with_all_optimal

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]
    Summary = []
    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        with open(os.path.join(path_to_model, "Event_log.pickle"), "rb") as file:
            log = pickle.load(file)

        alignments = {}
        # Loop through each pickle file that starts with "alignment_"
        for algorithm in algorithm_names:
            if os.path.isfile(os.path.join(path_to_model, f"alignment_{algorithm}.pickle")):
                file_name = f"alignment_{algorithm}.pickle"
                # Load the pickle file
                with open(os.path.join(path_to_model, file_name), "rb") as file:
                    alignment = pickle.load(file)

                # Apply the create_trace_variant_to_alignment_dict function
                alignments[algorithm] = create_trace_variant_to_alignemnt_dict(log, alignment)

        occurance_of_disagreement = 0
        number_of_diasgreeing_trace_variants = 0
        occurance_of_disagreement_order = 0
        number_of_diasgreeing_trace_variants_order = 0
        occurance_of_disagreement_set = 0
        number_of_diasgreeing_trace_variants_set = 0
        differences_list_of_rows_order = []
        differences_list_of_rows_set = []

        if not alignments == {}:
            for trace_variant in alignments[next(iter(alignments))].keys():
                list_alignments = []
                for algorithm in algorithm_names:
                    list_alignments.append(alignments[algorithm][trace_variant]["alignment"])

                same_alignments = all(list_alignments[0] == other for other in list_alignments[1:])
                different_sets_of_alignments = all(
                    set(list_alignments[0]) == set(other) for other in list_alignments[1:])

                if (same_alignments):
                    pass
                elif (different_sets_of_alignments):
                    for algorithm in algorithm_names:
                        row = []
                        row.append(alignments[algorithm][trace_variant]["trace_names"][0])
                        row.append(round(alignments[algorithm_names[0]][trace_variant]["frequency"], 1))
                        row.append(algorithm)
                        row += (alignments[algorithm][trace_variant]["alignment"])
                        differences_list_of_rows_order.append(row)

                    occurance_of_disagreement += alignments[algorithm_names[0]][trace_variant]["frequency"]
                    number_of_diasgreeing_trace_variants += 1
                    occurance_of_disagreement_order += alignments[algorithm_names[0]][trace_variant]["frequency"]
                    number_of_diasgreeing_trace_variants_order += 1

                elif (not different_sets_of_alignments):
                    for algorithm in algorithm_names:
                        row = []
                        row.append(alignments[algorithm][trace_variant]["trace_names"][0])
                        row.append(round(alignments[algorithm_names[0]][trace_variant]["frequency"], 1))
                        row.append(algorithm)
                        row += (alignments[algorithm][trace_variant]["alignment"])
                        differences_list_of_rows_set.append(row)


                    occurance_of_disagreement += alignments[algorithm_names[0]][trace_variant]["frequency"]
                    number_of_diasgreeing_trace_variants += 1
                    occurance_of_disagreement_set += alignments[algorithm_names[0]][trace_variant]["frequency"]
                    number_of_diasgreeing_trace_variants_set += 1



            #style tabel for different alignments when considering the order and ignoring the once with different sets
            different_alignemts_order_df = pd.DataFrame(differences_list_of_rows_order).fillna("")
            different_alignemts_order_df = different_alignemts_order_df.rename(
                columns={0: "Trace Variant", 1: "Frequency", 2: "Algorithm"})
            different_alignemts_order_styled_df = different_alignemts_order_df.style.map(color_cells)
            different_alignemts_order_styled_df = different_alignemts_order_styled_df.set_caption(
                f"<b>Disagreeing Alignments with the same moves but different ordering for {dir_model}</b>")
            different_alignemts_order_styled_df = different_alignemts_order_styled_df.apply(lambda row: row_borders(row, row.name, num_algos=len(algorithm_names)), axis=1)



            different_alignemts_order_html = different_alignemts_order_styled_df.to_html()
            with open(os.path.join(path_to_model, "trace_variants_disagreeing_alignments_order.html"), "w") as file:
                file.write(different_alignemts_order_html)


            # style tabel for different alignments when not considering the order
            different_alignemts_set_df = pd.DataFrame(differences_list_of_rows_set).fillna("")
            different_alignemts_set_df = different_alignemts_set_df.rename(
                columns={0: "Trace Variant", 1: "Frequency", 2: "Algorithm"})
            different_alignemts_set_styled_df = different_alignemts_set_df.style.map(color_cells)
            different_alignemts_set_styled_df = different_alignemts_set_styled_df.set_caption(
                f"<b>Disagreeing Alignments which have different moves or events for {dir_model}</b>")
            different_alignemts_set_styled_df = different_alignemts_set_styled_df.apply(lambda row: row_borders(row, row.name,num_algos=len(algorithm_names)), axis=1)



            different_alignemts_set_html = different_alignemts_set_styled_df.to_html()
            with open(os.path.join(path_to_model, "trace_variants_disagreeing_alignments_set.html"), "w") as file:
                file.write(different_alignemts_set_html)

        # Frequency of multiple optimal alignments mostly lower then of disagreement, so doesn't work
        # all_optimal_df = create_df_with_all_optimal(path_to_model)
        # all_optimal_df_grouped = all_optimal_df.groupby("Trace Variant")
        # filtered_groups = all_optimal_df_grouped.filter(lambda x: len(x) >= 2)
        # total_frequency_multiple_optimal = filtered_groups.groupby("Trace Variant").first()['Frequency'].sum()

        #jsut to find number of trace variants
        all_optimal_df = create_df_with_all_optimal(path_to_model)
        number_trace_variants = len(all_optimal_df["Trace Variant"].unique())


        match = re.search(r'noise_treshold_(\d+\.\d+)', dir_model, re.IGNORECASE)
        Summary.append({ "Model": f"{match.group(1)}",
                        "Frequency of Disagreement (FoD)": round(occurance_of_disagreement / len(log), 4),
                        "FoD-order": round(occurance_of_disagreement_order / len(log), 4),
                        "FoD-set": round(occurance_of_disagreement_set / len(log), 4),
                         "FoD-order Variant": round( number_of_diasgreeing_trace_variants_order /number_trace_variants, 4),
                         "FoD-set  Variant": round( number_of_diasgreeing_trace_variants_set / number_trace_variants, 4),
                        })



    df_summary = pd.DataFrame(Summary)
    df_summary.columns = ["Model<br> Noise Threshold","Frequency of Disagreement<br>(FoD) ",
                          "FoD-order","FoD-set","FoD-order Variant", "FoD-set  Variant"
                          ]

    html = df_summary.to_html(escape=False, justify = "left")
    with open(os.path.join(path_to_event_log, "Summary.html"), "w") as file:
        file.write(html)
    event_log = os.path.basename(path_to_event_log)
    latex_code = df_summary.to_latex(index=False,  bold_rows=True,
                             caption=f"Alignment Summary {event_log}", label=f"tab:Alignment Summary {event_log}", escape=False, float_format="%.4f",  column_format='c')
    with open(os.path.join(path_to_event_log, "Summary_latex.txt"), "w") as file:
        file.write(latex_code)

def alignment_to_event_log(alignment):
    """
        takes the alignments of an event log and filters out all taus and log moves and creates a new event log
        """
    event_log = []

    for align_dict in alignment:
        align_dict_filtered = {}
        align_dict_filtered["alignment"] = [item for item in align_dict["alignment"] if item is not None]
        filtered_tuples = [tup for tup in align_dict_filtered['alignment'] if tup[1] != '>>' and tup[1] != None]
        inner_list = [{'concept:name': tup[1]} for tup in filtered_tuples]
        event_log.append(inner_list)

    return event_log
def calculate_precision_for_all_alignments(path_to_event_log, algorithm_names):
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

    latex_filename_txt = os.path.join(path_to_event_log, "precision.txt")
    latex_filename_html = os.path.join(path_to_event_log, "precision.html")

    # Generate LaTeX code
    latex_code = precision_df.to_latex()

    # Save LaTeX code as .txt file
    with open(latex_filename_txt, 'w') as f:
        f.write(latex_code)

    # Save DataFrame as .html file
    precision_df.to_html(latex_filename_html)







