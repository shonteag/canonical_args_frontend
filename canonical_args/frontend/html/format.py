"""
Provide utils for reformatting from data from HTML frontend
into usable, nested dict of method arguments.
"""
from __future__ import absolute_import

from canonical_args import check
import re
from pprint import pprint


permitted_types = ["int",
                   "float",
                   "double",
                   "long",
                   "str",
                   "bool"]

def cast(valstring, typestring, name=None):
    """
    Perform a cast on ``valstring`` to type ``typestring``.
    First, have to ``eval`` the ``typestring``, provided it
    is a permitted type (security reasons).
    :param str valstring: the stringified value
    :param str typestring: the stringified type (eg. ``"int"``)
    :param str name: optional, if specified, any errors raised
        are more detailed.
    :raises ValueError: if ``valstring`` cannot be cast to
        requested type
    :raises TypeError: if ``typestring`` is not a permitted type.
    :returns: the ``valstring`` cast to the type of ``typestring``.
    """
    if typestring not in permitted_types:
        raise TypeError('{} is not a permitted type'.format(typestring))

    try:
        return eval(typestring)(valstring)
    except ValueError, e:
        err = "`{}` is invalid for type '{}'".format(valstring, typestring)
        if name:
            err += " for arg '{}'".format(name)
        raise ValueError(err)

def reform_from_html(spec, form, delimeter="-"):

    def recurse(level, name, types, values, delimeter="-"):
        """
        Recurse through a flattened ``form`` dictionary, reconstructing
        dictionary to match structure specified by ``spec``.
        :param dict spec: the canonical_args argspec dict
        :param dict form: the flat HTML form data
        :param str delimeter: default ``"-"``, the string character used
            to separate levels in the ``form.keys()`` entries.
        :returns: ``dict``, the reconstructed, type correct argument
            dictionary, matching the ``spec`` structure.
        """
        subtype = check.eval_subtype(types)

        # choice of one
        if isinstance(subtype, check.ChoiceOfOne):
            names = None

            for index, subsubtype in enumerate(subtype):
                try:
                    names = recurse(level+1,
                                    name,
                                    subsubtype,
                                    values[check.type_to_string(subsubtype)])
                except KeyError:
                    # this subkey doesn't exist, so it must
                    # be of a different type
                    pass
                    # Yes, you read that correctly, we pass here.
                    # But it's ok! If we can't find a valid type
                    # in the loop, we raise a KeyError below.
                else:
                    break

            if names is None:
                # we couldnt find a valid entry
                # See? Told you we re-raise the key error.
                raise KeyError("could not find valid entry for '{}'".format(
                    name))

            return names

        # structlist
        elif isinstance(subtype, list) and isinstance(values, list):
            names = []
            for index, subsubtype in enumerate(subtype):
                names.append(recurse(level+1,
                                     name+"[{}]".format(index),
                                     subtype[index],
                                     values[index]))
            return names

        # structdict
        elif subtype == dict and isinstance(values, dict):
            names = {}
            for kw in sorted(values):
                arg = values[kw]
                names[kw] = recurse(level+1,
                                    name+delimeter+kw,
                                    arg["type"],
                                    arg["values"],
                                    delimeter=delimeter)
            return names

        # unstructlist
        elif subtype == list and values is None:
            # find all keys matching (other than index)
            pattern = re.compile('{}\[(.*)\]'.format(name))
            matchingkeys = [key for key in form.keys()\
                            if pattern.match(key)]

            construct = []
            for subkey in sorted(matchingkeys):
                index = int(re.findall('\[(.*)\]', subkey)[0])
                raw = form[subkey]
                construct.append(cast(raw[0], raw[1], name=name))
            return construct
            # construct list of values ordered by index in key

        # unstructdict
        elif subtype == dict and values is None:
            pattern = re.compile('{}\[(.*)\]'.format(name))
            matchingkeys = [key for key in form.keys()\
                            if pattern.match(key)]

            construct = {}
            for subkey in matchingkeys:
                raw = form[subkey]
                construct[str(raw[0])] = cast(raw[1], raw[2], name=name)
            return construct

        # native
        else:
            raw = form[name]
            return cast(raw[0], raw[1], name=name)

    names = {
        "args": [],
        "kwargs": {}
    }
    for index, arg in enumerate(spec["args"]):
        names["args"].append(recurse(0,
                                     arg["name"],
                                     arg["type"],
                                     arg["values"],
                                     delimeter=delimeter))

    for kw, arg in spec["kwargs"].items():
        names["kwargs"][kw] = recurse(0,
                                      kw,
                                      arg["type"],
                                      arg["values"],
                                      delimeter=delimeter)

    return names
