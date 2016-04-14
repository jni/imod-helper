import numpy as np
from .geometry import ndline


def model(filename, format='ascii'):
    """Read an IMOD model file into a numpy array.

    Initially only ASCII input files are supported.

    Parameters
    ----------
    filename : string
        The filename to read.
    format : string in {'ascii'}, optional
        Whether the file is binary or ASCII format.

    Returns
    -------
    mod : array of int
        A numpy array of the same size as the minimal bounding box
        containing the model.
    offset : 3-tuple of int
        The top-left corner of the bounding box of the model.
    """
    object_dict = model2coords(filename, format=format)
    offset = np.zeros((3,), dtype=int)
    limits = np.zeros((3,), dtype=int)
    max_object_id = max(object_dict.keys())
    for value in object_dict:
        coords = np.round(object_dict[value]['coords']).astype(int)
        new_offset = np.min(coords, axis=1)
        offset = np.minimum(offset, new_offset, out=offset)
        new_limits = np.max(coords, axis=1)
        limits = np.maximum(limits, new_limits, out=limits)
    mod = np.zeros(limits + 1, dtype=np.min_scalar_type(max_object_id))
    for value in object_dict:
        coords = np.round(object_dict[value]['coords']).astype(int)
        coords -= offset[np.newaxis,]
        mod[tuple(coords)] = value
    return mod, offset


def model2coords(filename, format='ascii'):
    """Read an IMOD model file into a dictionary of objects.

    Initially only ASCII input files are supported.

    Parameters
    ----------
    filename : string
        The filename to read.
    format : string in {'ascii'}, optional
        Whether the file is binary or ASCII format.

    Returns
    -------
    obj_dict : dictionary
        A dictionary containing an element for every object described in
        the mod file. The object IDs are keys, and the values are
        dictionaries of properties, including coordinates ('coords').
    """
    with open(filename, 'r') as fin:
        header = next(fin)
        if not header.startswith('imod'):
            raise ValueError('First line of imod file should be '
                             '"imod (number of objects)".')
        obj = _consume_until_prefix(fin, 'object')


def _consume_until_prefix(file, prefix):
    currline = next(file)
    while not currline.startswith(prefix):
        currline = next(file)
    return currline