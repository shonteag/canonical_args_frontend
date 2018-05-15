"""
Provide utils for reformatting from data from HTML frontend
into usable, nested dict of method arguments.
"""
from __future__ import absolute_import

from canonical_args import check
import re
import warnings


permitted_types = ["int",
                   "float",
                   "double",
                   "long",
                   "str",
                   "bool"]

class NotSpecified(object):
    pass

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
    valstring = str(valstring)
    typestring = str(typestring)

    if typestring == "NoneType":
        return None
    elif valstring == "":
        # argument was left blank
        return NotSpecified
    else:
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
            entry = NotSpecified

            for index, subsubtype in enumerate(subtype):
                try:
                    entry = recurse(level+1,
                                    name,
                                    subsubtype,
                                    values[check.type_to_string(subsubtype)])
                except KeyError as e:
                    pass
                else:
                    break

            if entry is NotSpecified:
                # we couldnt find a valid entry
                # See? Told you we re-raise the key error.
                warnings.warn(
                    "could not find valid entry for '{}'".format(name),
                    RuntimeWarning)

            return entry

        # structlist
        elif isinstance(subtype, list) and isinstance(values, list):
            entry = []
            for index, subsubtype in enumerate(subtype):
                ret = recurse(level+1,
                              name+"[{}]".format(index),
                              subtype[index],
                              values[index])

                if ret is not NotSpecified:
                    # do not append an unspecified value
                    entry.append(ret)
                else:
                    # because this is a structured list, the positional
                    # argument is guaranteed. an unspecified value must
                    # therefore be None.
                    entry.append(None)
            return entry

        # structdict
        elif subtype == dict and isinstance(values, dict):
            entry = {}
            for kw in sorted(values):
                arg = values[kw]
                ret = recurse(level+1,
                              name+delimeter+kw,
                              arg["type"],
                              arg["values"],
                              delimeter=delimeter)
                if ret is not NotSpecified:
                    # do not set an unspecified value
                    entry[kw] = ret
                else:
                    # this is a Structured Dict, so we have to guarantee
                    # the presence of all keys. Thusly, set None when a
                    # value is unspecified.
                    entry[kw] = None
            return entry

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
                ret = cast(raw[0], raw[1], name=name)
                if ret is not NotSpecified:
                    # ensure not to appaned a NotSpecified value
                    construct.append(ret)
                # this is an unstructured list, so if a value is
                # unspecified, ignore the shit out of it.
            if len(construct) > 0:
                return construct
            else:
                return NotSpecified

        # unstructdict
        elif subtype == dict and values is None:
            pattern = re.compile('{}\[(.*)\]'.format(name))
            matchingkeys = [key for key in form.keys()\
                            if pattern.match(key)]

            construct = {}
            for subkey in matchingkeys:
                raw = form[subkey]
                if str(raw[0]) != '':
                    # ensure there is a valid key
                    ret = cast(raw[1], raw[2], name=name)
                    if ret != NotSpecified:
                        # ensure there is a valid value
                        construct[str(raw[0])] = ret
                    # this is an unstructured dict, so keys are not
                    # guaranteed here. If a value is unspecified,
                    # simply don't append it (aka, ignore it).
            if len(construct) > 0:
                return construct
            else:
                return NotSpecified

        # native
        else:
            raw = form[name]
            ret = cast(raw[0], raw[1], name=name)
            return ret

    names = {
        "args": [],
        "kwargs": {}
    }
    for index, arg in enumerate(spec["args"]):
        ret = recurse(0,
                      arg["name"],
                      arg["type"],
                      arg["values"],
                      delimeter=delimeter)
        if ret != NotSpecified:
            names["args"].append(ret)
        else:
            names["args"].append(None)

    for kw, arg in spec["kwargs"].items():
        ret = recurse(0,
                      kw,
                      arg["type"],
                      arg["values"],
                      delimeter=delimeter)
        print "  ", kw, ret
        if ret != NotSpecified:
            names["kwargs"][kw] = ret

    return names
