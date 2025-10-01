sysengbench_osq.csv is the output from the 2.1_converting_mcq_to_osq.ipynb

sysengbench_osq.csv is then filtered to ONLY include the rows that have OSQs. This is rows that are equal to or over the confidence threshold in the notebook.

The output from that filtering is sysengbench_osq_filtered.csv

Then, sysengbench_osq_filtered.csv, is renamed to test.csv so that way it's easy to pull from the HuggingFace repository.

The repository this new dataset is kept in is:

https://huggingface.co/datasets/rabell/SysEngBench-OSQ