
def is_algo_deterministic(dir_input, variant_str, number_of_runs=5):
    with open(os.path.join(dir_input, "Event_log.pickle"), "rb") as file:
        log = pickle.load(file)

        # Load the Petri net
    net, initial_marking, final_marking = pm4py.read_pnml(os.path.join(dir_input, "Petri_net.pnml"))

    # Create the alignments dictionary
    alignments = {}
    differences_list_of_rows = []
    for i in range(number_of_runs):
        alignment = pm4py.conformance_diagnostics_alignments(log, net, initial_marking, final_marking, variant_str)
        alignments[f"run {i}"] = create_trace_variant_to_alignemnt_dict(log, alignment)

    for trace_variant in alignments[next(iter(alignments))].keys():
        list_alignments = []
        for i in range(number_of_runs):
            list_alignments.append(alignments[f"run {i}"][trace_variant]["alignment"])

        same_alignments = all(list_alignments[0] == other for other in list_alignments[1:])
        if (not same_alignments):
            for i in range(number_of_runs):
                row = []
                row.append(alignments[f"run {i}"][trace_variant]["trace_names"][0])
                row.append(round(alignments[f"run {i}"][trace_variant]["frequency"], 1))
                row.append(f"run {i}")
                row += (alignments[f"run {i}"][trace_variant]["alignment"])
                differences_list_of_rows.append(row)


    # style tabel for different alignments when considering the order and ignoring the once with different sets
    different_alignemts_df = pd.DataFrame(differences_list_of_rows).fillna("")
    different_alignemts_df = different_alignemts_df.rename(
        columns={0: "Trace Variant", 1: "Frequency", 2: "run"})

    different_alignemts_styled_df = different_alignemts_df.style.map(color_cells)
    different_alignemts_styled_df = different_alignemts_styled_df.set_caption(
        f"<b>Disagreeing Alignments for {variant_str} considering both the order of moves and the set of moves</b>")
    different_alignemts_styled_df = different_alignemts_styled_df.apply(
        lambda row: row_borders(row, row.name,num_algos=number_of_runs), axis=1)

    different_alignemts_html = different_alignemts_styled_df.to_html()
    with open(os.path.join(dir_input, f"runs_{number_of_runs}_disagreeing_alignments_{variant_str}.html"), "w") as file:
        file.write(different_alignemts_html)
def create_summary_statistic_for_amount_of_optimal_alignments_for_all_in_folder(path_to_event_log, create_html_for_each=True):

    all_models = [d for d in os.listdir(path_to_event_log) if
                  os.path.isdir(os.path.join(path_to_event_log, d)) and d.startswith("Model_")]

    results_all_models = {}

    for dir_model in all_models:
        path_to_model = os.path.join(path_to_event_log, dir_model)
        all_optimal_df = create_df_with_all_optimal(path_to_model)
        results_all_models[dir_model] = create_summary_statistic_for_amount_of_optimal_alignments(all_optimal_df, path_to_model, create_html_for_each)

    summary_statistic = []
    for name, model_results in zip(results_all_models.keys(), results_all_models.values()):
        avarage_number_of_alignments_before = round(model_results["Number of alignments before filtering"].mean(),2)
        avarage_number_of_alignments_after = round(model_results["Number of alignments after filtering"].mean(),2)
        trace_with_highest_number_of_alignments_before = model_results.loc[model_results["Number of alignments before filtering"].idxmax()]
        name_trace_wit_highest = trace_with_highest_number_of_alignments_before["Trace Variant"]
        amount_before = trace_with_highest_number_of_alignments_before["Number of alignments before filtering"]
        amount_after = trace_with_highest_number_of_alignments_before["Number of alignments after filtering"]
        summary_statistic.append([name, avarage_number_of_alignments_before, avarage_number_of_alignments_after, name_trace_wit_highest, amount_before, amount_after])

    summary_statistic_df = pd.DataFrame(summary_statistic, columns=["Model","Average # before filtering", "Average # after filtering", "Trace with highest # before filtering", "Amount before filtering", "Amount after filtering"])

    summary_statistic_df.to_html(os.path.join(path_to_event_log, 'summary_statistic_all_optimal_amount_alignments.html'))
def create_summary_statistic_for_amount_of_optimal_alignments(all_optimal_df, path_to_model, create_html = True):

    path_to_all_optimal = os.path.join(path_to_model, 'all_optimal_alignments', 'all_optimal_variants_PM4PY.pickle')

    with open(path_to_all_optimal, 'rb') as file:
        all_optimal_variants = pickle.load(file)


    summary_statistics = []
    for variant, name in zip(all_optimal_variants.values(), all_optimal_variants.keys()):
        trace_length = variant["info"]["Trace Length"]
        number_of_alignments_before_filter = variant["info"]["#Alignments"]
        number_of_alignments_after_filter = all_optimal_df[all_optimal_df["Trace Variant"] == name].shape[0]
        row = [name, trace_length,number_of_alignments_before_filter, number_of_alignments_after_filter]
        summary_statistics.append(row)

    summary_df = pd.DataFrame(summary_statistics, columns=["Trace Variant", "Trace Length", "Number of alignments before filtering", "Number of alignments after filtering"])

    if create_html:
        summary_df.to_html(os.path.join(path_to_model, 'all_optimal_alignments', 'summary_statistic_amount_alignments.html'))

    return summary_df

def create_html_with_all_optimal_for_specific_trace(path_to_model,trace_name, filter = False):
    all_optimal_specific_trace = create_df_with_all_optimal(path_to_model, specific_trace= trace_name , filter_tau=filter, filter_duplicates_after_tau=filter)

    all_optimal_specific_trace_styled_df = all_optimal_specific_trace.fillna("").style.map(color_cells)

    all_optimal_styled_html = all_optimal_specific_trace_styled_df.to_html()
    with open(os.path.join(path_to_model, "all_optimal_alignments", f"all_optimal_alignments_trace_{trace_name}.html"), "w") as file:
        file.write(all_optimal_styled_html)

def monitor_memory(interval=600, variant_str="", path_to_performance_dir=""):
    process = psutil.Process(os.getpid())
    memory_usage = []
    start_time = time.time()

    while not stop_event.is_set():
        mem_info = process.memory_info()
        memory_usage.append(mem_info.rss / (1024 * 1024))  # Save memory usage in MB
        time.sleep(interval)

    min_memory = min(memory_usage)
    max_memory = max(memory_usage)
    avg_memory = sum(memory_usage) / len(memory_usage)

    end_time = time.time()
    duration = end_time - start_time
    duration_str = str(timedelta(seconds=duration))

    with open(os.path.join(path_to_performance_dir, f"{variant_str}_summary.txt"), "w") as file:
        file.write(f"Min memory usage: {min_memory:.2f} MB\n")
        file.write(f"Max memory usage: {max_memory:.2f} MB\n")
        file.write(f"Average memory usage: {avg_memory:.2f} MB\n")
        file.write(f"Duration: {duration_str}")

        # Create a graph of memory usage
        plt.plot(memory_usage)
        plt.title(f"Memory usage of {variant_str}")
        plt.xlabel(f"Time (in intervals of {interval} seconds)")
        plt.ylabel("Memory usage (in MB)")
        plt.savefig(os.path.join(path_to_performance_dir, f"{variant_str}_memory_usage.svg"))  # Save the graph as .svg



def perform_alignment(path_to_model, log, path_to_performance_dir, variant_str):
    if not os.path.isfile(os.path.join(path_to_model, f"alignment_{variant_str}.pickle")):
        start_time = time.time()  # Start the timer

        monitor_thread = Thread(target=monitor_memory, args=(5, variant_str, path_to_performance_dir))
        monitor_thread.start()

        net, initial_marking, final_marking = pm4py.read.read_pnml(os.path.join(path_to_model, "Petri_net.pnml"))

        aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, initial_marking, final_marking, variant_str)

        stop_event.set()
        monitor_thread.join()

        with open(os.path.join(path_to_model, f"alignment_{variant_str}.pickle"), "wb") as file:
            pickle.dump(aligned_traces, file)


def create_alignments(path_to_event_log, dir_model, variant_strings):
    with open(os.path.join(path_to_event_log, "Event_log.pickle"), "rb") as file:
        log = pickle.load(file)

    path_to_model = os.path.join(path_to_event_log, dir_model)

    path_to_performance_dir = os.path.join(path_to_model, "performance_metrics")
    if not os.path.isdir(path_to_performance_dir):
        os.mkdir(path_to_performance_dir)
    processes = []
    if len(variant_strings) > 1:
        for variant_str in variant_strings:
            p = multiprocessing.Process(target=perform_alignment,
                                        args=(path_to_model, log, path_to_performance_dir, variant_str))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()
    else:
        perform_alignment(path_to_model, log, path_to_performance_dir, variant_strings[0])

def compare_alignments(path_to_event_log, algorithm_names):



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

        Summary.append({ "Model": dir_model,
                        "frequency of Disagreement ": round(occurance_of_disagreement / len(log), 4),
                        "occurance of Disagreement": round(occurance_of_disagreement, 1),
                        "Number of Disagreeing Trace Variants": number_of_diasgreeing_trace_variants,
                        "Occurance of Disagreement(same Moves different Order)": round(occurance_of_disagreement_order, 1),
                        "Number of Disagreeing Trace Variants(same Moves different Order)": number_of_diasgreeing_trace_variants_order,
                        "Occurance of Disagreement(different Moves)": round(occurance_of_disagreement_set,1),
                        "Number of Disagreeing Trace Variants(different Moves)": number_of_diasgreeing_trace_variants_set
                        })

    df_summary = pd.DataFrame(Summary)
    df_summary.columns = ["model", "frequency of Disagreement ","occurance of Disagreement",
                          "number of Disagreeing Trace Variants","occurance of Disagreement<br>(same Moves different Order)",
                          "number of Disagreeing Trace Variants<br>(same Moves different Order)",
                            "occurance of Disagreement<br>(different Moves)", "number of Disagreeing Trace Variants<br>(different Moves)"]

    html = df_summary.to_html(escape=False, justify = "left")
    with open(os.path.join(path_to_event_log, "Summary.html"), "w") as file:
        file.write(html)


def create_seperate_heatmaps (directly_follows_occourance_dict_all_algorithms,path_to_directly_follows, file_name = "", caption = ""):
    # Extract all unique activities from the data

    data = directly_follows_occourance_dict_all_algorithms
    activities = set()
    for alg in data:
        for (act1, act2) in data[alg]:
            activities.add(act1)
            activities.add(act2)
    activities = sorted(activities)

    # Create a mapping from activity to index
    activity_to_index = {activity: idx for idx, activity in enumerate(activities)}
    n = len(activities)

    # Create a list of activities with numbers for y-axis labels
    y_labels = [f"{activity} ({idx + 1})" for idx, activity in enumerate(activities)]

    # Prepare the figure and axes for a 2x2 grid with constrained layout
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
    axes = axes.flatten()

    # List of algorithms
    algorithms = list(data.keys())

    # Find the maximum and minimum positive count across all algorithms for LogNorm
    all_counts = []
    for alg in algorithms:
        all_counts.extend(data[alg].values())
    max_count = max(all_counts)
    min_positive_count = min(filter(lambda x: x > 0, all_counts))

    # Create a custom colormap from white to dark blue
    colors = [(1, 1, 1), (0, 0, 0.5)]
    custom_cmap = LinearSegmentedColormap.from_list('custom_blue', colors)

    # For each algorithm, create a heatmap
    for idx, alg in enumerate(algorithms):
        ax = axes[idx]
        matrix = np.full((n, n), np.nan)  # Initialize with NaN for LogNorm
        for (act1, act2), count in data[alg].items():
            i = activity_to_index[act2]  # y-axis
            j = activity_to_index[act1]  # x-axis
            matrix[i][j] = count
        # Plot the heatmap with logarithmic normalization
        im = ax.imshow(matrix, cmap=custom_cmap, interpolation='nearest',
                       norm=LogNorm(vmin=min_positive_count, vmax=max_count))
        ax.set_title(alg)
        # Set x and y ticks
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        # Set x tick labels to numbers (starting from 1)
        x_numbers = [str(idx + 1) for idx in range(n)]
        # Remove x-axis ticks and labels for top two plots
        if idx < 2:
            ax.set_xticks([])
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(x_numbers, rotation=90, fontsize=8)
            ax.set_xlabel('Activity Index', fontsize=10)
        # Remove y-axis ticks and labels for rightmost plots
        if idx % 2 == 0:
            ax.set_yticklabels(y_labels, fontsize=8)
            ax.tick_params(axis='y', which='both', length=5)
        else:
            ax.set_yticks([])
            ax.set_yticklabels([])
        # Add gridlines
        ax.set_xticks(np.arange(-.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-.5, n, 1), minor=True)
        ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        ax.tick_params(which="minor", bottom=False, left=False)
        # Ensure spines are visible on all sides
        for edge, spine in ax.spines.items():
            spine.set_visible(True)

    # Add a single colorbar to the right of all subplots
    cbar = fig.colorbar(im, ax=axes, location='right', shrink=0.6)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Directly Follows Count (Log Scale)', fontsize=12)

    fig.suptitle(caption)
    path_to_graph = os.path.join(path_to_directly_follows, f'directly_follows_heatmaps_{file_name}.png')
    plt.savefig(path_to_graph)
    plt.close()

    def create_heatmap_with_counts(directly_follows_occourance_dict_all_algorithms, path_to_directly_follows,
                                   file_name="", caption=""):

        data = directly_follows_occourance_dict_all_algorithms
        # Extract all activities
        activities = set()
        for alg in data:
            for (act1, act2) in data[alg]:
                activities.add(act1)
                activities.add(act2)
        activities = sorted(activities)

        # Create a mapping from activity to index
        activity_to_index = {activity: idx for idx, activity in enumerate(activities)}
        n = len(activities)

        # List of algorithms and colors
        algorithms = list(data.keys())
        colors = ['blue', 'green', 'orange', 'black']  # Avoiding red to prevent conflict with the background

        # Initialize the difference matrix
        difference_matrix = np.zeros((n, n))

        # Initialize counts per cell
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
                difference = max(counts) - min(counts)
                difference_matrix[i][j] = difference

        # Normalize the difference matrix for colormap
        max_diff = np.max(difference_matrix)
        if max_diff == 0:
            max_diff = 1  # Avoid division by zero
        normalized_diff = difference_matrix / max_diff

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 12))

        # Use a red colormap for the background
        cmap = plt.cm.Reds  # Red gradient
        im = ax.imshow(normalized_diff, cmap=cmap, interpolation='nearest')

        # Adjust layout to accommodate the legend at the top
        plt.subplots_adjust(left=0.2, bottom=0.2, right=0.9, top=0.85)

        # Add colorbar to show the scale of differences
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Normalized Difference', rotation=270, labelpad=15)

        # Set the ticks
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))

        # Add arrow after each activity in y-axis labels
        y_labels = [activity + ' ➞' for activity in activities]
        ax.set_xticklabels(activities, rotation=90)
        ax.set_yticklabels(y_labels)

        # Turn spines off and create a grid
        ax.set_xticks(np.arange(-.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-.5, n, 1), minor=True)
        ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        ax.tick_params(which="minor", bottom=False, left=False)

        # Annotate each cell with counts from each algorithm
        for i in range(n):
            for j in range(n):
                counts = counts_per_cell[i][j]
                # Positions for annotations within the cell
                positions = [
                    (-0.3, 0.3),  # Top-left
                    (0.3, 0.3),  # Top-right
                    (-0.3, -0.3),  # Bottom-left
                    (0.3, -0.3),  # Bottom-right
                ]
                for idx, count in enumerate(counts):
                    x = j + positions[idx][0]
                    y = i + positions[idx][1]
                    if count > 0:
                        ax.text(x, y, str(count), ha='center', va='center', color=colors[idx], fontsize=6)
                    else:
                        # Optionally, display zeros in gray
                        ax.text(x, y, '0', ha='center', va='center', color='gray', fontsize=6)

        # Create custom legend
        legend_elements = []
        for idx, alg in enumerate(algorithms):
            legend_elements.append(Line2D([0], [0], marker='o', color='w', label=alg,
                                          markerfacecolor=colors[idx], markersize=10))
        # Place the legend above the plot
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.15),
                  ncol=len(algorithms), fontsize=8, frameon=False)

        fig.suptitle(caption)
        path_to_graph = os.path.join(path_to_directly_follows, f'directly_follows_{file_name}.png')
        plt.savefig(path_to_graph)
        plt.close()

    #
    def create_heatmap_and_scatter(directly_follows_occourance_dict_all_algorithms, path_to_directly_follows,
                                   file_name="", caption=""):
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
        abbreviations = {activity: f"A{idx + 1}" for idx, activity in enumerate(activities)}
        n = len(activities)

        # List of algorithms
        algorithms = list(data.keys())

        # Initialize the difference matrix
        difference_matrix = np.zeros((n, n))
        counts_per_cell = [[[] for _ in range(n)] for _ in range(n)]

        # Collect counts and compute average absolute differences
        for i in range(n):
            for j in range(n):
                act1 = activities[i]  # Preceding activity (y-axis)
                act2 = activities[j]  # Following activity (x-axis)
                counts = []
                for alg in algorithms:
                    count = data[alg].get((act1, act2), 0)
                    counts.append(count)
                counts_per_cell[i][j] = counts
                avg_abs_diff = np.mean([abs(count - np.mean(counts)) for count in counts])
                difference_matrix[i][j] = avg_abs_diff

        # Create the plot with two subplots
        fig, axs = plt.subplots(1, 2, figsize=((7.8, 3.9)))

        # Heatmap on the left
        cmap = plt.cm.Reds  # Red gradient
        im = axs[0].imshow(difference_matrix, cmap=cmap, interpolation='nearest')

        # Adjust layout to accommodate the legend at the top
        fig.subplots_adjust(left=0.2, bottom=0.2, right=0.9, top=0.85)

        # Add colorbar to show the scale of differences
        cbar = plt.colorbar(im, ax=axs[0], fraction=0.046, pad=0.04)
        cbar.set_label('Average Absolute Difference', rotation=270, labelpad=15)

        # Set the ticks
        axs[0].set_xticks(np.arange(n))
        axs[0].set_yticks(np.arange(n))

        # Add abbreviated labels with full names in parentheses for Y-axis
        y_labels = [f"{abbr} ({activity}) ➞" for activity, abbr in abbreviations.items()]
        axs[0].set_xticklabels([abbreviations[activity] for activity in activities], rotation=90)
        axs[0].set_yticklabels(y_labels)

        # Turn spines off and create a grid
        axs[0].set_xticks(np.arange(-.5, n, 1), minor=True)
        axs[0].set_yticks(np.arange(-.5, n, 1), minor=True)
        axs[1].set_title('Heat map of the average absolute difference between algorithms')
        axs[0].grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        axs[0].tick_params(which="minor", bottom=False, left=False)

        # Scatter plot on the right for the top 10 highest average absolute differences
        flat_diff = difference_matrix.flatten()
        top_10_indices = np.argsort(flat_diff)[-10:][::-1]  # Sort in descending order
        top_10_events = [(i // n, i % n) for i in top_10_indices]
        top_10_labels = [f"{abbreviations[activities[i]]} -> {abbreviations[activities[j]]}" for i, j in top_10_events]

        for idx, alg in enumerate(algorithms):
            counts = [counts_per_cell[i][j][idx] for i, j in top_10_events]
            x_positions = np.arange(len(top_10_labels)) + ((idx - 1.5) * 0.15)
            label, color, marker = get_algo_layout_params(alg)  # Offset markers
            axs[1].scatter(x_positions, counts, label=label, color=color, marker=marker, s=100)

        axs[1].set_xlabel('Directly Follows Relationship')
        axs[1].set_ylabel('Counts')
        axs[1].set_title('Top 10 Highest Average Absolute Differences')
        axs[1].set_xticks(np.arange(len(top_10_labels)))
        axs[1].set_xticklabels(top_10_labels, rotation=45, ha='right')
        axs[1].grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        axs[1].legend(title='Algorithms')

        path_to_graph = os.path.join(path_to_directly_follows, f'directly_follows_{file_name}.png')
        plt.savefig(path_to_graph, format='png', dpi=300, bbox_inches='tight')
        plt.close()