from canonical_args.frontend.html import generate

if __name__ == "__main__":
	stuff = {
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

	x = generate.generate_html(stuff)
	with open("templates/test.html", 'w') as f:
		f.write(x)
