'''Flask web app to produce an interactive interface to complete a crossword. The app is run when the
user presses the "Load crossword" button in the main GUI.
'''

from multiprocessing import Process 

from flask import Flask, render_template

app = Flask(__name__)

def _run(*args, **data):
    '''Ran as a new Process using the `multiprocessing` module. kwargs are forwarded from
    `_create_app_process`, which forwards the arguments from `init_webapp` in `main.py`.
    '''
    @app.route("/")
    def main():
        return render_template(
            "index.html",
            colour_palette=data["colour_palette"],
            json_colour_palette=data["json_colour_palette"],
            cword_data=data["cword_data"],
            empty=data["empty"],
            name=data["name"],
            intersections=data["intersections"],
            word_count=data["word_count"],
            failed_insertions=data["failed_insertions"],
            dimensions=data["dimensions"],
            starting_word_positions=data["starting_word_positions"],
            starting_word_matrix=data["starting_word_matrix"],
            grid=data["grid"],
            definitions_a=data["definitions_a"],
            definitions_d=data["definitions_d"],
        )
        
    app.run(debug=False, port=int(data["port"])) # NOTE: debug mode does not work when running the app
                                                 # as a process with the multiprocessing module   

def _create_app_process(**data):
    global server
    server = Process(target=_run, kwargs=data)
    server.start()

def terminate_app():
    server.terminate()
    server.join()
