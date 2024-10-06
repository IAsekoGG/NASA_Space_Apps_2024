import json
import os

from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from flask import request

from mongo_api import get_data

app = Flask(__name__)
load_dotenv()

@app.route('/')
def index():
    mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN')
    return render_template('map.html', mapbox_token=mapbox_token)


@app.route('/get_markers')
def get_markers():
    # db_markers = get_data('location_v4', {})
    db_markers = get_data('location_combined', {})
    markers = []
    
    for marker in db_markers:
        markers.append(
            {"id": marker["_id"], "coordinates": json.loads(marker["_id"]), "icon_url": marker["cluster_title"][0]})
    print(markers)
    return jsonify(markers)

# @app.route('/get_markers')
# def get_markers():
#
#     db_markers = get_data('location_v3', {})
#     markers = []
#
#     for marker in db_markers:
#         markers.append({"id": marker["_id"], "coordinates": json.loads(marker["_id"]), "icon_url": "/static/images/marker1.png"})
#     print(markers)
#     return jsonify(markers)


@app.route('/get_feed/<marker_coords>')
def get_feed(marker_coords):
    problem_id = request.args.get('problemId')
    posts = get_posts_for_problem(problem_id, marker_coords)
    return render_template('feed.html', posts=posts)


import re

import re
import bleach


def parse_and_generate_html(text):
    # Convert bold markdown-like syntax to HTML <b> tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Sanitize the content to only allow <b> tags
    safe_content = sanitize_content(text)
    
    return safe_content


def sanitize_content(content):
    # Only allow <b> tags
    allowed_tags = ['b']
    
    # Clean the content and strip all other tags
    safe_content = bleach.clean(content, tags=allowed_tags, strip=True)
    
    return safe_content


# Функция эмуляции запроса к базе данных
def get_posts_for_problem(problem_id, marker_id):
    posts = get_data("post_combined", {"summary_id": problem_id})
    result = []
    
    for post in posts:
        result.append({
            "title": post["title"],
            "content": parse_and_generate_html(post["text"]),
            "latitude": post["latitude"],
            "longitude": post["longitude"],
            "image": None,
            "source": str(int(post["message_id"]))
        })
    
    return result
    
    # if marker_id == 1:
    #     return [
    #     {
    #         "title": "Пост 1",
    #         "content": "Контент поста 1",
    #         "latitude": 50.5,
    #         "longitude": 30.5,
    #         "image": "https://example.com/image1.jpg",
    #         "source": "http://example.com/source1"
    #     },
    #     {
    #         "title": "Пост 2",
    #         "content": "Контент поста 2",
    #         "latitude": 50.6,
    #         "longitude": 30.7,
    #         "image": None,  # Нет изображения
    #         "source": "http://example.com/source2"
    #     }
    # ]
    # elif marker_id == 2:
    #     return [
    #     {
    #         "title": "Пост 3",
    #         "content": "Контент поста 1",
    #         "latitude": 50.5,
    #         "longitude": 30.5,
    #         "image": "https://lh5.googleusercontent.com/p/AF1QipO0pcZDUME24b0pxlZNGJc4OJARVMDWmDLNh7OE=w408-h306-k-no",
    #         "source": "http://example.com/source1"
    #     },
    #     {
    #         "title": "Пост 4",
    #         "content": "Контент поста 2",
    #         "latitude": 50.2,
    #         "longitude": 30.8,
    #         "image": "/static/images/test.jpg",
    #         "source": "http://example.com/source2"
    #     }
    # ]



# @app.route('/get_feed_problems/<coords>')
# def get_feed_problems(coords):
#     # coords will be a string like '30.4283648,50.4364983'
#     lat, lng = map(float, coords.split(','))
#     # Now you can use lat and lng as needed
#     return f"Coordinates: {lat}, {lng}"

@app.route('/get_feed_problems/<coords>')
def get_feed_problems(coords):
    
    lat, lng = map(float, coords.split(','))
    marker_id = json.dumps([lng, lat])
    
    # lat, lng = map(float, coords.split(','))
    
    # Create a marker ID based on lat and lng if needed (swapping lat, lng here as per your example)
    marker_id = json.dumps([lng, lat])
    
    problems = get_data("post_combined", {"location_id": marker_id})
    
    unic_problems = {}
    
    for problem in problems:
        unic_problems[problem["summary_id"]] = {
            "title": problem["title"],
            "description": problem["summary"],
            "id": problem["summary_id"],
            # "latitude": problem["latitude"],
            # "longitude": problem["longitude"],
            # "image": problem["image"],
            # "source": problem["source"]
        }
    
    problems = list(unic_problems.values())
    
    # problems = [
    #     {"id": 1, "title": "Проблема 1", "description": "Описание проблемы 1"},
    #     {"id": 2, "title": "Проблема 2", "description": "Описание проблемы 2"}
    # ]
    return render_template('feed_problem.html', problems=problems)


if __name__ == '__main__':
    app.run(debug=True)
