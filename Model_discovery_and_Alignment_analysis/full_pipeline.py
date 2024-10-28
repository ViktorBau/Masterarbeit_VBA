from functions import compare_alignments, calculate_precision_for_all_alignments, create_save_PN_Alignment_inductive
from Deviation_plots import create_deviation_plots_for_all_models
from PROM_to_PM4PY import PROM_result_list_to_PM4PY_alignment_for_all_in_folder, PROM_all_optimal_varaints_to_PM4PY_alignment_for_all_in_folder, PROM_planing_based_to_PM4PY_alignment_for_all_in_folder
from all_optimal_functions import create_html_with_all_optimal_for_all_in_folder, \
    from_all_optimal_alignments_choose_random_for_all_in_folder, from_all_optimal_read_and_save_event_log_excluded, \
    from_all_optimal_alignments_choose_sync_model_log_for_all_in_folder, calculate_jaccard_for_all_in_folder





if __name__ == '__main__':

    # Add path to folder with Event log here
    # path_to_event_log =
    algorithm_names = ["PROM_AStar","PROM_planing_based","ALL_OPTIMAL_random", "ALL_OPTIMAL_sync_model_log"]
    algorithm_namesPROM = ["PROM_AStar"]

    # Create Petri Net and save it, already done in example as all optimal are already calcualted
    create_save_PN_Alignment_inductive(path_to_event_log)


    # Create Eventlog that excludes all traces which weren't able to able to calculate by all optimal implementation
    from_all_optimal_read_and_save_event_log_excluded(path_to_event_log)

    # From Prom alignments results create  alignments in common format
    PROM_result_list_to_PM4PY_alignment_for_all_in_folder(path_to_event_log, algorithm_namesPROM)
    PROM_planing_based_to_PM4PY_alignment_for_all_in_folder(path_to_event_log)
    PROM_all_optimal_varaints_to_PM4PY_alignment_for_all_in_folder(path_to_event_log)
    from_all_optimal_alignments_choose_random_for_all_in_folder(path_to_event_log)
    from_all_optimal_alignments_choose_sync_model_log_for_all_in_folder(path_to_event_log)


    create_html_with_all_optimal_for_all_in_folder(path_to_event_log)

    # Create summary statistics with Fequency of Deviation
    compare_alignments(path_to_event_log, algorithm_names)
    calculate_precision_for_all_alignments(path_to_event_log, algorithm_names)
    create_deviation_plots_for_all_models(path_to_event_log, algorithm_names)

    calculate_jaccard_for_all_in_folder(path_to_event_log)