import os
import pickle
import copy
import shutil
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from functions import create_trace_variant_to_alignemnt_dict


def create_deviation_plots_for_all_models(path_to_event_log, algorithm_names, delete_old =True):
    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        path_to_deviation = os.path.join(path_to_model, 'deviation_plots')
        path_to_directly_follows = os.path.join(path_to_deviation, 'directly_follows_plots')
        path_to_deiviation_per_activity = os.path.join(path_to_deviation, 'deviation_per_activity')
        if os.path.exists(path_to_deviation):
            if delete_old:
                shutil.rmtree(path_to_deviation)
                os.makedirs(path_to_deviation)
                os.makedirs(path_to_directly_follows)
                os.makedirs(path_to_deiviation_per_activity)

        else:
            os.makedirs(path_to_deviation)
            os.makedirs(path_to_directly_follows)
            os.makedirs(path_to_deiviation_per_activity)

        directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
                                                                                                 algorithm_names,
                                                                                                 type="activity/activity")

        create_heatmap(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity",
                       "activity_activity")
        create_scatter_plot(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity",
                            "activity_activity")
        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows,
        #                            "activity_activity", "activity_activity")


        move_occourance_dict = create_move_occourance_dict_all_algorithms(path_to_model, algorithm_names)

        create_deviation_per_activity_plots(calc_number_of_deviation, "all", 'Number of Deviations',
                                 'Number of Deviations for Each Activity by Algorithm', 'Number of Deviations',
                                 move_occourance_dict, path_to_deiviation_per_activity)

        create_deviation_per_activity_plots(calc_number_of_deviation, "model", 'Number of Model move Deviation',
                                 'Number of Model move Deviation for Each Activity by Algorithm', 'Number of Model move Deviation',
                                 move_occourance_dict, path_to_deiviation_per_activity)

        create_deviation_per_activity_plots(calc_number_of_deviation, "log",'Number of Log move Deviation',
                                 'Number of Log move Deviation for Each Activity by Algorithm', 'Number of Log move Deviation',
                                 move_occourance_dict, path_to_deiviation_per_activity)

        create_deviation_per_activity_plots(calc_deviation_distribution, "all",'Deviation Distribution',
                                 'Deviation Distribution for Each Activity by Algorithm', 'Deviation Distribution',
                                 move_occourance_dict, path_to_deiviation_per_activity)

        move_occourance_dict_variantLog = create_move_occourance_dict_all_algorithms(path_to_model, algorithm_names, varaintLog = True)


        create_deviation_per_activity_plots(calc_number_of_deviation, "all", 'Number of Deviations in Trace Variant Log',
                                 'Number of Deviations for Each Activity by Algorithm  in Trace Variant Log', 'Number of Deviations in Trace Variant Log',
                                 move_occourance_dict_variantLog, path_to_deiviation_per_activity)

        create_deviation_per_activity_plots(calc_number_of_deviation, "model", 'Number of Model move Deviation  in Trace Variant Log',
                                 'Number of Model move Deviation for Each Activity by Algorithm  in Trace Variant Log',
                                 'Number of Model move Deviation  in Trace Variant Log',
                                 move_occourance_dict_variantLog, path_to_deiviation_per_activity)

        create_deviation_per_activity_plots(calc_number_of_deviation, "log", 'Number of Log move Deviation  in Trace Variant Log',
                                 'Number of Log move Deviation for Each Activity by Algorithm  in Trace Variant Log',
                                 'Number of Log move Deviation  in Trace Variant Log',
                                 move_occourance_dict_variantLog, path_to_deiviation_per_activity)



        directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
                                                                                                 algorithm_names,
                                                                                                 type="activity/activity", trace_variant=True)

        create_heatmap(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity_trace_variant", "activity_activity_trace_variant")
        create_scatter_plot(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity_trace_variant", "activity_activity_trace_variant")

        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity_trace_variant", "activity_activity_trace_variant")
        # create_seperate_heatmaps(directly_follows_occourance_dict, path_to_directly_follows, "activity_activity_trace_variant", "activity_activity_trace_variant")

        # directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
        #                                                                                          algorithm_names,
        #                                                                                          type="sync/sync", trace_variant=True)
        #
        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows, "sync_sync", "sync_sync")
        #create_seperate_heatmaps(directly_follows_occourance_dict, path_to_directly_follows, "sync_sync", "sync_sync")
        #
        # directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
        #                                                                                          algorithm_names,
        #                                                                                          type="sync/sync")
        #
        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows, "sync_sync_trace_variant", "sync_sync_trace_variant")
        # create_seperate_heatmaps(directly_follows_occourance_dict, path_to_directly_follows, "sync_sync_trace_variant", "sync_sync_trace_variant")
        #
        # directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
        #                                                                                          algorithm_names,
        #                                                                                          type="sync/dev", trace_variant=True)
        #
        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows, "sync_dev", "sync/dev")
        # create_seperate_heatmaps(directly_follows_occourance_dict, path_to_directly_follows, "sync_dev"_trace_variant, "sync_dev_trace_variant")
        #
        # directly_follows_occourance_dict = create_directly_folows_occourance_dict_all_algorithms(path_to_model,
        #                                                                                          algorithm_names,
        #                                                                                          type="sync/dev")
        #
        # create_heatmap_and_scatter(directly_follows_occourance_dict, path_to_directly_follows, "sync_dev_trace_variant", "sync_dev_trace_variant")
        # create_seperate_heatmaps(directly_follows_occourance_dict, path_to_directly_follows, "sync_dev_trace_variant", "sync_dev_trace_variant")


###### Deviation per activity plots ######
def create_min_max_occurance_dict(all_optimal_alignment_variants, varaintLog = False):
    max_occourance_dict = {}
    min_occourance_dict = {}


    for trace, details in all_optimal_alignment_variants.items():
        alignments = details['alignments']
        frequency = len(details["trace_indicies"])
        if varaintLog:
            frequency = 1
        max_deviations_trace = {}
        min_deviations_trace = {}

        # There is a problem with traces that have optimal alignments with different lengths.
        #The issue is that if the longer traces has an Event as a Model move but the shorter one doesn't have it all it would be counted for the shorter traces aswell
        # to avoid this prbolem I fill up the Count of deviations for each alignment with empty counts for event that exist in all optimal alignments for this trace


        all_possible_events = {}

        for alignment in alignments:
            for event1, event2 in alignment:
                if event1 not in all_possible_events and event1 != '>>':
                    all_possible_events[event1] = {'model_move': 0, 'log_move': 0, 'sync_move': 0}
                if event2 not in all_possible_events and event2 != '>>':
                    all_possible_events[event2] = {'model_move': 0, 'log_move': 0, 'sync_move': 0}

        deviations_alignments =[copy.deepcopy(all_possible_events) for _ in range(len(alignments))]
        for idx, alignment in enumerate(alignments):

            for event1, event2 in alignment:
                if event1 == '>>' and event2 != '>>':
                    deviations_alignments[idx][event2]['model_move'] += frequency
                elif event1 != '>>' and event2 == '>>':
                    deviations_alignments[idx][event1]['log_move'] += frequency
                elif event1 == event2:
                    deviations_alignments[idx][event1]['sync_move'] += frequency


            for event, counts in deviations_alignments[idx].items():
                if event not in max_deviations_trace:
                    max_deviations_trace[event] = counts
                    min_deviations_trace[event] = counts
                else:
                    if counts['model_move'] + counts['log_move'] >= max_deviations_trace[event]['model_move'] + max_deviations_trace[event]['log_move']:
                        max_deviations_trace[event] = counts
                    if counts['model_move'] + counts['log_move'] <= min_deviations_trace[event]['model_move'] + min_deviations_trace[event]['log_move']:
                        min_deviations_trace[event] = counts


        for event, counts in max_deviations_trace.items():
            counts = copy.deepcopy(counts)
            if event not in max_occourance_dict:
                max_occourance_dict[event] = counts
            else:
                max_occourance_dict[event]['model_move'] += counts['model_move']
                max_occourance_dict[event]['log_move'] += counts['log_move']
                max_occourance_dict[event]['sync_move'] += counts['sync_move']

        for event, counts in min_deviations_trace.items():
            counts = copy.deepcopy(counts)
            if event not in min_occourance_dict:
                min_occourance_dict[event] = counts
            else:
                min_occourance_dict[event]['model_move'] += counts['model_move']
                min_occourance_dict[event]['log_move'] += counts['log_move']
                min_occourance_dict[event]['sync_move'] += counts['sync_move']

    return min_occourance_dict,max_occourance_dict
def create_deviation_per_activity_plots(calc_frequency_func, type_of_move, ylabel, title, file_name, move_occourance_dict, path_to_deviation):
    # Initialize the plot using subplots
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.rcParams.update({'font.family': 'DejaVu Sans'})  # Update font style

    # Extract event names, excluding "total_number_of_events"
    event_names = move_occourance_dict[next(iter(move_occourance_dict))].keys()
    event_names = [item for item in event_names if item != "total_number_of_events"]

    # Create abbreviations for each event name
    abbreviations = {event: f"a{idx + 1}" for idx, event in enumerate(event_names)}
    abbr_event_names = [abbreviations[event] for event in event_names]  # List of abbreviations for the x-axis

    # Iterate through the dictionary to plot each algorithm
    for idx, (algorithm, events) in enumerate(move_occourance_dict.items()):

        frequencies = []
        # Calculate frequencies using the provided function
        event_frequencies = calc_frequency_func(events, type_of_move)
        for event in event_names:
            frequencies.append(event_frequencies.get(event, 0))

        if algorithm not in ['max', 'min']:
            # Create a slight horizontal offset to avoid overlap
            x_positions = np.arange(len(event_names)) + ((idx - 1.5) * 0.17)

            # Plot the data using scatter plot with smaller points
            label, color, marker = get_algo_layout_params(algorithm)
            ax.scatter(x_positions, frequencies, s=75, label=label, color=color, marker=marker)
        else:
            # Handle 'max' and 'min' cases with horizontal lines
            if algorithm == 'max':
                label = "maximum"
                color = 'red'
                linestyle = 'dashed'
            else:
                label = "minimum"
                color = 'blue'
                linestyle = 'solid'
            x_positions_min = np.arange(len(event_names)) - 0.45
            x_positions_max = np.arange(len(event_names)) + 0.45
            ax.hlines(frequencies, x_positions_min, x_positions_max, label=label, color=color, linestyle=linestyle)

    # Add labels, title, and grid using the ax object
    ax.set_xlabel('Activity', fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    #ax.set_title(title, fontsize=20)

    # Set x-ticks and rotate them for better visibility using abbreviations
    ax.set_xticks(ticks=np.arange(len(event_names)))
    ax.set_xticklabels(abbr_event_names, rotation=45, ha='right')

    # Add gridlines and legend
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    ax.legend(title='Algorithms',fontsize=14)

    # Create a text box with abbreviations and full labels to the right of the plot
    abbr_and_full_labels = [f"{abbreviations[event]}: {event}" for event in event_names]
    abbr_text = "\n".join(abbr_and_full_labels)

    # Position the text box on the right side of the plot
    plt.text(1.02, 0.5, abbr_text, transform=ax.transAxes, fontsize=12, verticalalignment='center',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # Tight layout to ensure no elements overlap
    plt.tight_layout()

    # Save the plot
    path_to_graph = os.path.join(path_to_deviation, f'{file_name}.png')
    plt.savefig(path_to_graph, format='png', dpi=300, bbox_inches='tight')
    plt.close()
def create_move_occourance_dict_all_algorithms(path_to_model, algorithm_names, add_min_max = True, varaintLog = False):
    move_occourance_dict_all_algorithms = {}
    with open(os.path.join(path_to_model, f"Event_log.pickle"), "rb") as file:
        log = pickle.load(file)


    for algorithm in algorithm_names:
        if os.path.isfile(os.path.join(path_to_model, f"alignment_{algorithm}.pickle")):
            with open(os.path.join(path_to_model, f"alignment_{algorithm}.pickle"), "rb") as file:
                alignment = pickle.load(file)


            move_occourance_dict_all_algorithms[algorithm] = create_move_occourance_dict(log, alignment, varaintLog)

    if add_min_max:
        with open(os.path.join(path_to_model, "all_optimal_alignments", f"all_optimal_variants_PM4PY.pickle"),
                  "rb") as file:
            all_optimal_alignment_variants = pickle.load(file)
            min, max = create_min_max_occurance_dict(all_optimal_alignment_variants, varaintLog)
            move_occourance_dict_all_algorithms['min'] = min
            move_occourance_dict_all_algorithms['max'] = max

    return move_occourance_dict_all_algorithms

####### Different Metrics for deviation per acitivty ######
def calc_deviation_distribution(events, type_of_move = "all"):
    total_deviations = 0
    event_frequencies = {}
    for event, counts in events.items():
        if event != "total_number_of_events":
            model_moves = counts['model_move']
            log_moves = counts['log_move']
            total_deviations += model_moves + log_moves
    for event, counts in events.items():
        if event != "total_number_of_events":
            model_moves = counts['model_move']
            log_moves = counts['log_move']
            total_deviations_event = model_moves + log_moves
            if total_deviations > 0:
                frequency = total_deviations_event / total_deviations
                event_frequencies[event] = frequency
    return event_frequencies
def calc_frequency_deviation(events, type_of_move = "all"):

    event_frequencies = {}
    for event, counts in events.items():
        if event != "total_number_of_events":
            model_moves = counts['model_move']
            log_moves = counts['log_move']
            sync_moves = counts['sync_move']
            total_moves = model_moves + log_moves + sync_moves
            if type_of_move == "all":
                if total_moves > 0:
                    frequency = (model_moves + log_moves) / total_moves
            elif type_of_move == "model":
                if total_moves > 0:
                    frequency = (model_moves) / total_moves
            elif type_of_move == "log":
                if total_moves > 0:
                    frequency = (log_moves) / total_moves
            event_frequencies[event] = frequency
    return event_frequencies
def calc_number_of_deviation(events, type_of_move = "all"):

    event_frequencies = {}
    for event, counts in events.items():
        if event != "total_number_of_events":
            move_counts = {
                "all": counts['model_move'] + counts['log_move'],
                "model": counts['model_move'],
                "log": counts['log_move']
            }
            total_deviation = move_counts.get(type_of_move, 0)
            event_frequencies[event] = total_deviation
    return event_frequencies

###### Directly follows plots ######

def create_heatmap(directly_follows_occourance_dict_all_algorithms, path_to_directly_follows, file_name="", caption=""):
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    data = directly_follows_occourance_dict_all_algorithms

    # Extract all activities
    activities = set()
    for alg in data:
        for (act1, act2) in data[alg]:
            activities.add(act1)
            activities.add(act2)
    activities = sorted(activities)

    # Create a mapping from activity to index and abbreviations
    activity_to_index = {activity: idx for idx, activity in enumerate(activities)}
    abbreviations = {activity: f"a{idx + 1}" for idx, activity in enumerate(activities)}
    n = len(activities)

    # List of algorithms
    algorithms = list(data.keys())

    # Initialize the difference matrix
    difference_matrix = np.zeros((n, n))
    counts_per_cell = [[[] for _ in range(n)] for _ in range(n)]

    # Collect counts and compute differences
    for i in range(n):
        for j in range(n):
            act1 = activities[i]  # Preceding activity (y-axis)
            act2 = activities[j]  # Following activity (x-axis)
            counts = []
            for alg in algorithms:
                if (act1, act2) in data[alg]:
                    counts.append(data[alg][(act1, act2)])
                else:
                    counts.append(0)
            counts_per_cell[i][j] = counts
            max_min_diff = max(counts) - min(counts)
            difference_matrix[i][j] = max_min_diff

    # Identify top 10 highest max-min differences
    flat_diff = difference_matrix.flatten()
    top_10_indices = np.argsort(flat_diff)[-10:][::-1]  # Sort in descending order
    top_10_events = [(i // n, i % n) for i in top_10_indices]

    # Create the plot with four subplots
    fig, axs = plt.subplots(2, 2, figsize = (24, 24),  constrained_layout=True)
   # fig.subplots_adjust(hspace=0.00,)
    # fig.subplots_adjust(top=0.9)# Adjust vertical space between subplots
    axs = axs.flatten()

    # Create custom colormap from white to dark blue
    original_cmap = plt.cm.YlGnBu
    colors = original_cmap(np.linspace(0, 1, original_cmap.N))
    colors[0] = [1, 1, 1, 1]  # Set the first color to white
    custom_cmap = LinearSegmentedColormap.from_list('custom_YlGnBu', colors)

    # Create heatmaps for each algorithm
    for idx, alg in enumerate(algorithms):
        ax = axs[idx]
        matrix = np.zeros((n, n))  # Reset matrix for each algorithm
        for (act1, act2), count in data[alg].items():
            i = activity_to_index[act1]  # y-axis
            j = activity_to_index[act2]  # x-axis
            matrix[i][j] = count

        im = ax.imshow(matrix, cmap=custom_cmap, norm=PowerNorm(gamma=0.5), interpolation='nearest')
        ax.set_title(get_algo_layout_params(alg)[0], fontsize=25 , pad=20)  # Increase font size

        # Set the ticks
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels([abbreviations[activity] for activity in activities], rotation=90, fontsize=14)

        # Set y tick labels
        if idx % 2 == 0:
            ax.set_yticklabels([f"{abbreviations[activity]} ({activity}) ⟶ " for activity in activities], fontsize=14)
        else:
            ax.set_yticklabels([f"{abbreviations[activity]} ⟶" for activity in activities], fontsize=14)


        # Turn spines off and create a grid
        ax.set_xticks(np.arange(-.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-.5, n, 1), minor=True)
        ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        ax.tick_params(which="minor", bottom=False, left=False)

        # Highlight top 10 highest max-min differences
        for (i, j) in top_10_events:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor='red', lw=2, zorder=5))

    # Add a single colorbar to the right of all subplots
    cbar = fig.colorbar(im, ax=axs, location='right', shrink=0.6)
    cbar.set_label('# of directly follows relationship in aligned log', fontsize=14)
    cbar.ax.tick_params(labelsize=14)
    path_to_graph = os.path.join(path_to_directly_follows, f'directly_follows_heatmap_{file_name}.png')
    plt.savefig(path_to_graph, format='png', dpi=300, bbox_inches='tight')
    plt.close()


def create_scatter_plot(directly_follows_occourance_dict_all_algorithms, path_to_directly_follows, file_name="",
                        caption=""):
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    data = directly_follows_occourance_dict_all_algorithms

    # Extract all activities
    activities = set()
    for alg in data:
        for (act1, act2) in data[alg]:
            activities.add(act1)
            activities.add(act2)
    activities = sorted(activities)

    # Create a mapping from activity to index and abbreviations
    activity_to_index = {activity: idx for idx, activity in enumerate(activities)}
    abbreviations = {activity: f"a{idx + 1}" for idx, activity in enumerate(activities)}
    n = len(activities)

    # List of algorithms
    algorithms = list(data.keys())

    # Initialize the difference matrix
    difference_matrix = np.zeros((n, n))
    counts_per_cell = [[[] for _ in range(n)] for _ in range(n)]

    # Collect counts and compute differences
    for i in range(n):
        for j in range(n):
            act1 = activities[i]  # Preceding activity (y-axis)
            act2 = activities[j]  # Following activity (x-axis)
            counts = []
            for alg in algorithms:
                count = data[alg].get((act1, act2), 0)
                counts.append(count)
            counts_per_cell[i][j] = counts
            max_min_diff = max(counts) - min(counts)
            difference_matrix[i][j] = max_min_diff

    # Identify top 10 highest max-min differences
    flat_diff = difference_matrix.flatten()
    top_15_indices = np.argsort(flat_diff)[-15:][::-1]  # Sort in descending order
    top_15_events = [(i // n, i % n) for i in top_15_indices]
    top_15_labels = [f"{abbreviations[activities[i]]}⟶{abbreviations[activities[j]]}" for i, j in top_15_events]

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(16, 8))

    for idx, alg in enumerate(algorithms):
        counts = [counts_per_cell[i][j][idx] for i, j in top_15_events]
        x_positions = np.arange(len(top_15_labels)) + ((idx - 1.5) * 0.17)  # Offset markers
        label, color, marker = get_algo_layout_params(alg)
        ax.scatter(x_positions, counts, label=label, color=color, marker=marker, s=75)

    ax.set_xlabel('Directly follows relationship', fontsize=14)
    ax.set_ylabel('# of directly follows relationship in aligned log', fontsize=14)

    ax.set_xticks(np.arange(len(top_15_labels)))
    ax.set_xticklabels(top_15_labels, rotation=45, ha='right', fontsize=14)
    ax.tick_params(axis='y', labelsize=12)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.legend(title='Algorithms', fontsize=14)

    # Create a text box with abbreviations and full labels to the right of the plot
    abbr_and_full_labels = [f"{abbreviations[activity]}: {activity}" for activity in activities]
    abbr_text = "\n".join(abbr_and_full_labels)

    # Position the text box on the right side of the plot
    plt.text(1.02, 0.5, abbr_text, transform=ax.transAxes, fontsize=12, verticalalignment='center',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # Save the plot
    path_to_graph = os.path.join(path_to_directly_follows, f'directly_follows_scatter_{file_name}.png')
    plt.savefig(path_to_graph, format='png', dpi=300, bbox_inches='tight')
    plt.close()

def create_move_occourance_dict(log,alignment, variantLog = False):
    trace_varaint_alignement_dict = create_trace_variant_to_alignemnt_dict(log, alignment)
    total_events = 0
    event_occourance_dict = {"total_number_of_events": 0}
    # Iterate through each trace in the dictionary
    for trace, details in trace_varaint_alignement_dict.items():
        alignment = details['alignment']
        frequency = details['frequency']
        if variantLog:
            frequency = 1

        # Sum the frequency to the total number of events


        # Iterate through the alignment to identify and count move types
        for event1, event2 in alignment:
            event_occourance_dict["total_number_of_events"] += frequency
            if event1 not in event_occourance_dict and event1 != '>>':
                event_occourance_dict[event1] = {'model_move': 0, 'log_move': 0, 'sync_move': 0}
            if event2 not in event_occourance_dict and event2 != '>>':
                event_occourance_dict[event2] = {'model_move': 0, 'log_move': 0, 'sync_move': 0}

            if event1 == '>>' and event2 != '>>':
                event_occourance_dict[event2]['model_move'] += frequency
            elif event1 != '>>' and event2 == '>>':
                event_occourance_dict[event1]['log_move'] += frequency
            elif event1 == event2:
                event_occourance_dict[event1]['sync_move'] += frequency

    return event_occourance_dict
def create_directly_follows_occurrence_dict(log, alignment, type = "activity/activity", trace_variant = False):
    trace_variant_alignment_dict = create_trace_variant_to_alignemnt_dict(log, alignment)
    directly_follows_occurrence_dict = {}

    for trace, details in trace_variant_alignment_dict.items():
        alignment = details['alignment']
        frequency = details['frequency']

        for i in range(len(alignment) - 1):
            event1 = alignment[i]
            event2 = alignment[i + 1]
            directly_follows_pair = (event1, event2)

            if directly_follows_pair not in directly_follows_occurrence_dict:
                directly_follows_occurrence_dict[directly_follows_pair] = 0
            if trace_variant:
                frequency = 1
            directly_follows_occurrence_dict[directly_follows_pair] += frequency

        if type == "sync/sync":
            directly_follows_occurrence_dict = filter_sync_sync(directly_follows_occurrence_dict)
        elif type == "sync/dev":
            directly_follows_occurrence_dict = filter_sync_dev(directly_follows_occurrence_dict)

        aggregated_dict = aggregate_dict(directly_follows_occurrence_dict)


    return aggregated_dict
def create_directly_folows_occourance_dict_all_algorithms(path_to_model, algorithm_names, type = "activity/activity", trace_variant = False):
    directly_follows_occourance_dict_all_algorithms = {}
    with open(os.path.join(path_to_model, f"Event_log.pickle"), "rb") as file:
        log = pickle.load(file)

    for algorithm in algorithm_names:
        if os.path.isfile(os.path.join(path_to_model, f"alignment_{algorithm}.pickle")):
            with open(os.path.join(path_to_model, f"alignment_{algorithm}.pickle"), "rb") as file:
                alignment = pickle.load(file)

            directly_follows_occourance_dict_all_algorithms[algorithm] = create_directly_follows_occurrence_dict(log, alignment, type, trace_variant)


    return directly_follows_occourance_dict_all_algorithms

# can be used to adjust which kind of directly follows relations should be plotted example only sync/sync
# have to be inserted into create_move_occourance_dict
def filter_sync_sync(input_dict):
    keys_to_delete = [key for key in input_dict if
                      any('>>' in sub_key for sub_tuple in key for sub_key in sub_tuple)]
    for key in keys_to_delete:
        del input_dict[key]
    return input_dict
def filter_sync_dev(input_dict):
    # Identify keys to delete where '>>' is present in the first tuple
    keys_to_delete = [key for key in input_dict if '>>' in key[0] or '>>' not in key[1]]

    # Delete the identified keys from the dictionary
    for key in keys_to_delete:
        del input_dict[key]

    return input_dict
def aggregate_dict(input_dict):
    aggregated_dict = {}

    for key, value in input_dict.items():
        # Extract activities from the inner tuples, ignoring '>>'
        activity1 = key[0][0] if key[0][0] != '>>' else key[0][1]
        activity2 = key[1][0] if key[1][0] != '>>' else key[1][1]

        # Create a new key using the extracted activities
        new_key = (activity1, activity2)

        # Add the value to the aggregated dictionary
        if new_key in aggregated_dict:
            aggregated_dict[new_key] += value
        else:
            aggregated_dict[new_key] = value

    return aggregated_dict


###### Helper functions for deviation plots ######
def get_algo_layout_params(algorithm):
    if algorithm == "PROM_AStar":
        label = "Astar"
        color = "#AA3377"  # purple
        marker = 'o'
    elif algorithm == "PROM_planing_based":
        label = "planningBased"
        color = "#56B4E9"  # cyan
        marker = 'D'
    elif algorithm == "ALL_OPTIMAL_random":
        label = "Simulated:Random"
        color = "#D4C337"  # gelb
        marker = 's'
    elif algorithm == "ALL_OPTIMAL_sync_model_log":

        label = "Simulated:Sync-Model-Log"
        color = "#F781BF"  # pink
        marker = '^'
    else:
        label = algorithm
        color = "#7f7f7f"  # Default grey
        marker = 'x'
    return label, color, marker















