"""
Provide frontend HTML/Javascript/CSS generation for an
argspec.
"""
from __future__ import absolute_import

from jinja2 import Environment, PackageLoader, select_autoescape
from canonical_args import check



env = Environment(
	loader=PackageLoader('canonical_args.frontend.html', 'templates'),
	autoescape=select_autoescape(['html', 'xml'])
)
env.globals.update(zip=zip)

custom_env = None

def generate_html(spec,
				  delimeter="-",
				  action="",
				  method="POST",
				  include_styling=True):
	"""
	Recurse through ``spec`` dict, generating HTML components for
	argspec entries.

	:param dict spec: the canonical_args argspec dict
	:param str delimeter: default ``"-"``, the string character used
		to separate levels in the HTML input ``"name"`` attributes.
	:param str action: default ``""``, the html ``<form>`` "action"
		attribute
	:param str method: default ``"POST"`` the html ``<form>`` "method"
		attribute
	:param bool include_styling: default True, include html ``<style>``
		tags.
	:returns: str, the fully rendered HTML to display on the front end.
	"""

	def recurse(level, name, types, values, delimeter=delimeter):
		subtype = check.eval_subtype(types)
		
		# choice of one
		if isinstance(subtype, check.ChoiceOfOne):
			entries = []
			for index, subsubtype in enumerate(subtype):
				entries.append(recurse(level+1,
									   name,
									   subtype[index],
									   values[check.type_to_string(subsubtype)]
									   ))

			template = env.get_template("one_selector.html")
			html = template.render(name=name,
								   options=[check.type_to_string(x)\
								   			for x in subtype],
								   entries=entries)
			
			if level > 0:
				template = env.get_template("level.html")
				html = template.render(name=name.split(delimeter)[-1],
									   include_header=True,
									   inner=html)
			return html			


		# structlist
		elif isinstance(subtype, list) and isinstance(values, list):
			# recurse
			html = ""
			for index, subsubtype in enumerate(subtype):
				html += recurse(level+1,
								name+"["+str(index)+"]",
								subtype[index],
								values[index])

			if level > 0:
				template = env.get_template("level.html")
				html = template.render(name=name.split(delimeter)[-1],
									   include_header=True,
									   inner=html)
			return html

		# structdict
		elif subtype == dict and isinstance(values, dict):
			html = ""
			for kw in sorted(values):
				arg = values[kw]
				html += recurse(level+1,
								name+delimeter+kw,
								arg["type"],
								arg["values"])

			if level > 0:
				template = env.get_template("level.html")
				html = template.render(name=name.split(delimeter)[-1],
									   include_header=True,
									   inner=html)
			return html

		# unstructlist
		elif subtype == list and values is None:
			template = env.get_template("base.html")
			html = template.render(name=name,
								   displayname=name.split(delimeter)[-1],
								   type=check.type_to_string(subtype),
								   inputtype="unstructlist")

			if level > 0:
				template = env.get_template("level.html")
				html = template.render(name=name.split(delimeter)[-1],
									   include_header=True,
									   inner=html)
			return html


		# unstructdict
		elif subtype == dict and values is None:
			template = env.get_template("base.html")
			html = template.render(name=name,
								   displayname=name.split(delimeter)[-1],
								   type=check.type_to_string(subtype),
								   inputtype="unstructdict")

			if level > 0:
				template = env.get_template("level.html")
				html = template.render(name=name.split(delimeter)[-1],
									   include_header=True,
									   inner=html)
			return html

		# selector
		elif isinstance(values, list):
			template = env.get_template("base.html")
			return template.render(name=name,
								   displayname=name.split(delimeter)[-1],
								   type=check.type_to_string(subtype),
								   options=values,
								   inputtype="selector")

		# native
		else:
			print "!!!!", name, subtype
			# name, type, inputtype
			template = env.get_template("base.html")
			return template.render(name=name,
								   displayname=name.split(delimeter)[-1],
								   type=check.type_to_string(subtype),
								   constraint=values,
								   inputtype="native")

	html = ""
	for index, arg in enumerate(spec["args"]):
		subhtml = recurse(0,
						  arg["name"],
						  arg["type"],
						  arg["values"])
		# level template
		template = env.get_template("level.html")
		html += template.render(name=arg["name"],
								include_header=True,
								inner=subhtml)

	for kw, arg in spec["kwargs"].items():
		subhtml = recurse(0,
						  kw,
						  arg["type"],
						  arg["values"])
		# level template
		template = env.get_template("level.html")
		html += template.render(name=kw,
								include_header=True,
								inner=subhtml)

	# top template
	template = env.get_template("form.html")
	html = template.render(inner=html, action=action, method=method)

	if include_styling:
		template = env.get_template("styling.html")
		html = template.render(inner=html)

	return html
