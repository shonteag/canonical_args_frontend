"""
Provide a register/lookup interface for ``cls`` type
arguments.  When called by a frontend generator, a ``cls``
type registered to the sources module will pull a list of
available instantiated objects via a configurable method.
"""
from __future__ import absolute_import

import types
from canonical_args import check


SOURCES = {}


def register(import_string,
			 cls_name,
			 cls_display_name,
			 display_name_format,
			 get_all,
			 get_one):
	"""
	register a class type to the sources, along with how to retrieve
	available instances, and how to identify specific instances of the
	class.

	:param str import_string: the import string of the 'cls()' type
	:param str cls_name: the class attribute holding the primary identifier
	:param cls_display_name: the class attribute holding the humanized
		identifier
	:param str display_name_format: the python format string indicating
		how display names should be formatted.

			cls_display_name = ["name", "version"]
			display_name_format = "{name} ({version})"

	:type cls_display_name: ``str`` or ``list``
	:param callable get_all: a method for getting all available cls objects
	:param callable get_one: a method which takes the primary identifier
		``cls_name`` and returns the correct instance
	"""
	if isinstance(import_string, types.TypeType):
		import_string = check.type_to_string(import_string)

	SOURCES[import_string] = {
		"cls_name": cls_name,
		"cls_display_name": cls_display_name,
		"display_name_format": display_name_format,
		"get_all": get_all,
		"get_one": get_one
	}

def _make_display_name(obj):
	"""
	make human readable display names from a list of attrs
	"""
	import_string = check.type_to_string(type(obj))
	formatstring = SOURCES[import_string]["display_name_format"]
	formatdict = {}
	formatattrs = SOURCES[import_string]["cls_display_name"]
	if not isinstance(formatattrs, list):
		formatattrs = list([formatattrs, ])
	for attr in formatattrs:
		formatdict[attr] = getattr(obj, attr)
	return formatstring.format(**formatdict)

def get_all(import_string, raw=False):
	"""
	get all instantiated options for a cls arg of type
	``import_string``.

	:param import_string: the import path of the object
	:type import_string: ``str`` or ``types.TypeType``
	:param bool raw: default False, return the objects
		themselves
	:returns: if ``raw``, returns ``list`` of objects.
		else, returns ``tuple`` of two ``list``s: the
		primary indentifiers for the objects, and the
		dispaly names for the objects.
	"""
	if isinstance(import_string, types.TypeType):
		import_string = check.type_to_string(import_string)
	objs = SOURCES[import_string]["get_all"]()
	
	if raw:
		return objs

	# return ids and names
	return [getattr(obj, SOURCES[import_string]["cls_name"]) for obj in objs],\
		   [_make_display_name(obj) for obj in objs]

def get_one(import_string, primary_identifier, raw=False):
	"""

	"""
	if isinstance(import_string, types.TypeType):
		import_string = check.type_to_string(import_string)
	obj = SOURCES[import_string]["get_one"](primary_identifier)

	if raw:
		return obj

	return getattr(obj, SOURCES[import_string]["cls_name"]),\
		   _make_display_name(obj)

