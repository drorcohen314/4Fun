"""
Example post representation in the database:

{
  "title": "Based Post",
  "content": "allo",
  "tags": [
    "based",
    "entrepreneur"
  ],
  "upvotes": 0,
  "downvotes": 0,
  "reports": 0,
  "id": 123245123124,
  "parent": 85718975819651, // null if the post is a thread
  "image": null,
  date: ISODate("2021-08-03T15:14:27.817Z"),
}
"""

from flask import Flask, render_template, redirect
from flask import request as req
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongoclient = MongoClient()
db = mongoclient["4fun"]
posts = db["posts"]
counters = db["counters"]

if counters.estimated_document_count() == 0:
    counters.insert_one({"coll": "posts", "last_index": 0})


def id_for_new_post():
    """
    Get a new unused ID for a post. IDs are auto incremented
    """
    last_indx_doc = counters.find_one_and_update({"coll": "posts"},
                                                 {"$inc": {"last_index": 1}},
                                                 new=True)
    return last_indx_doc["last_index"]


@app.route("/")
def index():
    return render_template("index.html", posts=posts.find({}))


@app.route("/new-post", methods=["POST"])
def new_post():
    posts.insert_one({
        "title": req.form["title"],
        "content": req.form["content"],
        "tags": [],
        "upvotes": 0,
        "downvotes": 0,
        "reports": 0,
        "id": id_for_new_post(),
        "image": None,
        "date": datetime.now()
    })
    return redirect("/")

def parse_content(lines):
    parsed_lines = []
    for line in lines:
        line_content = line
        text_type = "plain"
        reference_post_id = None
        
        if line[0] == '>':
            if line[1] == '>' and (line[2:len(line)]).isdigit():
                text_type = "reference"
                reference_post_id = line[2:len(line)]
            else:
                text_type = "greentext"
        
        # insert paresd line
        parsed_lines.append({
                            "line_content":line_content,
                            "type":text_type,
                            "reference_post_id":reference_post_id
                            })
    return parsed_lines

def check_reference(line):
    if line[0] == '>':
        if (line[1:len(line)]).isdigit() or (line[1] == ' ' and (line[2:len(line)]).isdigit()):
            return True
    return False       