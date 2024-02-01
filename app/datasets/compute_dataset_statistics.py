import os


def compute_dataset_statistics(
    slice_name: str,
    dataset_path: str
):
    with open(os.path.join(dataset_path, f"samples.{slice_name}.txt")) as file:
        lines = file.readlines()
    
    samples = set(lines)
    scores = set(line.split("/")[1] for line in lines)

    with open(os.path.join(dataset_path, f"statistics.{slice_name}.yaml"), "w") as file:
        print("samples:", len(samples), file=file)
        print("scores:", len(scores), file=file)
