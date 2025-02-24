from flask import Flask, request, jsonify

app = Flask(__name__)

# Mapping from text to its decimal representation (as string)
number_map = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10"
}

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input provided", "result": None}), 400
    
    input_val = data.get("input")
    input_type = data.get("inputType")
    output_type = data.get("outputType")
    
    # Check for required keys
    if input_val is None or input_type is None or output_type is None:
        return jsonify({"error": "Missing required parameters", "result": None}), 400
    
    # Supported conversion: text to decimal
    if input_type.lower() == "text" and output_type.lower() == "decimal":
        # Convert input value to lowercase and lookup in our mapping
        result = number_map.get(input_val.lower())
        if result is not None:
            return jsonify({"error": None, "result": result})
        else:
            return jsonify({"error": "Conversion failed", "result": None}), 400
    
    return jsonify({"error": "Unsupported conversion", "result": None}), 400

if __name__ == '__main__':
    app.run(debug=True)
