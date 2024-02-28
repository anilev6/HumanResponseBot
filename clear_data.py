import json

def clean_words_belong_json(json_filename):
    with open(json_filename, "r", encoding="utf-8") as file:
        original_json = json.load(file)
    simplified_json = {"name": json_filename, "instances": []}

    for instance in original_json:
        simplified_instance = {
            "index": instance["index"],
            "old_index": instance["old_index"],
            "ukr_text": instance["ukr_text"],
            "ukr_title": instance["ukr_title"],
            "similar_titles_unmasked": eval(instance["similar_titles_unmasked"]),
        }
        simplified_json["instances"].append(simplified_instance)

    # Save the simplified JSON to a new file
    simplified_json_filename = f"Clean{json_filename.split('.')[0]}.json"
    with open(simplified_json_filename, 'w', encoding='utf-8') as f:
        json.dump(simplified_json, f, ensure_ascii=False, indent=4)


if __name__=="__main__":
    clean_words_belong_json("Up_titles.json")
