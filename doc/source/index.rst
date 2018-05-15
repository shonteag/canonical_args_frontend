canonical\_args\_frontend
=========================

``canonical_args_frontend`` is a namespace sub-package of ``canonical_args``, designed to dynamically generate frontend UI components according to ``canonical_args`` "argspec" dictionaries. ::

	from canonical_args.frontend.html import generate, format
	from canonical_args import structure

	argspec = {
		"args": [
			{
				"name": "arg1",
				"type": "int",
				"values": ">0"
			},
			{
				"name": "arg2",
				"type": "one([int, float, NoneType, list([int, int])])",
				"values": {
					"int": "!=0",
					"float": "range(0, 1)",
					"NoneType": None,
					"list": [
						"range(0, 100)",
						">=0"
					]
				}
			}
		]
	}

	frontend_html = generate.generate_html(argspec)

	# display that to the front end
	...
	# get the form data back from the frontend
	...

	# reform the form data to match the argspec
	reformed = format.reform_from_html(argspec, formdata)

	# now check the reformed data
	try:
		structure.checkargs(argspec, reformed["args"], reformed["kwargs"])
	except (AssertionError, TypeError, ValueError), e:
		# raise an error, show the user an error box at the frontend?
		...
	else:
		# successfully validated user input against argspec
		# so now, do something with it, like call the intended method!
		...

Using the above methodology, we can easily integrate with Flask, Django, or any other python web package.

.. toctree::
   :maxdepth: 4

   modules