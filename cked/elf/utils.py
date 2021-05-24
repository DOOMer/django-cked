
import hashlib
import re
import traceback
from pathlib import Path
from typing import List, Optional, Tuple, Union


def crop_tuple(size: Tuple[int, int]) -> Optional[Tuple[int, int, int, int]]:
    """ Return the crop rectangle, as a (left, upper, right, lower)-tuple. """
    width, height = size

    if width > height:  # landscape
        left = int((width - height) / 2)
        upper = 0
        right = left + height
        lower = height
        return left, upper, right, lower
    if height > width:  # portrait
        left = 0
        upper = int((height - width) / 2)
        right = width
        lower = upper + width
        return left, upper, right, lower

    # cube
    return None


def exception_to_string(e: Exception) -> str:
    """ Convert exception to printable string """
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(e.__traceback__)
    pretty_out = traceback.format_list(stack)
    return f"{pretty_out}\n {e.__class__} {e}"


def read_link(path: Path) -> Union[bool, Path]:
    """ Read link and return real path if not broken """
    target = path.readlink()
    if not str(target)[0] == '/':
        target = path.parent.joinpath(target)
    target = target.resolve(strict=False)

    if target.exists():
        if not str(target).find(self._options['root']) == -1:
            return target
    return False


def make_hash(to_hash: str) -> str:
    """ Return a hash of to_hash. """
    new_hash = hashlib.md5()
    new_hash.update(to_hash.encode("utf-8"))
    return str(new_hash.hexdigest())


def make_unique_name(path: Path, copy: str = " copy") -> Path:
    """ Generate unique name for file copied file. """
    cur_dir = path.parent
    cur_name = path.name
    last_dot = cur_name.rfind(".")
    ext = new_name = ""

    if not path.is_dir() and re.search(r"\..{3}\.(gz|bz|bz2)$", cur_name):
        pos = -7
        if cur_name[-1:] == "2":
            pos -= 1
        ext = cur_name[pos:]
        old_name = cur_name[0:pos]
        new_name = old_name + copy
    elif path.is_dir() or last_dot <= 0:
        old_name = cur_name
        new_name = old_name + copy
    else:
        ext = cur_name[last_dot:]
        old_name = cur_name[0:last_dot]
        new_name = old_name + copy

    pos = 0

    if old_name[-len(copy):] == copy:
        new_name = old_name
    elif re.search(r"" + copy + r"\s\d+$", old_name):
        pos = old_name.rfind(copy) + len(copy)
        new_name = old_name[0:pos]
    else:
        # new_path = os.path.join(cur_dir, new_name + ext)
        new_path = cur_dir.joinpath(f"{new_name}{ext}")
        if not new_path.exists():
            return new_path

    # if we are here then copy already exists or making copy of copy
    # we will make new indexed copy *black magic*
    idx = 1
    if pos > 0:
        idx = int(old_name[pos:])
    while True:
        idx += 1
        new_name_ext = new_name + " " + str(idx) + ext
        new_path = Path(cur_dir).joinpath(new_name_ext)
        if not new_path.exists():
            return new_path
        # if idx >= 1000: break # possible loop

