import json

data = json.load(open("./bot/data/training/training_data.json"))
formatted_data = []

for item in data:
    # split the input text into lines
    lines = item["input"].split("\n")

    # extract the prompt from the second line
    prompt = lines[2:]
    prmpt = ""
    for line in prompt:
        if line.startswith(" "):
            line = line[1:]
        if line.startswith("User1:"):
            line = line[7:]
        if line.startswith("User2:"):
            line = line[7:]
        if line.startswith("[EOS]"):
            line = line[6:]
        line.strip()
        prmpt += line + "\n"
    while prmpt.find("\n\n") != -1:
        prmpt = prmpt.replace("\n\n", "\n")
    if prmpt.endswith("\n"):
        prmpt = prmpt[:-1]
    # replace all \n  with [EOS]\n and add [EOS] to the endS
    prmpt = prmpt.replace("\n", "[EOS]\n")
    prmpt += "[EOS]"
    # create a new dictionary with the formatted data
    formatted_item = {"prompt": prmpt, "response": item["output"] + "[EOS]"}

    formatted_data.append(formatted_item)

# convert the formatted data to JSON and print it
print(json.dumps(formatted_data, indent=2))

# replace the old training data with the new training data
with open("./bot/data/training/training_data.json", "w") as f:
    json.dump(formatted_data, f, indent=2)
    f.close()
