# %% [markdown]
# This notebook is for post-processing 'lm-eval' outputs in the format of:
# 
# output folder > task > model > results_datetime.json
# 
# and
# 
# output folder > task > model > samples_task_datetime.jsonl

# %% [markdown]
# Assuming the following directory structure
# 
# ```markdown
# main_dir/
# ├── task1/
# │ ├── model1/
# │ │ └── results.json
# │ ├── model2/
# │ │ └── results.json
# ├── task2/
# │ ├── model1/
# │ │ └── results.json
# │ ├── model2/
# │ │ └── results.json
# ```

# %% [markdown]
# # Execute Parsing Results File Functions

# %% [markdown]
# ## Parsing file name nomenclature for times

# %%
# Now for each row in df_all_results, compute the model and time columns from the names of the files
import json
from datetime import datetime

# Helper function to extract model and timestamp from filename
def parse_filename(filename):
    base_name = os.path.basename(filename)
    parts = base_name.split('_')
    model = parts[1]
    timestamp_str = parts[-1].replace('.json', '').replace('.jsonl', '')
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%f')
    return model, timestamp

# %% [markdown]
# ## Parse Results Files
# 

# %%
import pandas as pd
import json

def extract_results_files_info(df_all_results):
    # Initialize list to store temporary DataFrames
    df_list = []

    # Loop through the DataFrame and extract data from each JSON file
    for idx, row in df_all_results.iterrows():
        results_file_path = row['Results File Path']
        
        with open(results_file_path, 'r') as f:
            results = json.load(f)

        # Extract task name (key)
        task_name = list(results['results'].keys())[0]

        # Extract the task results
        task_data = results['results'][task_name]

        # Initialize a dictionary to hold the data for the DataFrame row
        data_dict = {'Results File Path': results_file_path, 'Task': task_name}

        # Loop through the keys in task_data and add them to data_dict
        for key, value in task_data.items():
            data_dict[key] = value

        # Extract additional requested information
        config = results.get('config', {})
        gen_kwargs = config.get('gen_kwargs')
        
        # Handle the case where gen_kwargs is None
        if gen_kwargs is None:
            data_dict['temperature'] = None
        else:
            data_dict['temperature'] = gen_kwargs.get('temperature')
        
        data_dict['model_dtype'] = config.get('model_dtype')
        data_dict['total_evaluation_time_seconds'] = results.get('total_evaluation_time_seconds')
        
        configs = results.get('configs', {})
        task_config = configs.get(task_name, {})
        data_dict['output_type'] = task_config.get('output_type')

        # Extract the task size from "n-samples" section
        n_samples = results.get('n-samples', {})
        task_samples = n_samples.get(task_name, {})
        data_dict['task_size_original'] = task_samples.get('original', None)

        # Create a DataFrame for the current row
        df_results = pd.DataFrame([data_dict])

        df_list.append(df_results)

    # Concatenate all temporary DataFrames
    df_extracted_data = pd.concat(df_list, ignore_index=True)

    # Combine the DataFrames and bring over everything except the 'Results File Path' column and the 'alias' column
    df_all_results = pd.concat([df_all_results, df_extracted_data.drop(columns=['Results File Path', 'alias'], errors='ignore')], axis=1)

    return df_all_results

# Example usage
# df_all_results_files_info = extract_results_files_info(df_all_filepaths)
# print(df_all_results_files_info)


# %% [markdown]
# We also need to pull out the model_name info ...
# 
# doing this from the directory its in b/c the configuration output is "hf" and "model_args" which would require a lot more parsing and special cases...

# %%
# Function to extract model name from the file path
def extract_model(file_path):
    # Split the file path into parts
    parts = file_path.split(os.sep)
    
    # The model name is two directory levels above the file
    model_name = parts[-2]
    
    return model_name

# Apply the function to each file path
# df_all_results_files_info['Model'] = df_all_results_files_info['Results File Path'].apply(extract_model)

# Display the DataFrame
# print(df_all_results_files_info)

# %%
# df_all_results_files_info

# %% [markdown]
# ## Filtering down to the desired results to analyze

# %%
def filter_unique_models(df_all_results_files_info, tasks_to_keep=['sysengbench', 'yes_or_no_tasks']):
    # Step 1: Filter the DataFrame for the specified tasks
    df_filtered = df_all_results_files_info[df_all_results_files_info['Task'].isin(tasks_to_keep)]

    # Step 2: Convert the Timestamp column to datetime
    df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp'])

    # Step 3: Sort the DataFrame by "Timestamp" in descending order
    df_filtered = df_filtered.sort_values(by='Timestamp', ascending=False)

    # Step 4: Drop duplicates based on the "Model" column, keeping only the most recent entry for each model
    df_unique_models = df_filtered.drop_duplicates(subset='Model', keep='first')

    # Step 5: Extract the relevant columns
    df_all_samples = df_unique_models

    return df_all_samples

# %% [markdown]
# # Execute Parsing Results Files

# %%
############# OVERALL EXECUTION WORKFLOW ###################
import glob
import os
import numpy as np
import pandas as pd

# base_dir_path = 'output5-20241113-SysEngBench1.0'
# base_dir_path = 'output6-20241118-ft-gpt4o-vs-gpt40 (new prompt)'
# base_dir_path = 'output7-20241119-SysEngBench1.0-newprompt Wiley INCOSE'
base_dir_path = 'output7-20241119-SysEngBench1.0-prompt1.1 Wiley INCOSE (Journal 1)'

# Finding all results_*.json and results_*.jsonl files in the directory and its subdirectories
results_files_json = glob.glob(os.path.join(base_dir_path, '**/results_*.json'), recursive=True)
samples_files_jsonl = glob.glob(os.path.join(base_dir_path, '**/samples_*.jsonl'), recursive=True)

# Assuming the pairs are in order for json and jsonl files 
# Create a DataFrame with the two lists as columns
df_all_filepaths = pd.DataFrame({
    'Results File Path': results_files_json,
    'Samples File Path': samples_files_jsonl
})

# Extract mtimestamp and add as new columns
df_all_filepaths['Timestamp'] = df_all_filepaths['Results File Path'].apply(lambda x: parse_filename(x)[1])

df_all_results_files_info = extract_results_files_info(df_all_filepaths)

# Apply the function to each file path
df_all_results_files_info['Model'] = df_all_results_files_info['Results File Path'].apply(extract_model)

# Optional Filter task and only keep most recent runs for each model
df_all_results_files_info_filtered = filter_unique_models(df_all_results_files_info)

# %%
df_all_results_files_info_filtered

# %% [markdown]
# # Execute Parsing Samples Files Functions
# ## Using df_all_results_files_info_filtered as the structure for our samples
# We do this because it also has all of the model info, courtesy of the results json file for each run

# %%
import pandas as pd
import json

def extract_samples_data(df_all_samples):
    """
    Extracts sample data from a DataFrame by reading JSON lines from files specified in the DataFrame.

    Parameters:
    df_all_samples (pd.DataFrame): DataFrame containing columns 'Samples File Path', 'Task', 'task_size_original', 'Model', 'model_dtype', and 'temperature'.

    Returns:
    pd.DataFrame: A new DataFrame with extracted sample data including task, model, question, true answer, and predicted answer.
    """
    # Initialize a list to hold the sample data
    samples_data = []

    # Loop through the DataFrame rows
    for idx, row in df_all_samples.iterrows():
        samples_file_path = row['Samples File Path']
        task_name = row['Task']
        task_size = row['task_size_original']
        model_name = row['Model']
        model_dtype = row['model_dtype']
        temperature = row['temperature']

        # Open the file specified in the 'Samples File Path' column
        with open(samples_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    sample = json.loads(line)
                    doc = sample['doc']
                    doc_id = sample['doc_id']

                    # Extract filtered_resps only
                    filtered_resps = sample.get('filtered_resps', [])

                    # Enhanced Debug Logging
                    print(f"Processing question_number = {doc_id + 1}")
                    print(f"filtered_resps = {filtered_resps}, type of filtered_resps = {type(filtered_resps)}")

                    # Determine the predicted answer
                    predicted_answer = 'INVALID'  # Default in case nothing is determined

                    # Check if filtered_resps contains log probability values or direct answers
                    if filtered_resps and isinstance(filtered_resps[0], list) and len(filtered_resps[0]) > 0:
                        # Check if the first element can be interpreted as a number
                        try:
                            # If the value can be converted to float, treat this as a log probability model
                            float(filtered_resps[0][0])  # Attempt to convert to float to verify type

                            # Find the maximum value index based on log probabilities (less negative is better)
                            predicted_answer_idx = max(
                                enumerate(filtered_resps),
                                key=lambda x: float(x[1][0])
                            )[0]
                            predicted_answer = chr(65 + predicted_answer_idx)  # Convert index to 'A', 'B', 'C', 'D', etc.
                            print(f"Determined log probability answer: {predicted_answer}")
                        except ValueError:
                            # If the conversion fails, it is not a log probability model
                            print("filtered_resps[0][0] could not be converted to float, skipping log probability model handling...")

                    elif filtered_resps and isinstance(filtered_resps[0], str) and filtered_resps[0].isalpha():
                        # Direct answer (generate until model)
                        predicted_answer = filtered_resps[0]
                        print(f"Determined generate until answer from filtered_resps: {predicted_answer}")

                    # Append the extracted data to the list
                    samples_data.append({
                        'task': task_name,
                        'task_size': task_size,
                        'model': model_name,
                        'model_dtype': model_dtype,
                        'temperature': temperature,
                        'question': doc.get('question', 'Unknown'),
                        'true_answer': doc.get('answer', 'Unknown'),
                        'predicted_answer': predicted_answer,
                        'INCOSE Handbook Category': doc.get('INCOSE Handbook Category', 'Unknown'),
                        'question_number': doc_id + 1  # account for 0-based indexing
                    })

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}, file: {samples_file_path}")
                    continue
                except KeyError as e:
                    print(f"Missing key in JSON: {e}, file: {samples_file_path}")
                    continue

    # Convert the list to a DataFrame
    df_all_samples_mcqs = pd.DataFrame(samples_data)
    
    return df_all_samples_mcqs

# Example usage:
df_all_samples_mcqs = extract_samples_data(df_all_results_files_info_filtered)
# print(df_all_samples_mcqs)     # Display the resulting DataFrame


# %%
df_all_samples_mcqs
# df_filtered_phi_2 = df_all_samples_mcqs[df_all_samples_mcqs['model'] == 'microsoft__phi-2']
# df_filtered_phi_2

# %%
import pandas as pd

# Replace 'output_file.xlsx' with your desired file name
output_file = "df_all_samples_mcqs_debug.xlsx"

# Exporting the DataFrame to an Excel file
df_all_samples_mcqs.to_excel(output_file, index=False, engine='openpyxl')

print(f"DataFrame successfully exported to {output_file}")


# %% [markdown]
# ## Generating the metrics across the df_all_samples_mcqs dataframe

# %% [markdown]
# We're going to use the samples files to calculate the metrics manually. This should correlated to the matrices provided in the results files. We're doing this ourselves to dive deeper into the metrics for the sub-categories.

# %% [markdown]
# Creating the metrics_df framework from below. Pulling the following columns as able:
# 
# task : model : category : sub-category : accurracy : stderr : recall : f1score 
# 
# then we're going to create all of the branches since the samples_ files do not include reference to a model 

# %% [markdown]
# ## Models meta-data
# 
# We use an external excel document to track all of the models.

# %%
import pandas as pd
import numpy as np

# ensure the df_models is empty
df_models = pd.DataFrame()
# Load data from Excel file
df_models = pd.read_excel("models-12092024.xlsx", sheet_name="models")

# Replace "unknown" with NaN for consistent handling
df_models.replace("unknown", np.nan, inplace=True)

# Model Name in the models.xslx should match the "model" column in the samples DataFrame
# Create Model Alias
# df_models['Model Alias'] = df_models['Model Name'].str.replace('/', '__')
# df_models['Model Alias'] = df_models['model'].str.replace('/', '__')

# Convert Release Date to datetime
df_models['FM Release Date'] = pd.to_datetime(df_models['FM Release Date'], errors='coerce')


# %%
df_models

# %% [markdown]
# ## Metrics by Model Only (No Categories or Sub-Categories)

# %%
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def calculate_metrics(df_all_samples_mcqs):
    """
    Calculate performance metrics for each model in the dataset.

    Parameters:
    df_all_samples_mcqs (pd.DataFrame): DataFrame containing columns 'model', 'true_answer', 'predicted_answer', 'model_dtype', 'temperature'.

    Returns:
    pd.DataFrame: DataFrame with calculated metrics for each model.
    """
    # Initialize a list to hold the metrics
    metrics_data = []

    # Group by model and calculate metrics for each group
    for model, group in df_all_samples_mcqs.groupby('model'):
        # Debug: Print group information to understand its structure
        print(f"Debug: Processing model = {model}")
        print(group.head())

        true_answers = group['true_answer']
        predicted_answers = group['predicted_answer']
        task_name = group['task'].iloc[0]
        task_size = group['task_size'].iloc[0]

        # Debug: Print true and predicted answers to check for issues
        print(f"Debug: true_answers = {true_answers}")
        print(f"Debug: predicted_answers = {predicted_answers}")

        # Identify indices where true or predicted answers are None
        invalid_indices = true_answers[true_answers.isna() | predicted_answers.isna()].index
        if not invalid_indices.empty:
            print(f"Debug: Invalid indices with None values: {invalid_indices}")

        # Calculate the metrics
        try:
            accuracy = accuracy_score(true_answers, predicted_answers)
            precision = precision_score(true_answers, predicted_answers, average='macro', zero_division=0)
            recall = recall_score(true_answers, predicted_answers, average='macro', zero_division=0)
            f1 = f1_score(true_answers, predicted_answers, average='macro', zero_division=0)
        except Exception as e:
            # Debug: Print the error if metrics calculation fails
            print(f"Error calculating metrics for model {model}: {e}")
            continue

        # Extract model_dtype and temperature (assuming they are consistent within the group)
        # model_dtype = group['model_dtype'].iloc[0]
        # temperature = group['temperature'].iloc[0]

        # Extract model_dtype and temperature (assuming they are consistent within the group)
        model_dtype = group['model_dtype'].iloc[0]
        if pd.isna(model_dtype):
            model_dtype = 'proprietary'  # Assign 'proprietary' if model_dtype is None
        temperature = group['temperature'].iloc[0]

        # Append the metrics and additional information to the list
        metrics_data.append({
            'task': task_name,
            'task_size': task_size,
            'model': model,
            'model_dtype': model_dtype,
            'temperature': temperature,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
        })

    # Convert the list to a DataFrame
    metrics_df = pd.DataFrame(metrics_data)

    return metrics_df

# Example usage:
df_metrics_only_overall = calculate_metrics(df_all_samples_mcqs)
# Display the DataFrame
print("Metrics Overall DataFrame:")
print(df_metrics_only_overall)

# %%
import pandas as pd

# Assume df is your DataFrame
df_metrics_only_overall['model_name'] = df_metrics_only_overall['model'].str.split('__').str[-1]


# %%
df_metrics_only_overall

# %%
df_models

# %%
# Merge the DataFrames on the 'model alias' column?
df_metrics_only_overall_with_sizes = pd.merge(df_metrics_only_overall, df_models, left_on='model_name', right_on='Model Name on HF', how='left')

# %%
df_metrics_only_overall_with_sizes

# %%
def calculate_defect_density(metrics_df):
    # Calculate incorrect predictions as (1 - accuracy) * task_size
    metrics_df['incorrect_predictions'] = (1 - metrics_df['accuracy']) * metrics_df['task_size']

    # Calculate defect density as incorrect_predictions divided by model size (in billion parameters)
    metrics_df['defect_density'] = metrics_df['incorrect_predictions'] / metrics_df['Parameter Size (Billion Parameters)']

    # Display the updated DataFrame with defect density
    print(metrics_df[['model', 'task', 'accuracy', 'task_size', 'Parameter Size (Billion Parameters)', 'defect_density']])

    return metrics_df

# df_metrics_only_overall_with_sizes_and_defects = calculate_defect_density(df_metrics_only_overall_with_sizes )

# %%

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, LogFormatter, FormatStrFormatter, FuncFormatter

def plot_pareto_frontier(metrics_df,print_pareto_points=False):
    """
    Plot Pareto Frontier for Defect Density vs Model Size and Accuracy vs Model Size.

    Parameters:
    metrics_df (pd.DataFrame): DataFrame containing 'Parameter Size (Billion Parameters)', 'defect_density', 'accuracy', and 'model_name' columns.
    print_pareto_points (bool): If True, prints the models on the Pareto curves with their attributes.
    """
    # Step 1: Sort models by model size for both defect density and accuracy
    metrics_df_sorted_by_defect = metrics_df.sort_values(by='Parameter Size (Billion Parameters)').drop_duplicates(subset='model_name', keep='first')
    metrics_df_sorted_by_accuracy = metrics_df.sort_values(by='Parameter Size (Billion Parameters)').drop_duplicates(subset='model_name', keep='first')

    # Step 2: Identify models on the Pareto frontier for Defect Density (lowest defect density for given model sizes)
    pareto_frontier_defect = []
    min_defect_density = float('inf')

    for _, row in metrics_df_sorted_by_defect.iterrows():
        if row['defect_density'] < min_defect_density:
            pareto_frontier_defect.append(row)
            min_defect_density = row['defect_density']

    pareto_frontier_defect_df = pd.DataFrame(pareto_frontier_defect)
    if print_pareto_points:
        print("Pareto Frontier (Defect Density):")
        print(pareto_frontier_defect_df[['model_name', 'Parameter Size (Billion Parameters)', 'defect_density']])  # ## HERE

    # Step 3: Identify models on the Pareto frontier for Accuracy (highest accuracy for given model sizes)
    pareto_frontier_accuracy = []
    max_accuracy = 0

    for _, row in metrics_df_sorted_by_accuracy.iterrows():
        if row['accuracy'] > max_accuracy:
            pareto_frontier_accuracy.append(row)
            max_accuracy = row['accuracy']

    pareto_frontier_accuracy_df = pd.DataFrame(pareto_frontier_accuracy)
    if print_pareto_points:
        print("\nPareto Frontier (Accuracy):")
        print(pareto_frontier_accuracy_df[['model_name', 'Parameter Size (Billion Parameters)', 'accuracy']])  # ## HERE

    # Step 4: Create a side-by-side plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ------------------------------
    # Left: Pareto Frontier for Defect Density vs Model Parameter Size
    # ------------------------------
    axes[0].scatter(metrics_df['Parameter Size (Billion Parameters)'], metrics_df['defect_density'], color='blue', label='All Models')
    axes[0].plot(pareto_frontier_defect_df['Parameter Size (Billion Parameters)'], pareto_frontier_defect_df['defect_density'], color='orange', marker='o', label='Pareto Frontier (Defect Density)')
    for i in range(len(metrics_df)):
        axes[0].text(metrics_df['Parameter Size (Billion Parameters)'].iloc[i], metrics_df['defect_density'].iloc[i], metrics_df['model_name'].iloc[i], fontsize=9, ha='center', va='center')

    axes[0].set_xscale('log')  # Set x-axis to logarithmic scale
    axes[0].set_yscale('log')  # Set y-axis to logarithmic scale

    # Set the formatter to display numbers in fixed-point notation
    axes[0].xaxis.set_major_formatter(ScalarFormatter())

    # Define custom y-axis formatter
    def yaxis_format_func(value, tick_number):
        if value < 1:
            return f'{value:.2f}'
        else:
            return f'{value:.0f}'

    axes[0].yaxis.set_major_formatter(FuncFormatter(yaxis_format_func))
    axes[0].set_xlim(left=0)
    axes[0].set_ylim(bottom=0.01)
    axes[0].set_xlabel('Model Parameter Size (Billion Parameters)')
    axes[0].set_ylabel('Defect Density')
    axes[0].set_title('Pareto Frontier: Defect Density vs Model Parameter Size')
    axes[0].grid(True, which='both', axis='both')
    axes[0].legend(loc='upper right')

    # ------------------------------
    # Right: Pareto Frontier for Accuracy vs Model Size
    # ------------------------------
    axes[1].scatter(metrics_df['Parameter Size (Billion Parameters)'], metrics_df['accuracy'], color='green', label='All Models')
    axes[1].plot(pareto_frontier_accuracy_df['Parameter Size (Billion Parameters)'], pareto_frontier_accuracy_df['accuracy'], color='orange', marker='o', label='Pareto Frontier (Accuracy)')
    for i in range(len(metrics_df)):
        axes[1].text(metrics_df['Parameter Size (Billion Parameters)'].iloc[i], metrics_df['accuracy'].iloc[i], metrics_df['model_name'].iloc[i], fontsize=9, ha='center', va='center')

    axes[1].set_xscale('log')  # Set x-axis to logarithmic scale
    axes[1].xaxis.set_major_formatter(LogFormatter(labelOnlyBase=True))
    axes[1].set_xlim(left=0)
    axes[1].set_ylim(bottom=0)
    axes[1].set_xlabel('Model Parameter Size (Billion Parameters)')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Pareto Frontier: Accuracy vs Model Parameter Size')
    axes[1].grid(True, which='both', axis='both')
    axes[1].legend(loc='lower right')

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Show the plots
    plt.show()

# Example usage:
plot_pareto_frontier(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True)


# %%
def plot_defect_density_vs_parameter_size_pareto(metrics_df, print_pareto_points=False):
    """
    Plot Pareto Frontier for Defect Density vs Model Parameter Size.

    Parameters:
    metrics_df (pd.DataFrame): DataFrame containing 'Parameter Size (Billion Parameters)', 'defect_density', and 'model_name' columns.
    print_pareto_points (bool): If True, prints the models on the Pareto curve with their attributes.
    """
    metrics_df_sorted = metrics_df.sort_values(by='Parameter Size (Billion Parameters)')
    pareto_frontier = []
    min_defect_density = float('inf')

    for _, row in metrics_df_sorted.iterrows():
        if row['defect_density'] < min_defect_density:
            pareto_frontier.append(row)
            min_defect_density = row['defect_density']

    pareto_frontier_df = pd.DataFrame(pareto_frontier)

    if print_pareto_points:
        print("Pareto Frontier (Defect Density):")
        print(pareto_frontier_df[['model_name', 'Parameter Size (Billion Parameters)', 'defect_density']])

    # Plotting
    plt.figure(figsize=(12, 9))
    plt.scatter(metrics_df['Parameter Size (Billion Parameters)'], metrics_df['defect_density'], color='blue', label='All Models')
    plt.plot(pareto_frontier_df['Parameter Size (Billion Parameters)'], pareto_frontier_df['defect_density'], color='orange', marker='o', label='Pareto Frontier (Defect Density)')

    # Annotate all models on the plot
    for i in range(len(metrics_df)):
        plt.text(metrics_df['Parameter Size (Billion Parameters)'].iloc[i], metrics_df['defect_density'].iloc[i], metrics_df['model_name'].iloc[i], fontsize=9, ha='left', va='center') # ha left is text start at left, center is centered on the text.

    # Only annotate models on the Pareto frontier
    # for i in range(len(pareto_frontier_df)):
    #     plt.text(pareto_frontier_df['Parameter Size (Billion Parameters)'].iloc[i], 
    #              pareto_frontier_df['defect_density'].iloc[i], 
    #              pareto_frontier_df['model_name'].iloc[i], fontsize=9, ha='left', va='bottom') # change va between 'center' and 'left' 
        
    # Alternate annotation position (top/bottom)
    # for i in range(len(pareto_frontier_df)):
    #     va_position = 'top' if i % 2 == 0 else 'bottom'  # Alternate between 'top' and 'bottom'
    #     plt.text(pareto_frontier_df['Parameter Size (Billion Parameters)'].iloc[i] * 1.05,  # Offset to the right
    #              pareto_frontier_df['defect_density'].iloc[i], 
    #              pareto_frontier_df['model_name'].iloc[i], 
    #              fontsize=7, ha='left', va=va_position)  # Alternate vertical alignment


    plt.xscale('log')
    plt.yscale('log')
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.xlabel('Model Parameter Size (Billion Parameters)')
    plt.ylabel('Defect Density')
    # plt.title('Pareto Frontier: Defect Density vs Model Parameter Size')
    plt.grid(True, which='both', axis='both')
    plt.legend(loc='upper right')
    plt.show()

# %%
def plot_accuracy_vs_parameter_size_pareto(metrics_df, print_pareto_points=False):
    """
    Plot Pareto Frontier for Accuracy vs Model Parameter Size.

    Parameters:
    metrics_df (pd.DataFrame): DataFrame containing 'Parameter Size (Billion Parameters)', 'accuracy', and 'model_name' columns.
    print_pareto_points (bool): If True, prints the models on the Pareto curve with their attributes.
    """
    metrics_df_sorted = metrics_df.sort_values(by='Parameter Size (Billion Parameters)')
    pareto_frontier = []
    max_accuracy = 0

    for _, row in metrics_df_sorted.iterrows():
        if row['accuracy'] > max_accuracy:
            pareto_frontier.append(row)
            max_accuracy = row['accuracy']

    pareto_frontier_df = pd.DataFrame(pareto_frontier)

    if print_pareto_points:
        print("Pareto Frontier (Accuracy):")
        print(pareto_frontier_df[['model_name', 'Parameter Size (Billion Parameters)', 'accuracy']])

    # Plotting
    plt.figure(figsize=(12, 9))
    plt.scatter(metrics_df['Parameter Size (Billion Parameters)'], metrics_df['accuracy'], color='green', label='All Models')
    plt.plot(pareto_frontier_df['Parameter Size (Billion Parameters)'], pareto_frontier_df['accuracy'], color='orange', marker='o', label='Pareto Frontier (Accuracy)')

    # Annotate all models on the plot
    for i in range(len(metrics_df)):
        plt.text(metrics_df['Parameter Size (Billion Parameters)'].iloc[i] * 1.05, # offset to the right
                 metrics_df['accuracy'].iloc[i], metrics_df['model_name'].iloc[i], fontsize=6, ha='left', va='center') # change va between 'center' and 'left' 

    # Only annotate models on the Pareto frontier
    # for i in range(len(pareto_frontier_df)):
    #     plt.text(pareto_frontier_df['Parameter Size (Billion Parameters)'].iloc[i], 
    #              pareto_frontier_df['accuracy'].iloc[i], 
    #              pareto_frontier_df['model_name'].iloc[i], fontsize=9, ha='left', va='bottom') # change va between 'center' and 'left' 
        
    # Alternate annotation position (top/bottom) for readability
    # for i in range(len(pareto_frontier_df)):
    #     va_position = 'bottom' if i % 2 == 0 else 'top'  # Alternate between 'top' and 'bottom'
    #     plt.text(pareto_frontier_df['Parameter Size (Billion Parameters)'].iloc[i] * 1.05,  # Slight right offset
    #              pareto_frontier_df['accuracy'].iloc[i] * 1.01,  # Slight vertical shift
    #              pareto_frontier_df['model_name'].iloc[i], 
    #              fontsize=7, ha='left', va=va_position)  # Alternate vertical alignment


    plt.xscale('log')
    plt.gca().xaxis.set_major_formatter(LogFormatter(labelOnlyBase=True))
    plt.xlabel('Model Parameter Size (Billion Parameters)')
    plt.ylabel('Accuracy')
    # plt.title('Pareto Frontier: Accuracy vs Model Parameter Size')
    plt.grid(True, which='both', axis='both')
    plt.legend(loc='lower right')
    plt.show()


# %%
def plot_defect_density_vs_date_with_marginals(metrics_df, print_pareto_points=False):
    """
    Plot Defect Density vs Release Date with scatter plot and marginal histograms.
    """
    metrics_df_sorted = metrics_df.sort_values(by='FM Release Date')
    pareto_frontier = []
    min_defect_density = float('inf')

    for _, row in metrics_df_sorted.iterrows():
        if row['defect_density'] < min_defect_density:
            pareto_frontier.append(row)
            min_defect_density = row['defect_density']

    pareto_frontier_df = pd.DataFrame(pareto_frontier)

    if print_pareto_points:
        print("Pareto Frontier (Defect Density vs Release Date):")
        print(pareto_frontier_df[['model_name', 'FM Release Date', 'defect_density']])

    # Plotting using JointGrid
    g = sns.JointGrid(
        data=metrics_df, x='FM Release Date', y='defect_density', space=0.2, ratio=5
    )

    # Main scatter plot
    g.plot(sns.scatterplot, sns.histplot)
    scatter = g.ax_joint.scatter(
        pareto_frontier_df['FM Release Date'],
        pareto_frontier_df['defect_density'],
        color='orange',
        label='Pareto Frontier (Lowest Defect Density for Model Sizes)',
        s=100,
        zorder=10
    )

    # Marginal histograms
    g.ax_marg_x.hist(metrics_df['FM Release Date'], bins=20, color='blue', alpha=0.7)
    g.ax_marg_y.hist(metrics_df['defect_density'], bins=20, color='blue', alpha=0.7, orientation='horizontal')

    # Adding labels, title, and grid
    g.set_axis_labels('Release Date', 'Defect Density')
    plt.suptitle('Defect Density vs Release Date with Marginals', y=1.02)
    g.ax_joint.legend(handles=[scatter], loc='upper right', title='Legend')
    g.ax_joint.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # Rotate x-axis labels vertically
    for label in g.ax_joint.get_xticklabels():
        label.set_rotation(90)
        label.set_ha('center')

    plt.show()


# %%
def plot_accuracy_vs_date_with_marginals(metrics_df, print_pareto_points=False, use_kde=False):
    """
    Plot Accuracy vs Release Date with scatter plot and marginal histograms or KDE curves.
    
    Parameters:
    metrics_df (pd.DataFrame): DataFrame with columns 'FM Release Date', 'accuracy', and 'model_name'.
    print_pareto_points (bool): Whether to print Pareto frontier points.
    use_kde (bool): If True, use KDE for marginal distributions; otherwise, use histograms.
    """
    metrics_df_sorted = metrics_df.sort_values(by='FM Release Date')
    pareto_frontier = []
    max_accuracy = 0

    for _, row in metrics_df_sorted.iterrows():
        if row['accuracy'] > max_accuracy:
            pareto_frontier.append(row)
            max_accuracy = row['accuracy']

    pareto_frontier_df = pd.DataFrame(pareto_frontier)

    if print_pareto_points:
        print("Pareto Frontier (Accuracy vs Release Date):")
        print(pareto_frontier_df[['model_name', 'FM Release Date', 'accuracy']])

    # Plotting using JointGrid
    g = sns.JointGrid(
        data=metrics_df, x='FM Release Date', y='accuracy', space=0.2, ratio=5
    )

    # Main scatter plot
    g.plot(sns.scatterplot, sns.kdeplot if use_kde else sns.histplot)
    scatter = g.ax_joint.scatter(
        pareto_frontier_df['FM Release Date'],
        pareto_frontier_df['accuracy'],
        color='orange',
        label='Pareto Frontier (Highest Accuracy for Model Sizes)',
        s=100,
        zorder=10
    )

    # Marginal plots
    if use_kde:
        sns.kdeplot(
            data=metrics_df, x='FM Release Date', ax=g.ax_marg_x,
            color='green', fill=True, alpha=0.4, linewidth=2
        )
        sns.kdeplot(
            data=metrics_df, y='accuracy', ax=g.ax_marg_y,
            color='green', fill=True, alpha=0.4, linewidth=2
        )
    else:
        g.ax_marg_x.hist(
            metrics_df['FM Release Date'], bins=20, color='green', alpha=0.4, edgecolor='black'
        )
        g.ax_marg_y.hist(
            metrics_df['accuracy'], bins=20, color='green', alpha=0.4,
            edgecolor='black', orientation='horizontal'
        )

    # Adding labels, title, and grid
    g.set_axis_labels('Release Date', 'Accuracy')
    plt.suptitle('Accuracy vs Release Date with Marginals', y=1.02)
    g.ax_joint.legend(handles=[scatter], loc='lower right', title='Legend')
    g.ax_joint.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # Rotate x-axis labels vertically
    for label in g.ax_joint.get_xticklabels():
        label.set_rotation(90)
        label.set_ha('center')

    plt.show()


# %%
import seaborn as sns
################ OVERALL EXECUTION WORKFLOW ###################
df_all_samples_mcqs = extract_samples_data(df_all_results_files_info_filtered)
df_metrics_only_overall = calculate_metrics(df_all_samples_mcqs)

# Merge the DataFrames on the 'model alias' column?
df_metrics_only_overall['model_name'] = df_metrics_only_overall['model'].str.split('__').str[-1]
#### below line isnt working. troubleshoot if i want...it's becuase i add some stuff above that is unaccounted for.

df_metrics_only_overall_with_sizes = pd.merge(df_metrics_only_overall, df_models, left_on='model_name', right_on='Foundation Model (FM) Name', how='left')
df_metrics_only_overall_with_sizes_and_defects = calculate_defect_density(df_metrics_only_overall_with_sizes )
# plot_pareto_frontier(df_metrics_only_overall_with_sizes_and_defects)
# Now working to create 

# splitting pareto plotting into 2 different plots for ease of sharing with journal
plot_defect_density_vs_parameter_size_pareto(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True)
plot_accuracy_vs_parameter_size_pareto(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True)

# Pareto Frontier for Defect Density vs Release Date
plot_defect_density_vs_date_with_marginals(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True)
# Pareto Frontier for Accuracy vs Release Date
# plot_accuracy_vs_date_with_marginals(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True)


# With traditional histograms
plot_accuracy_vs_date_with_marginals(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True, use_kde=False)

# With KDE curves
plot_accuracy_vs_date_with_marginals(df_metrics_only_overall_with_sizes_and_defects, print_pareto_points=True, use_kde=True)


# %%


# %%


# %% [markdown]
# # Maybe adding sunburst plot instead of doing a giant table.
# ![image.png](attachment:image.png)

# %%
# Add a bold black outline around the highest score in each row
plt.figure(figsize=(16, 10))
ax = sns.heatmap(data.drop(columns=['Category']), annot=False, cmap="viridis", cbar_kws={"label": "Percent Correct"})

# Loop through each row and highlight the maximum value
for i, row in enumerate(data.drop(columns=['Category']).values):
    max_col = np.argmax(row)
    ax.add_patch(plt.Rectangle((max_col, i), 1, 1, fill=False, edgecolor='black', lw=2))

plt.title("Heatmap: Subcategory Performance Across Models (Highlighted Max Values)", fontsize=16)
plt.xlabel("Models")
plt.ylabel("Subcategories")
plt.tight_layout()
plt.show()

# Create a sunburst plot to visualize hierarchical data
import plotly.express as px

# Prepare data for the sunburst
sunburst_data = pd.DataFrame({
    "Category": [data['Category'][i // len(models)] for i in range(len(data.index) * len(models))],
    "Subcategory": np.repeat(data.index, len(models)),
    "Model": np.tile(models, len(data.index)),
    "Accuracy": data.drop(columns=['Category']).values.flatten()
})

# Plot the sunburst
fig = px.sunburst(
    sunburst_data,
    path=["Category", "Subcategory", "Model"],
    values="Accuracy",
    color="Accuracy",
    color_continuous_scale="Viridis",
    title="Sunburst Chart: Accuracy Across Categories, Subcategories, and Models",
)

fig.show()


# %%


# %%


# %%


# %%


# %% [markdown]
# # Parsing and Exploding the INCOSE Handbook Categories 

# %%
print(df_all_samples_mcqs)


# %%
##### first we need to explode the INCOSE Handbook Category column to get the individual categories
df_all_samples_mcqs_test = df_all_samples_mcqs
# need to take the last string behind the / and before the newline character
print(df_all_samples_mcqs_test)

print("========== BREAK =============")

def explode_incose_handbook_category(df):
    # Fill NaN values with empty strings to prevent issues during splitting
    df = df.copy()
    df.loc[:, 'INCOSE Handbook Category'] = df['INCOSE Handbook Category'].fillna('')
    
    # Explode 'INCOSE Handbook Category' by splitting on newline characters
    incose_expanded = df['INCOSE Handbook Category'].str.split('\n').explode()

    # Create a new DataFrame with expanded rows dynamically copying all columns
    incose_expanded_df = df.loc[incose_expanded.index].copy()
    incose_expanded_df['INCOSE Handbook Category'] = incose_expanded.values

    # Split 'INCOSE Handbook Category' into 'INCOSE Category' and 'INCOSE Sub-Category'
    incose_expanded_df[['INCOSE Category', 'INCOSE Sub-Category']] = incose_expanded_df['INCOSE Handbook Category'] \
        .str.extract(r'INCOSEHandbook/([^/]+)/(.+)')

    return incose_expanded_df.reset_index(drop=True)


expanded_df = explode_incose_handbook_category(df_all_samples_mcqs_test)
print(expanded_df)


# %% [markdown]
# # Metrics by Category and Subcategory

# %%
def calculate_metrics(df):
    # Grouping by model, INCOSE Category, and INCOSE Sub-Category
    grouped = df.groupby(['model', 'INCOSE Category', 'INCOSE Sub-Category'])

    # Calculating metrics for each group
    metrics = grouped.agg(
        total_questions=('question', 'count'),
        correct_predictions=('true_answer', lambda x: (x == df.loc[x.index, 'predicted_answer']).sum()),
        accuracy=('true_answer', lambda x: (x == df.loc[x.index, 'predicted_answer']).mean())
    ).reset_index()

    return metrics
metrics_df = calculate_metrics(expanded_df)
print(metrics_df)


# %%
metrics_df

# %% [markdown]
# # Exporting to Excel

# %%
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Alignment


def create_metrics_overview_sheet(metrics_df, wb):
    """
    Create the Metrics Overview sheet with color-coded formatting.

    Parameters:
    metrics_df (pd.DataFrame): DataFrame containing the metrics data.
    wb (Workbook): The Excel workbook to add the sheet to.
    """
    # Add a worksheet for metrics overview
    ws = wb.create_sheet(title="Metrics Overview")

    # Extract overall accuracy by model
    overall_accuracy = metrics_df.groupby('model')['accuracy'].mean().reset_index()
    overall_accuracy_dict = overall_accuracy.set_index('model')['accuracy'].to_dict()
    print("Overall accuracy by model:")
    print(overall_accuracy)

    # Get all unique categories and subcategories
    all_categories = metrics_df['INCOSE Category'].unique().tolist()
    print("All categories:")
    print(all_categories)

    # Create the header rows
    ws.append(["LLM", "LLM Overall Accuracy"] + all_categories)
    print("Header row created.")

    # Create the sub-header rows
    sub_headers = ["LLM", "LLM Overall Accuracy"]
    for category in all_categories:
        sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
        print(f"Subcategories for category '{category}': {sub_categories}")  # Debug output
        sub_headers.extend(sub_categories)
    ws.append(sub_headers)
    print("Sub-header row created:")
    print(sub_headers)

    # Fill in the data rows
    for model in metrics_df['model'].unique():
        row = [model, f"{overall_accuracy_dict[model]:.2f}"]
        for category in all_categories:
            sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
            for sub_category in sub_categories:
                accuracy = metrics_df[(metrics_df['model'] == model) &
                                      (metrics_df['INCOSE Category'] == category) &
                                      (metrics_df['INCOSE Sub-Category'] == sub_category)]['accuracy']
                if not accuracy.empty:
                    row.append(f"{accuracy.iloc[0]:.2f}")
                else:
                    row.append("N/A")
        ws.append(row)
        print(f"Data row for model {model} added:")
        print(row)

    # Format the header rows
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    for cell in ws[2]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Adjusting the top header row to avoid overwriting categories during merging
    col_idx = 3
    for category in all_categories:
        sub_categories_count = len(metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique())
        print(f"Merging cells for category '{category}' from column {col_idx} to {col_idx + sub_categories_count - 1}")
        if sub_categories_count > 0:  # Only merge if there are subcategories
            ws.merge_cells(start_row=1, start_column=col_idx, end_row=1, end_column=col_idx + sub_categories_count - 1)
            # Set the value for the merged cells
            ws.cell(row=1, column=col_idx).value = category
        col_idx += sub_categories_count

    # Merge cells for the LLM and LLM Overall Accuracy columns
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    print("Merged cells for LLM and LLM Overall Accuracy columns.")


def create_metrics_overview_detailed_sheet(metrics_df, wb):
    """
    Create the Metrics Overview sheet with an additional row for category-level accuracies,
    calculating accuracies based on weighted averages considering total questions.
    Merge the 'LLM' and 'LLM Overall Accuracy' cells for each model across the two data rows.
    Make the text for all subcategory columns vertical and adjust the row height to accommodate the rotated text.
    Display all accuracy results to two decimal places.
    
    Parameters:
    metrics_df (pd.DataFrame): DataFrame containing the metrics data.
    wb (Workbook): The Excel workbook to add the sheet to.
    """
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    # Add a worksheet for metrics overview
    ws = wb.create_sheet(title="Metrics Overview Detailed")

    # Compute overall accuracy per model based on total correct predictions and total questions
    model_totals = metrics_df.groupby('model').agg({'correct_predictions': 'sum', 'total_questions': 'sum'}).reset_index()
    model_totals['accuracy'] = model_totals['correct_predictions'] / model_totals['total_questions']
    overall_accuracy_dict = model_totals.set_index('model')['accuracy'].to_dict()

    # Get all unique categories and subcategories
    all_categories = metrics_df['INCOSE Category'].unique().tolist()

    # Create the header and sub-header rows
    ws.append(["LLM", "LLM Overall Accuracy"] + all_categories)
    sub_headers = ["LLM", "LLM Overall Accuracy"]
    for category in all_categories:
        sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
        sub_headers.extend(sub_categories)
    ws.append(sub_headers)

    # Format the header rows
    # Row 1: Categories
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    # Row 2: Subcategories
    for idx, cell in enumerate(ws[2], start=1):
        cell.font = Font(bold=True)
        if idx > 2:  # Skip the first two columns ('LLM' and 'LLM Overall Accuracy')
            cell.alignment = Alignment(horizontal="center", vertical="bottom", text_rotation=90)
        else:
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Adjusting the top header row to avoid overwriting categories during merging
    col_idx = 3
    for category in all_categories:
        sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
        sub_categories_count = len(sub_categories)
        if sub_categories_count > 0:  # Only merge if there are subcategories
            ws.merge_cells(start_row=1, start_column=col_idx, end_row=1, end_column=col_idx + sub_categories_count - 1)
            ws.cell(row=1, column=col_idx).value = category
            # Center align the merged header cell
            ws.cell(row=1, column=col_idx).alignment = Alignment(horizontal="center", vertical="center")
        col_idx += sub_categories_count

    # Merge cells for the LLM and LLM Overall Accuracy columns in the header
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    # Center align the merged LLM cells
    ws.cell(row=1, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=1, column=2).alignment = Alignment(horizontal="center", vertical="center")

    # Fill in the data rows
    for model in metrics_df['model'].unique():
        # Record the starting row for this model
        start_row = ws.max_row + 1  # Since ws.max_row gives the last row with data, we add 1

        # Row 1: Subcategory-level accuracies
        row_subcategory = [model, f"{overall_accuracy_dict[model]:.2f}"]
        for category in all_categories:
            sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
            for sub_category in sub_categories:
                subcategory_data = metrics_df[(metrics_df['model'] == model) &
                                              (metrics_df['INCOSE Category'] == category) &
                                              (metrics_df['INCOSE Sub-Category'] == sub_category)]
                if not subcategory_data.empty:
                    total_correct = subcategory_data['correct_predictions'].sum()
                    total_questions = subcategory_data['total_questions'].sum()
                    accuracy = total_correct / total_questions if total_questions > 0 else float('nan')
                    row_subcategory.append(f"{accuracy:.2f}")
                else:
                    row_subcategory.append("N/A")
        ws.append(row_subcategory)

        # Row 2: Category-level accuracies (with merged cells)
        row_category = [model, f"{overall_accuracy_dict[model]:.2f}"]
        merge_info = []  # To store the merging information
        col_idx = 3  # Starting from the third column
        for category in all_categories:
            sub_categories = metrics_df[metrics_df['INCOSE Category'] == category]['INCOSE Sub-Category'].unique().tolist()
            sub_categories_count = len(sub_categories)
            category_data = metrics_df[(metrics_df['model'] == model) & (metrics_df['INCOSE Category'] == category)]
            total_correct = category_data['correct_predictions'].sum()
            total_questions = category_data['total_questions'].sum()
            if total_questions > 0:
                category_accuracy = total_correct / total_questions
                row_category.append(f"{category_accuracy:.2f}")
            else:
                row_category.append("N/A")
            # Fill the remaining cells with empty strings
            row_category.extend([""] * (sub_categories_count - 1))
            # Store the columns to merge
            if sub_categories_count > 0:
                merge_info.append((col_idx, col_idx + sub_categories_count - 1))
            col_idx += sub_categories_count
        ws.append(row_category)

        # Merge the category accuracy cells
        current_row = ws.max_row  # This is the row number of row_category
        for start_col, end_col in merge_info:
            ws.merge_cells(start_row=current_row, start_column=start_col, end_row=current_row, end_column=end_col)
            # Center align the merged cells
            cell = ws.cell(row=current_row, column=start_col)
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Merge the 'LLM' and 'LLM Overall Accuracy' cells across the two data rows
        for col in [1, 2]:  # Columns for 'LLM' and 'LLM Overall Accuracy'
            ws.merge_cells(start_row=start_row, start_column=col, end_row=current_row, end_column=col)
            # Center align the merged cells
            cell = ws.cell(row=start_row, column=col)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(bold=True)

        # Apply center alignment to data cells under subcategory columns
        for row in ws.iter_rows(min_row=start_row, max_row=current_row, min_col=3):
            for cell in row:
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Adjust column widths based on maximum content length in each column
    for idx, col in enumerate(ws.columns, start=1):
        col_cells = list(col)
        column_index = col_cells[0].column  # Get the column index
        column_letter = get_column_letter(column_index)
        max_length = 0
        for cell in col_cells:
            try:
                if cell.value:
                    # For rotated text, length does not affect column width
                    if cell.row == 2 and idx > 2:
                        continue  # Skip adjusting width based on rotated text
                    else:
                        max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column_letter].width = adjusted_width

    # Set row height for subcategory header row to accommodate rotated text
    ws.row_dimensions[2].height = 100  # Adjust this value as needed

def create_metrics_df_sheet(metrics_df, wb):
    """
    Export the metrics DataFrame to an Excel workbook as a separate sheet.

    Parameters:
    metrics_df (pd.DataFrame): The metrics DataFrame to export.
    wb (Workbook): The Excel workbook to add the sheet to.
    """
    # Add a worksheet for metrics_df
    ws = wb.create_sheet(title="Metrics DataFrame")

    # Write the headers to the worksheet
    ws.append(metrics_df.columns.tolist())
    print("Headers written to Metrics DataFrame worksheet.")

    # Write the data to the worksheet
    for row in metrics_df.itertuples(index=False, name=None):
        ws.append(row)
    print("Data written to Metrics DataFrame worksheet.")


def highlight_best_answers(wb, highlight=True, highlight_color="C6EFCE", bold=False):
    """
    Highlight the best answers in the "Metrics Overview" sheet by filling cells with the highest values in a given color or making them bold.

    Parameters:
    wb (Workbook): The Excel workbook containing the "Metrics Overview" sheet.
    highlight (bool): Whether to highlight the best cells.
    highlight_color (str): The color to use for highlighting.
    bold (bool): Whether to make the best cells bold.
    """
    # Select the Metrics Overview sheet
    ws = wb["Metrics Overview"]

    # Define the highlight fill and font styles
    fill = PatternFill(start_color=highlight_color, end_color=highlight_color, fill_type="solid")
    bold_font = Font(bold=True)

    # Highlight or bold the best answers
    print("Finding the best values in each column and applying formatting...")
    for col in ws.iter_cols(min_row=3, min_col=3):
        best_value = None
        for cell in col:
            if isinstance(cell.value, str) and cell.value != "N/A":
                try:
                    value = float(cell.value)
                    if best_value is None or value > best_value:
                        best_value = value
                except ValueError:
                    continue
        for cell in col:
            if isinstance(cell.value, str) and cell.value != "N/A":
                try:
                    value = float(cell.value)
                    if value == best_value:
                        if highlight:
                            print(f"Highlighting cell {cell.coordinate} with color {highlight_color}")
                            cell.fill = fill
                        if bold:
                            print(f"Making cell {cell.coordinate} bold")
                            cell.font = bold_font
                except ValueError:
                    continue

def highlight_best_category_accuracies(wb, highlight=True, highlight_color="C6EFCE", bold=False):
    """
    Highlight the best category-level accuracies in the "Metrics Overview Detailed" sheet by filling cells with the highest values in a given color or making them bold.

    Parameters:
    wb (Workbook): The Excel workbook containing the "Metrics Overview Detailed" sheet.
    highlight (bool): Whether to highlight the best cells.
    highlight_color (str): The color to use for highlighting.
    bold (bool): Whether to make the best cells bold.
    """
    from openpyxl.styles import Font, PatternFill

    # Select the "Metrics Overview Detailed" sheet
    ws = wb["Metrics Overview Detailed"]

    # Define the highlight fill and font styles
    fill = PatternFill(start_color=highlight_color, end_color=highlight_color, fill_type="solid")
    bold_font = Font(bold=True)

    # Find the starting row of the data (after the headers)
    # Assuming headers are in rows 1 and 2
    data_start_row = 3

    # Identify the columns for categories
    # Categories are in the first header row (row 1), starting from column 3
    category_columns = []
    col_idx = 3
    while True:
        cell = ws.cell(row=1, column=col_idx)
        if cell.value is None:
            break  # End of categories
        # Get the number of subcategories under this category
        merged_cells = ws.merged_cells.ranges
        merged_range = None
        for merged_cell in merged_cells:
            if cell.coordinate in merged_cell:
                merged_range = merged_cell
                break
        if merged_range:
            start_col = merged_range.min_col
            end_col = merged_range.max_col
        else:
            start_col = col_idx
            end_col = col_idx
        category_columns.append((cell.value, start_col, end_col))
        col_idx = end_col + 1

    # Iterate over each category to find and highlight the best accuracy
    for category_name, start_col, end_col in category_columns:
        best_value = None
        best_cells = []
        # Iterate over the category-level accuracy rows
        # Assuming that for each model, category accuracies are in the second row of their data block
        row_idx = data_start_row
        while row_idx <= ws.max_row:
            # Get the cell for this category's accuracy (merged cell)
            cell = ws.cell(row=row_idx + 1, column=start_col)  # row_idx + 1 because category accuracies are in the second row
            value = cell.value
            if isinstance(value, str) and value != "N/A":
                try:
                    accuracy = float(value)
                    if best_value is None or accuracy > best_value:
                        best_value = accuracy
                        best_cells = [cell]
                    elif accuracy == best_value:
                        best_cells.append(cell)
                except ValueError:
                    pass
            row_idx += 2  # Move to the next model's data block (each model has two data rows)

        # Highlight the best cells
        for cell in best_cells:
            # Apply formatting to the merged cell
            if highlight:
                cell.fill = fill
            if bold:
                cell.font = bold_font

    # Optionally, highlight the best overall accuracies in the 'LLM Overall Accuracy' column (column 2)
    best_overall_value = None
    best_overall_cells = []
    row_idx = data_start_row
    while row_idx <= ws.max_row:
        cell = ws.cell(row=row_idx, column=2)  # Overall accuracy is in column 2
        value = cell.value
        if isinstance(value, str) and value != "N/A":
            try:
                accuracy = float(value)
                if best_overall_value is None or accuracy > best_overall_value:
                    best_overall_value = accuracy
                    best_overall_cells = [cell]
                elif accuracy == best_overall_value:
                    best_overall_cells.append(cell)
            except ValueError:
                pass
        row_idx += 2  # Move to the next model's data block

    # Highlight the best overall accuracy cells
    for cell in best_overall_cells:
        if highlight:
            cell.fill = fill
        if bold:
            cell.font = bold_font



# Usage example
wb = Workbook()
wb.remove(wb.active)  # Remove the default sheet
create_metrics_overview_sheet(metrics_df, wb)
create_metrics_overview_detailed_sheet(metrics_df, wb)

create_metrics_df_sheet(metrics_df, wb)

# Highlight best subcategory answers in the "Metrics Overview" sheet
highlight_best_answers(wb, highlight=True, highlight_color="C6EFCE", bold=True)
# Highlight best category answers in the "Metrics Overview Detailed" sheet
highlight_best_category_accuracies(wb, highlight=True, highlight_color="C6EFCE", bold=True)


# Save workbook
try:
    print("Saving workbook...")
    wb.save("publication_metrics.xlsx")
    print("Workbook saved as 'publication_metrics.xlsx'.")
except PermissionError:
    temp_filename = "temp_publication_metrics.xlsx"
    print("Attempting to save as a temporary file due to permission issues...")
    wb.save(temp_filename)
    print(f"Workbook saved as temporary file: '{temp_filename}' due to permission issues.")


# %%


# %% [markdown]
# # Add Export to LaTeX here.

# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %% [markdown]
# ## Tables

# %%
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

# Assuming metrics_df is already defined and contains the calculated metrics

# Step 1: Split 'incose_category' into different levels using the '/' character
category_levels = metrics_df['incose_category'].str.split('/', expand=True)
metrics_df['Level 1'] = category_levels[0]
metrics_df['Level 2'] = category_levels[1]
metrics_df['Level 3'] = category_levels[2]

# Step 2: Create a summary for each level with TOTALs for aggregation

# Summary for Level 3 (granular level)
level_3_summary = metrics_df.groupby(['task', 'model', 'Level 1', 'Level 2', 'Level 3']).agg({
    'accuracy': 'mean',
    'stderr': 'mean',
    'precision': 'mean',
    'recall': 'mean',
    'f1_score': 'mean'
}).reset_index()

# Summary for Level 2 with TOTALs for Level 3
level_2_summary = metrics_df.groupby(['task', 'model', 'Level 1', 'Level 2']).agg({
    'accuracy': 'mean',
    'stderr': 'mean',
    'precision': 'mean',
    'recall': 'mean',
    'f1_score': 'mean'
}).reset_index()
level_2_summary['Level 3'] = 'TOTAL'

# Summary for Level 1 with TOTALs for Level 2
level_1_summary = metrics_df.groupby(['task', 'model', 'Level 1']).agg({
    'accuracy': 'mean',
    'stderr': 'mean',
    'precision': 'mean',
    'recall': 'mean',
    'f1_score': 'mean'
}).reset_index()
level_1_summary['Level 2'] = 'TOTAL'
level_1_summary['Level 3'] = 'TOTAL'

# Combine all summaries into one single DataFrame with TOTALs at each level
combined_summary = pd.concat([level_3_summary, level_2_summary, level_1_summary], ignore_index=True)

# Sort the combined summary for better readability
combined_summary.sort_values(by=['task', 'model', 'Level 1', 'Level 2', 'Level 3'], inplace=True)

# Step 3: Generate a publication-worthy table for the combined summary
combined_table_str = tabulate(combined_summary, headers='keys', tablefmt='github', floatfmt='.2f')
print("Combined Summary with TOTALs for All Levels:")
print(combined_table_str)



# %%


# %% [markdown]
# ## Bar Charts

# %% [markdown]
# ### By Model Release Date

# %%
print(metrics_df)

# %%
# Step 1: Split 'incose_category' into different levels using the '/' character
category_levels = metrics_df['incose_category'].str.split('/', expand=True)
metrics_df['Level 1'] = category_levels[0]
metrics_df['Level 2'] = category_levels[1]
metrics_df['Level 3'] = category_levels[2]

import seaborn as sns
# Sort the merged DataFrame by release date
metrics_df.sort_values(by='Release Date', inplace=True)

# Plotting overall accuracy by second-level category with bar graphs
plt.figure(figsize=(12, 8))
barplot = sns.barplot(x=metrics_df.apply(lambda row: f"{row['model']}\n({row['Release Date'].strftime('%Y-%m-%d')})", axis=1), y='accuracy', hue='Level 2', data=metrics_df)

# add the accuracy at the base of the bars
for p in barplot.patches:
    if p.get_height() > 0:
        barplot.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., 0), 
                        ha='center', va='center', 
                        xytext=(0, 9), 
                        textcoords='offset points')
        
        
plt.title('Accuracy of Model Performance in Second-Level Categories By Release Date')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
# add dashed grid lines
plt.grid(axis='y', linestyle='--')
plt.ylim(0, 1)
plt.legend(title='Second-Level Category')
plt.tight_layout()
plt.show()


# %% [markdown]
# ######## BELOW NEEDS UPDATING

# %%
import seaborn as sns
# Sort the merged DataFrame by release date
metrics_df.sort_values(by='Release Date', inplace=True)

# Plotting overall accuracy by category with bar graphs
plt.figure(figsize=(12, 8))
barplot = sns.barplot(x=metrics_df.apply(lambda row: f"{row['model']}\n({row['Release Date'].strftime('%Y-%m-%d')})", axis=1), y='accuracy', hue='Level 3', data=metrics_df)

# add the accuracy at the base of the bars
for p in barplot.patches:
    if p.get_height() > 0:
        barplot.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., 0), 
                        ha='center', va='center', 
                        xytext=(0, 9), 
                        textcoords='offset points')
        
        
plt.title('Accuracy of Model Performance in Categories By Release Date')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
# add dashed grid lines
plt.grid(axis='y', linestyle='--')
plt.ylim(0, 1)
plt.legend(title='Category')
plt.tight_layout()
plt.show()

# %% [markdown]
# ### By Model Size

# %%
# Sort the merged DataFrame by release date
metrics_df.sort_values(by='Size (Billion Parameters)', inplace=True)

# Plotting overall accuracy by category with bar graphs
plt.figure(figsize=(12, 8))
barplot = sns.barplot(x=metrics_df.apply(lambda row: f"{row['model']}\n({row['Size (Billion Parameters)']}B)", axis=1), y='accuracy', hue='category', data=metrics_df)

# add the accuracy at the base of the bars
for p in barplot.patches:
    if p.get_height() > 0:
        barplot.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., 0), 
                        ha='center', va='center', 
                        xytext=(0, 9), 
                        textcoords='offset points')
        
plt.title('Accuracy of Model Performance in Categories By Model Size')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
# add dashed grid lines
plt.grid(axis='y', linestyle='--')
plt.ylim(0, 1)
plt.legend(title='Category')
# plt.legend(title='Category', bbox_to_anchor=(0.5, 1.15), loc='center')
plt.tight_layout()
plt.show()


# %%
# Sort the merged DataFrame by release date
metrics_df.sort_values(by='Size (Billion Parameters)', inplace=True)

# Plotting overall accuracy by category with bar graphs
plt.figure(figsize=(12, 8))
barplot = sns.barplot(x=metrics_df.apply(lambda row: f"{row['model']}\n({row['Size (Billion Parameters)']}B)", axis=1), y='accuracy', hue='sub_category', data=metrics_df)
# put text of the accuracy on the bars if height is non-zero
for p in barplot.patches:
    if p.get_height() > 0:
        barplot.annotate(format(p.get_height(), '.2f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha='center', va='center', 
                         xytext=(0, 9), 
                         textcoords='offset points',
                         rotation=90)
plt.title('Accuracy of Model Performance in Categories By Model Size')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
# add dashed grid lines
plt.grid(axis='y', linestyle='--')
plt.ylim(0, 1)
plt.legend(title='Sub-Category')
plt.tight_layout()
plt.show()

# %% [markdown]
# # Appendix: Question Analysis - Too Easy or Too Hard?
# Visualizing the raw Question and Answer Stats by Question (in work)

# %% [markdown]
# ## Overall Heatmap

# %% [markdown]
# These should look like below...
# 
# ![image.png](attachment:image.png)
# 
# 
# ![image-2.png](attachment:image-2.png)
# 
# 
# 

# %%
df_all_samples_mcqs

# %%
# Step 1: Map questions to sequential numbers
# df_all_samples_mcqs['question_num'] = df_all_samples_mcqs.groupby('category').cumcount() + 1

# Step 2: Calculate correctness directly
df_all_samples_mcqs['correct'] = (df_all_samples_mcqs['predicted_answer'] == df_all_samples_mcqs['true_answer']).astype(int)


# %%
# Check the data type of the "correct" column
print(df_all_samples_mcqs['correct'].dtype)


# %%
import pandas as pd
import numpy as np

# Get unique models and question numbers
unique_models = df_all_samples_mcqs['model'].unique()
unique_question_nums = df_all_samples_mcqs['question_number'].unique()

# Initialize the new DataFrame for the heatmap with NaN values
heatmap_data = pd.DataFrame(data=np.nan, index=unique_models, columns=unique_question_nums)



# %%
# Populate the heatmap DataFrame
for _, row in df_all_samples_mcqs.iterrows():
    model = row['model']
    question_num = row['question_number']
    correct = row['correct']
    
    # If there are duplicates, decide how to handle them, e.g., taking the mean
    if pd.isna(heatmap_data.at[model, question_num]):
        heatmap_data.at[model, question_num] = correct
    else:
        # For duplicates, you could average the value or choose another method
        heatmap_data.at[model, question_num] = (heatmap_data.at[model, question_num] + correct) / 2


# %%
# Computing the average row
average_per_question = heatmap_data.mean(axis=0)

# Add the average as a new row to the DataFrame
heatmap_data.loc['Average'] = average_per_question

# Optional: Move the 'Average' row to the top
heatmap_data = pd.concat([heatmap_data.loc[['Average']], heatmap_data.drop('Average')])


# %%
heatmap_data

# %%
# Set up the matplotlib figure
plt.figure(figsize=(20, 10))

# Create the heatmap
sns.heatmap(heatmap_data, cmap="RdYlGn", cbar_kws={'label': 'Correct (1.0) or Incorrect (0.0)'})

# Add labels and title
plt.xlabel('Question Number')
plt.ylabel('Model')
plt.title('Heatmap of Model Performance on SysEngBench Questions')

# Show the plot
plt.show()


# sns.heatmap(heatmap_data, cmap="RdYlGn", cbar=True, linewidths=.5, annot=True, vmin=0, vmax=1)


# %% [markdown]
# ## Category and Sub-Category Heatmap Subplots

# %%
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd

# Flag to include or exclude the average row
include_average = True  # Set to False if you don't want the average row

# Assuming df_all_samples_mcqs is your DataFrame
df = df_all_samples_mcqs

# Get unique categories
unique_categories = df['category'].unique()
num_categories = len(unique_categories)

# Determine the number of rows and columns for subplots (e.g., 2x2 grid)
cols = 2
rows = math.ceil(num_categories / cols)

# Set up the matplotlib figure with subplots
fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(20, rows * 5))

# Flatten the axes array for easy iteration
axes = axes.flatten()

# Loop through each category and generate a heatmap subplot
for i, category in enumerate(unique_categories):
    # Filter data by category
    df_category = df[df['category'] == category]

    # Pivot the data to create a heatmap structure
    heatmap_data_category = df_category.pivot(index='model', columns='question_number', values='correct')

    if include_average:
        # Calculate the average row
        average_per_question = heatmap_data_category.mean(axis=0)
        heatmap_data_category.loc['Average'] = average_per_question

        # Move the 'Average' row to the top
        heatmap_data_category = pd.concat([heatmap_data_category.loc[['Average']], heatmap_data_category.drop('Average')])

    # Create the heatmap in the appropriate subplot
    sns.heatmap(heatmap_data_category, cmap="RdYlGn", cbar_kws={'label': 'Correct (1.0) or Incorrect (0.0)'}, ax=axes[i])

    # Add labels and title to each subplot
    axes[i].set_title(f'Performance on Category: {category}')
    axes[i].set_xlabel('Question Number')
    axes[i].set_ylabel('Model')

# Hide any unused axes
for j in range(i + 1, len(axes)):
    axes[j].axis('off')  # Turn off the axis

# Adjust layout
plt.tight_layout()
plt.show()


# %%
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd

# Flag to include or exclude the average row
include_average = True  # Set to False if you don't want the average row

# Assuming df_all_samples_mcqs is your DataFrame
df = df_all_samples_mcqs

# Get unique categories
unique_categories = df['category'].unique()

# Loop through each category
for category in unique_categories:
    # Filter data by category
    df_category = df[df['category'] == category]

    # Get unique sub-categories for the current category
    unique_sub_categories = df_category['sub_category'].unique()
    num_sub_categories = len(unique_sub_categories)

    # Determine the number of rows and columns for subplots (e.g., 2x2 grid)
    cols = 2
    rows = math.ceil(num_sub_categories / cols)

    # Set up the matplotlib figure with subplots
    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(20, rows * 5))
    
    # Flatten the axes array for easy iteration (if more than one subplot)
    if num_sub_categories > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    # Loop through each sub-category and generate a heatmap subplot
    for i, sub_category in enumerate(unique_sub_categories):
        # Filter data by sub-category
        df_sub_category = df_category[df_category['sub_category'] == sub_category]

        # Pivot the data to create a heatmap structure
        heatmap_data_sub_category = df_sub_category.pivot(index='model', columns='question_number', values='correct')

        if include_average:
            # Calculate the average row
            average_per_question = heatmap_data_sub_category.mean(axis=0)
            heatmap_data_sub_category.loc['Average'] = average_per_question

            # Move the 'Average' row to the top
            heatmap_data_sub_category = pd.concat([heatmap_data_sub_category.loc[['Average']], heatmap_data_sub_category.drop('Average')])

        # Create the heatmap in the appropriate subplot
        sns.heatmap(heatmap_data_sub_category, cmap="RdYlGn", cbar_kws={'label': 'Correct (1.0) or Incorrect (0.0)'}, ax=axes[i])

        # Add labels and title to each subplot
        axes[i].set_title(f'{category} - {sub_category}')
        axes[i].set_xlabel('Question Number')
        axes[i].set_ylabel('Model')

    # Hide any unused axes
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')  # Turn off the axis

    # Adjust layout
    plt.tight_layout()
    plt.show()


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %% [markdown]
# # Appendix: Explanation of the Stderr output of lm-eval
# Step-by-Step Calculation of Standard Error
# 
# 
# 1. **Calculate the Mean (Accuracy)**:
#    - Let's denote the total number of samples as \( n \).
#    - Suppose the model correctly answers \( k \) out of \( n \) samples.
#    - The accuracy (\( \hat{p} \)) is given by:
#      \[
#      \hat{p} = \frac{k}{n}
#      \]
# 
# 2. **Calculate the Standard Deviation (σ)**:
#    - For binary outcomes (correct or incorrect answers), the standard deviation of the accuracy can be derived from the binomial distribution.
#    - The standard deviation (σ) of a binomial distribution is given by:
#      \[
#      \sigma = \sqrt{\hat{p} \cdot (1 - \hat{p})}
#      \]
# 
# 3. **Calculate the Standard Error (SE)**:
#    - The standard error (SE) of the accuracy is the standard deviation of the sampling distribution of the sample mean.
#    - It is calculated by dividing the standard deviation (σ) by the square root of the number of samples (n):
#      \[
#      \text{SE} = \frac{\sigma}{\sqrt{n}} = \frac{\sqrt{\hat{p} \cdot (1 - \hat{p})}}{\sqrt{n}}
#      \]
# 
# ### Example Calculation
# 
# Let's use your provided data:
# - \( \hat{p} \) (accuracy) = 0.1719
# - Standard error (SE) = 0.0094
# - Number of samples (\( n \)) = 1600
# 
# #### Step 1: Calculate the Standard Deviation (σ)
# 
# Using the accuracy value:
# \[
# \sigma = \sqrt{\hat{p} \cdot (1 - \hat{p})}
# \]
# \[
# \sigma = \sqrt{0.1719 \cdot (1 - 0.1719)}
# \]
# \[
# \sigma = \sqrt{0.1719 \cdot 0.8281}
# \]
# \[
# \sigma = \sqrt{0.1423}
# \]
# \[
# \sigma \approx 0.3772
# \]
# 
# #### Step 2: Calculate the Standard Error (SE)
# 
# Using the standard deviation (σ) and the number of samples (\( n \)):
# \[
# \text{SE} = \frac{\sigma}{\sqrt{n}}
# \]
# \[
# \text{SE} = \frac{0.3772}{\sqrt{1600}}
# \]
# \[
# \text{SE} = \frac{0.3772}{40}
# \]
# \[
# \text{SE} \approx 0.0094
# \]
# 
# ### Verification
# 
# The calculated standard error (0.0094) matches the provided standard error, confirming the correctness of the steps.
# 
# ### Summary
# 
# - **Accuracy (Mean)** (\( \hat{p} \)): Proportion of correct answers.
# - **Standard Deviation** (\( \sigma \)): Measures the dispersion of accuracy.
# - **Standard Error** (\( \text{SE} \)): Indicates the precision of the accuracy estimate, derived from the standard deviation and the number of samples.
# 
# The standard error provides an estimate of how much the calculated accuracy might vary if the experiment were repeated multiple times, giving a measure of the reliability of the accuracy metric.
# 

# %% [markdown]
# 


