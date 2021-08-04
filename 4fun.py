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
  "date": ISODate("2021-08-03T15:14:27.817Z"),
}
"""

from flask import Flask, render_template, redirect
from flask import request as req
from flask.globals import request
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
    last_indx_doc = counters.find_one_and_update(
        {"coll": "posts"}, {"$inc": {"last_index": 1}}, new=True
    )
    return last_indx_doc["last_index"]


@app.route("/")
def index():
    all_posts = list(posts.find({}))
    posts_by_id = {p["id"]: p for p in all_posts}
    threads = parents_and_children(all_posts)
    return render_template("index.html", threads=threads, posts_by_id=posts_by_id)


@app.route("/new-post", methods=["POST"])
def new_post(**overrides):
    base_post = {
        "title": req.form.get("title", None),
        "content": req.form["content"],
        "tags": [],
        "upvotes": 0,
        "downvotes": 0,
        "reports": 0,
        "parent": None,
        "id": id_for_new_post(),
        "image": None,
        "date": datetime.now(),
    }
    posts.insert_one({**base_post, **overrides})
    return redirect("/")

  
@app.route("/reply/<int:post_id>", methods=["GET", "POST"])
def reply(post_id):
    # reply input page, not submitting yet
    if request.method == "GET":
        post = posts.find_one({"id": post_id})
        title = post["title"] or str(post["id"])
        return render_template("reply.html", post=post, title=title)
    # actual POST submission endpoint
    else:
        return new_post(content=req.form["content"], parent=int(req.form["parent"]))


def parents_and_children(all_posts):
    """
    Given a list of raw posts from the DB, return a dictionary where the keys are thread posts and
    their values are all of the thread replies.

    >>> parents_and_children([
    ...     {'parent': None, "id": 1}, # thread, because parent=null
    ...     {'parent': 1, "id": 2},    # reply, because parent references another post
    ...     {'parent': None, "id": 3},
    ...     {'parent': 1, "id": 4},
    ... ])
    {1: [2, 4], 3: []}
    """
    result = {}
    for post in all_posts:
        if post["parent"] is None:
            result[post["id"]] = []
        else:
            if not result.get(post["parent"], None):
                result[post["parent"]] = []
            result[post["parent"]].append(post["id"])
    return result
  
  
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
<<<<<<< HEAD
    return parsed_lines
=======
    return parsed_lines

def check_reference(line):
    if line[0] == '>':
        if (line[1:len(line)]).isdigit() or (line[1] == ' ' and (line[2:len(line)]).isdigit()):
            return True
    return False       
>>>>>>> parse-text
