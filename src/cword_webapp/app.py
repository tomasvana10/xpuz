from multiprocessing import Process 
from flask import Flask, render_template

app = Flask(__name__)

def run(*args, **data):
    @app.route("/")
    def main():
        return render_template(
            "index.html",
            colour_palette=data["colour_palette"],
            cword_data=data["cword_data"],
            empty=data["empty"],
            name=data["name"],
            word_count=data["word_count"],
            failed_insertions=data["failed_insertions"],
            dimensions=data["dimensions"],
            starting_word_positions=data["starting_word_positions"],
            starting_word_matrix=data["starting_word_matrix"],
            grid=data["grid"],
            definitions_a=data["definitions_a"],
            definitions_d=data["definitions_d"],
        )
        
    app.run(debug=False, port=int(data["port"]))

def init_webapp(**data):
    global server
    server = Process(target=run, kwargs=data)
    server.start()

def terminate_app():
    server.terminate()
    server.join()
