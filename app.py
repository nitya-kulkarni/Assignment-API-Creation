from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId


app = Flask(__name__)


app.config["MONGO_URI"] = "mongodb://localhost:27017/mentor_db"  # Localhost MongoDB URI
mongo = PyMongo(app)
db = mongo.db


@app.route('/')
def home():
    return "Welcome to the Mentor Marketplace API!", 200

@app.route('/mentors', methods=['POST'])
def register_mentor():
    name = request.form.get('name')
    expertise = request.form.get('expertise')
    location = request.form.get('location')
    availability = request.form.getlist('availability')  # Accept multiple availability values

    if not name or not expertise or not location:
        return jsonify({"error": "Name, expertise, and location are required"}), 400

    mentor = {
        "name": name,
        "expertise": expertise,
        "location": location,
        "availability": availability  # Optional
    }
    result = db.mentors.insert_one(mentor)
    return jsonify({"message": "Mentor registered successfully", "id": str(result.inserted_id)}), 201


@app.route('/mentors/search', methods=['POST'])
def search_mentors():
    expertise = request.form.get('expertise')
    location = request.form.get('location')

    query = {}
    if expertise:
        query["expertise"] = expertise
    if location:
        query["location"] = location

    mentors = db.mentors.find(query)
    return dumps(mentors), 200


@app.route('/mentors/availability', methods=['POST'])
def get_mentor_availability():
    mentor_id = request.form.get('mentor_id')
    if not mentor_id:
        return jsonify({"error": "Mentor ID is required"}), 400

    try:
        mentor = db.mentors.find_one({"_id": ObjectId(mentor_id)})
        if not mentor:
            return jsonify({"error": "Mentor not found"}), 404

        return jsonify({"availability": mentor.get("availability", [])}), 200
    except Exception as e:
        return jsonify({"error": f"Invalid Mentor ID. Details: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(debug=True)
