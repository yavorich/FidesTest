def get_lines_data(path, separator):
    with open(path, "r") as f:
        lines = f.read().splitlines()
    ids = [l.split(separator)[0] for l in lines]
    weights = [l.split(separator)[-1] for l in lines]
    data = {i: w for i, w in zip(ids, weights)}
    return data

def compare_results(base_file, compare_file, separator="¬~"):
    old_data = get_lines_data(base_file, separator)
    new_data = get_lines_data(compare_file, separator)
    
    diff_log = ""
    for _id in old_data.keys():
        diff_log += _id
        if _id in new_data.keys():
            diff_log += " - EXIST"
            old_weight, new_weight = old_data[_id], new_data[_id]
            if new_weight == old_weight:
                diff_log += f" ({new_weight} = {old_weight})\n"
            elif new_weight > old_weight:
                diff_log += f" ({new_weight} > {old_weight}) - NOT EQUAL\n"
            else:
                diff_log += f" ({new_weight} < {old_weight}) - NOT EQUAL\n"
        else:
            diff_log += " - MISS\n"
        
    for _id in new_data.keys():
        if _id not in old_data.keys():
            diff_log += _id + " - EXTRA\n"
    with open("diff.txt", "w") as f:
        f.write(diff_log)

if __name__ == "__main__":
    compare_results("out_new.txt", "out_old.txt")