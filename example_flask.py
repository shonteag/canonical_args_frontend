from flask import Flask, request, render_template
from pprint import pformat
app = Flask(__name__)

from canonical_args.frontend.html import generate, format
from canonical_args import structure

# from canonical_args.frontend.html import format
from pprint import pformat
import json


argspec = {
	"args": [
		{
			"name": "arg1",
			"type": "one([int, float, str, dict])",
			"values": {
				"int": ">=0",
				"float": "<=0",
				"str": ["A", "B", "C"],
				"dict": {
					"subkey1": {
						"type": "one([int, float])",
						"values": {
							"int": ">0",
							"float": "<=0"
						}
					}
				}
			}
		},
		{
			"name": "arg2",
			"type": "dict",
			"values": {
				"subkey1": {
					"type": "one([int, float, dict])",
					"values": {
						"int": None,
						"float": None,
						"dict": {
							"subsub1": {
								"type": int,
								"values": None
							}
						}
					}
				},
				"subkey2": {
					"type": float,
					"values": None
				}
			}
		}
	],
	"kwargs": {
		"kwarg1": {
			"type": "dict",
			"values": None
		}
	}
}
@app.route("/", methods=["POST", "GET"])
def index():
	if request.method == "GET":
		return generate.generate_html(argspec)
	elif request.method == "POST":
		flatdict = dict(request.form)

		print flatdict

		try:
			reconstdict = format.reform_from_html(argspec, flatdict)
			structure.checkspec(argspec,
								reconstdict["args"],
								reconstdict["kwargs"])
		except Exception as e:
			raise
			return str(e)

		return json.dumps(reconstdict, sort_keys=True)


if __name__ == "__main__":
	app.run()