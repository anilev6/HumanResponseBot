import json

def clean_words_belong_json(json_filename):
    with open(json_filename, "r", encoding="utf-8") as file:
        original_json = json.load(file)
    simplified_json = {"name": json_filename, "instances": []}

    for instance in original_json:
        simplified_instance = {
            "context": instance["context"],
            "question": instance["question"],
            "answer": instance["answer"],
            "options_list": instance["options_list"],
            "id": instance["id"],
        }
        simplified_json["instances"].append(simplified_instance)

    # Save the simplified JSON to a new file
    simplified_json_filename = f"Clean{json_filename.split('.')[0]}.json"
    with open(simplified_json_filename, 'w', encoding='utf-8') as f:
        json.dump(simplified_json, f, ensure_ascii=False, indent=4)


if __name__=="__main__":
    clean_words_belong_json("ua_cbt_v0_1_clean_humaneval.json")
