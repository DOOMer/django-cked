
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union, Tuple, Optional
from urllib.parse import quote, urljoin
import mimetypes
import os
import shutil
import time
import traceback

from .const import *
from .utils import crop_tuple, exception_to_string, make_hash, make_unique_name, read_link


class Connector:
    _options = {

        'URL': '',
        'archiveMimes': {},
        'archivers': {
            'create': {},
            'extract': {}
        },
        'defaults': {
            'read': True,
            'write': True,
            'rm': True
        },
        'disabled': [],
        'debug': False,
        'dotFiles': False,
        'dirSize': True,
        'fileURL': True,
        'imgLib': 'auto',
        'perms': {},
        'root': '',
        'rootAlias': 'Home',
        'tmbAtOnce': 5,
        'tmbDir': '.tmb',
        'tmbSize': 48,
        'uploadMaxSize': 256,
        'uploadWriteChunk': 8192,
        'uploadAllow': [],
        'uploadDeny': [],
        'uploadOrder': ['deny', 'allow'],
    }

    _commands = {
        'open': '_cmd_open',
        'rename': '_cmd_rename',
        'mkdir': '_cmd_mkdir',
        'mkfile': '_cmd_mkfile',
        'rm': '_cmd_rm',
        'paste': '_cmd_paste',
        'upload': '_cmd_upload',
        'duplicate': '_cmd_duplicate',
        'resize': '_cmd_resize',
        'tmb': '_cmd_thumbnails',
        'read': '_cmd_read',
        'edit': '_cmd_edit',
        'ping': '_cmd_ping',
    }

    _mimeType_list = {
        # text
        'txt': 'text/plain',
        'conf': 'text/plain',
        'ini': 'text/plain',
        'php': 'text/x-php',
        'html': 'text/html',
        'htm': 'text/html',
        'js': 'text/javascript',
        'css': 'text/css',
        'rtf': 'text/rtf',
        'rtfd': 'text/rtfd',
        'py': 'text/x-python',
        'java': 'text/x-java-source',
        'rb': 'text/x-ruby',
        'sh': 'text/x-shellscript',
        'pl': 'text/x-perl',
        'sql': 'text/x-sql',
        # apps
        'doc': 'application/msword',
        'ogg': 'application/ogg',
        '7z': 'application/x-7z-compressed',
        # video
        'ogm': 'appllication/ogm',
        'mkv': 'video/x-matroska'
    }

    _file_options = {
        'fileMode': 0o644,
        'dirMode': 0o755,
    }

    http_allowed_params = (
        API_CMD, API_CONTENT, API_CURRENT, API_CUT,  API_DEST, API_INIT, API_HEIGHT, API_NAME, API_SRC, API_TARGET,
        API_TARGETS, API_TREE, API_TYPE, API_UPLOAD, API_WIDTH,
    )
    http_status_code = 0
    http_header = {}
    http_response = None

    _time = 0
    _request: Dict = {}
    _response = {
        RSP_DEBUG: {},
    }
    _error_data: Dict = {}
    _form = {}
    _im = None
    _sp = None
    _today = 0
    _yesterday = 0

    def __init__(self, opts: dict) -> None:
        for option, value in opts.items():
            self._options[option] = value

        # print(self._options)
        self._options['URL'] = self._check_utf8(self._options['URL']).rstrip('/')
        self._options['root'] = self._check_utf8(self._options['root'])
        self._debug('URL', self._options['URL'])
        self._debug('root', self._options['root'])

        for cmd in self._options['disabled']:
            if cmd in self._commands:
                del self._commands[cmd]

        if self._options['tmbDir']:
            self._options['tmbDir'] = Path(self._options['root']).joinpath(self._options['tmbDir'])
            tmp_path = Path(self._options['tmbDir'])
            try:
                if not tmp_path.exists():
                    tmp_path.mkdir()
                self._options['tmbDir'] = tmp_path
            except PermissionError:
                self._options['tmbDir'] = False
                self._debug("thumbnail", f"Permission denied: {tmp_path}")
                print(f"WARNING: failed to create thumbnail folder at {tmp_path}, "
                      f"due to permission denied, it will be disabled.")

    def __reset(self):
        """ Flush per request variables """
        # self.httpStatusCode = 0
        # self.httpHeader = {}
        # self.httpResponse = None
        self._request: Dict = {}
        self._response: Dict = {}
        self._errorData = {}
        self._form = {}

        self._time = time.time()
        t = datetime.fromtimestamp(self._time)
        self._today = time.mktime(datetime(t.year, t.month, t.day).timetuple())
        self._yesterday = self._today - 86400

        self._response['debug'] = {}

    def run(self, http_request: Dict[str, Any]) -> tuple[int, dict, str]:
        """ Run main function. """
        self.__reset()
        time_start = time.time()
        root_ok = True
        if not Path(self._options['root']).exists() or self._options['root'] == "":
            root_ok = False
            self._response[RSP_ERROR] = "Invalid backend configuration"
        elif not self._is_allowed(Path(self._options['root']), ACCESS_READ):
            root_ok = False
            self._response['error'] = f"Access denied to {self._options['root']}"

        for field in self.http_allowed_params:
            if field in http_request:
                self._request[field] = http_request[field]

        if root_ok:
            if API_CMD in self._request:
                if self._request[API_CMD] in self._commands:
                    cmd = self._request[API_CMD]

                    # A missing command method should blow up here.
                    c_attr = self._commands[cmd]
                    call_func = getattr(self, c_attr)

                    try:
                        call_func()
                    except Exception as exc:  # pylint: disable=broad-except
                        # self._response[RSP_ERROR] = f"Command Failed: {self._response[API_CMD]}, Error: \n{exc}"
                        traceback.print_exc()
                        self._debug('exception', exception_to_string(exc))

                else:
                    self._response[RSP_ERROR] = f"Unknown command"

            else:
                self._cmd_open()

            if API_INIT in self._request:
                # self.check arch
                self._response['disabled'] = self._options['disabled']
                if not self._options['fileURL']:
                    url = ''
                else:
                    url = self._options['URL']

                self._response['params'] = {
                    'dotFiles': self._options['dotFiles'],
                    'uplMaxSize': str(self._options['uploadMaxSize']) + 'M',
                    # 'archives': list(self._options['archivers']['create'].keys()),
                    # 'extract': list(self._options['archivers']['extract'].keys()),
                    'url': url
                }

        if self._error_data:
            self._debug("error_data", self._error_data)

        if self._options['debug']:
            self._debug('time', time.time() - self._time)
        else:
            if RSP_DEBUG in self._response:
                self._response[RSP_ERROR] = None

        if self.http_status_code < 100:
            self.http_status_code = 200

        if 'Content-type' not in self.http_header:
            if API_CMD in self._request and self._request[API_CMD] == API_UPLOAD:
                self.http_header['Content-type'] = "text/html"
            else:
                self.http_header['Content-type'] = "application/json"

        return self.http_status_code, self.http_header, self._response

    def _cmd_open(self):
        """ Open file or directory. """
        if 'current' in self._request:
            cur_dir = self._find_dir('current', None)
            cur_file = self._find(self._request['target'], cur_dir)

            if not cur_dir or not cur_file or Path(cur_file).is_dir():
                self.http_status_code = HTTP_NOT_FOUND
                self.http_header['Content-type'] = 'text/html'
                self._response = "File not found"
                return

            if not self._is_allowed(cur_dir, ACCESS_READ) or not self._is_allowed(cur_file, ACCESS_READ):
                self.http_status_code = HTTP_FORBIDDEN
                self.http_header['Content-type'] = 'text/html'
                self._response = "File not found"
                return

            if Path(cur_file).is_symlink():
                # cur_file = read_link(cur_file)
                cur_file = Path(read_link(cur_file))

                if not cur_file or cur_file.is_dir():
                    self.http_status_code = HTTP_NOT_FOUND
                    self.http_header['Content-type'] = 'text/html'
                    self._response = "File not found"
                    return
                if (
                        not self._is_allowed(cur_file.parent, ACCESS_READ)
                        or not self._is_allowed(cur_file, ACCESS_READ)
                ):
                    self.http_status_code = HTTP_FORBIDDEN
                    self.http_header['Content-type'] = 'text/html'
                    self._response = "Access denied"
                    return

            mime = self._mimetype(cur_file)
            parts = mime.split('/', 2)

            if parts[0] == 'image':
                disp = 'image'
            elif parts[0] == 'text':
                disp = 'inline'
            else:
                disp = 'attachments'

            self.http_status_code = HTTP_OK
            self.http_header['Content-type'] = mime
            self.http_header['Content-Disposition'] = disp + '; filename=' + cur_file.name
            self.http_header['Content-Location'] = str(cur_file).replace(self._options['root'], "")
            self.http_header['Content-Transfer-Encoding'] = 'binary'
            self.http_header['Content-Length'] = str(Path(cur_file).stat().st_size)
            self.http_header['Connection'] = 'close'
            self.http_header['file'] = open(cur_file, 'r')
            return

        else:  # try dir
            path = Path(self._options['root'])

            if 'target' in self._request and self._request['target']:
                target = self._find_dir(self._request['target'], None)

                if not target:
                    self._response['error'] = "Invalid parameters"
                elif not self._is_allowed(target, ACCESS_READ):
                    self._response['error'] = "Access denied"
                else:
                    path = target

            self._content(path, API_TREE in self._request)

        pass

    def _cmd_rename(self) -> None:
        """ Rename file or dir """
        current = name = target = None
        cur_dir = cur_name = new_name = None

        if API_NAME in self._request and API_CURRENT in self._request and API_TARGET in self._request:
            name = self._request[API_NAME]
            current = self._request[API_CURRENT]
            target = self._request[API_TARGET]

            cur_dir = self._find_dir(current, None)
            cur_name = self._find(target, cur_dir)
            new_name = Path(cur_dir).joinpath(name)

        if not cur_dir or not cur_name:
            self._response[RSP_ERROR] = "File not found"
        elif not self._is_allowed(cur_dir, ACCESS_WRITE) and self._is_allowed(cur_name, ACCESS_RM):
            self._response[RSP_ERROR] = "Access denied"
        elif not self._check_name(name):
            self._response[RSP_ERROR] = "Invalid name"
        elif Path(new_name).exists():
            self._response[RSP_ERROR] = "File or folder with the same name already exists"
        else:
            self._rm_tmb(cur_name)
            try:
                os.rename(cur_name, new_name)
                self._response[RSP_SELECT] = [make_hash(str(new_name))]
                self._content(cur_dir, new_name.is_dir())
            except:
                self._response['error'] = "Unable to rename file"

    def _cmd_mkdir(self) -> None:
        """ Create new directory. """
        name = new_dir = path = None

        if API_NAME in self._request and API_CURRENT in self._request:
            name = self._request[API_NAME]
            current = self._request[API_CURRENT]
            path = self._find_dir(current, None)
            new_dir = Path(path).joinpath(name)

        if not path:
            self._response[RSP_ERROR] = "Invalid parameters"
        if not self._is_allowed(path, ACCESS_WRITE):
            self._response[RSP_ERROR] = "Access denied"
        elif not self._check_name(name):
            self._response['error'] = "Invalid name"
        elif new_dir.exists():
            self._response[RSP_ERROR] = "File or folder with the same name already exists"
        else:
            try:
                new_dir.mkdir(mode=0o755)
                self._response[RSP_SELECT] = [make_hash(str(new_dir))]
                self._content(path, True)
            except:
                self._response[RSP_ERROR] = "Unable to create folder"

    def _cmd_mkfile(self) -> None:
        """ Create new file. """
        name = cur_dir = new_file = None

        if API_NAME in self._request and API_CURRENT in self._request:
            name = self._request[API_NAME]
            current = self._request[API_CURRENT]
            cur_dir = self._find_dir(current, None)
            new_file = Path(cur_dir).joinpath(name)

        if not cur_dir and not new_file:
            self._response[RSP_ERROR] = "Invalid parameters"
        elif not self._is_allowed(cur_dir, ACCESS_WRITE):
            self._response[RSP_ERROR] = "Access denied"
        elif not self._check_utf8(name):
            self._response[RSP_ERROR] = "Invalid name"
        elif new_file.exists():
            self._response[RSP_ERROR] = "File or folder with the same name already exists"
        else:
            try:
                open(new_file, 'w').close()
                self._response[RSP_SELECT] = [make_hash(str(new_file))]
                self._content(cur_dir, False)
            except:
                self._response[RSP_ERROR] = "Unable to create file"

    def _cmd_rm(self) -> bool:
        """ Delete files and directories. """
        rm_list = cur_dir = None

        if API_CURRENT in self._request and API_TARGETS in self._request:
            current = self._request[API_CURRENT]
            rm_list = self._request[API_TARGETS]
            cur_dir = self._find_dir(current, None)

        if not rm_list or not cur_dir:
            self._response[RSP_ERROR] = "Invalid parameters"
            return False

        if not isinstance(rm_list, list):
            rm_list = [rm_list]

        for rm in rm_list:
            rm_file = self._find(rm, cur_dir)
            if not rm_file:
                continue
            self._remove(rm_file)

        # TODO if errorData not empty return error
        self._content(cur_dir, True)
        return True

    def _cmd_paste(self) -> None:
        """ Copy or cut files/directories. """
        if API_CURRENT in self._request and API_SRC in self._request and API_DEST in self._request:
            cur_dir = self._find_dir(self._request[API_CURRENT], None)
            src = self._find_dir(self._request[API_SRC], None)
            dest = self._find_dir(self._request[API_DEST], None)

            if not cur_dir or not src or not dest or not 'targets[]' in self._request:
                self._response[RSP_ERROR] = "Invalid parameters"
                return

            files = self._request['targets[]']
            if not isinstance(files, list):
                files = [files]

            cut = False
            if API_CUT in self._request and self._request[API_CUT] == '1':
                cut = True

            if not self._is_allowed(src, ACCESS_READ) or not self._is_allowed(dest, ACCESS_WRITE):
                self._response[RSP_ERROR] = "Access denied"
                return

            for file_hash in files:
                f = self._find(file_hash, src)
                if not f:
                    self._response[RSP_ERROR] = "File not found"
                    return
                new_dest = dest.joinpath(f.name)

                if str(dest).find(str(f)) == 0:
                    self._response[RSP_ERROR] = "Unable to copy into itself"
                    return

                if cut:
                    if not self._is_allowed(f, ACCESS_RM):
                        self._response[RSP_ERROR] = "Move failed"
                        self._set_error_data(str(f), "Access denied")
                        self._content(cur_dir, True)
                        return
                    # TODO thumbs
                    if new_dest.exists():
                        self._response[RSP_ERROR] = "Unable to move files"
                        self._set_error_data(str(f), "File or folder with the same name already exists")
                        self._content(cur_dir, True)
                        return
                    try:
                        f.rename(new_dest)
                        self._rm_tmb(f)
                        continue
                    except:
                        self._response[RSP_ERROR] = "Unable to move files"
                        self._set_error_data(str(f), "Unable to move")
                        self._content(cur_dir, True)
                        return
                else:
                    if not self._copy(f, new_dest):
                        self._response[RSP_ERROR] = "Unable to copy files"
                        self._content(cur_dir, True)
                        return
                    continue

            self._content(cur_dir, True)
        else:
            self._response[RSP_ERROR] = "Invalid parameters"
        return

    def _cmd_duplicate(self)  -> None:
        """ Create copy of files/directories. """
        cur_dir = None
        if 'current' in self._request and 'target' in self._request:
            cur_dir = self._find_dir(self._request['current'], None)
            target = self._find(self._request['target'], cur_dir)

            if not cur_dir or not target:
                self._response[RSP_ERROR] = "Invalid parameters"
                return

            if not self._is_allowed(target, ACCESS_READ) or not self._is_allowed(cur_dir, ACCESS_WRITE):
                self._response[RSP_ERROR] = "Access denied"

            new_name = make_unique_name(target)

            if not self._copy(target, new_name):
                self._response[RSP_ERROR] = "Unable to create file copy"
                return

        self._content(cur_dir, True)
        return

    def _cmd_upload(self) -> None:
        """ Upload files. """
        try:  # Windows needs stdio set for binary mode.
            import msvcrt  # pylint: disable=import-outside-toplevel

            msvcrt.setmode(0, os.O_BINARY)  # type: ignore
            msvcrt.setmode(1, os.O_BINARY)  # type: ignore
        except ImportError:
            pass


        if API_CURRENT in self._request:
            cur_dir = self._find_dir(self._request[API_CURRENT], None)

            if not cur_dir:
                self._response[RSP_ERROR] = "Invalid parameters"
                return
            if not self._is_allowed(cur_dir, ACCESS_WRITE):
                self._response[RSP_ERROR] = "Access denied"
                return
            if not API_WIDTH in self._request:
                self._response[RSP_ERROR] = "No file to upload"
                return

            upload_files = self._request[API_WIDTH]
            # invalid format
            # must be dict('filename1': 'filedescriptor1', 'filename2': 'filedescriptor2', ...)
            if not isinstance(upload_files, dict):
                self._response[RSP_ERROR] = "Invalid parameters"
                return

            self._response[RSP_SELECT] = []
            total = 0
            uploaded_size = 0
            max_size = self._options['uploadMaxSize'] * 1024 * 1024

            self._response[RSP_SELECT] = []
            for name, data in upload_files.items():
                if name:
                    total += 1
                    name = Path(name).name

                    if not self._check_name(name):
                        self._set_error_data(str(name), "Invalid name")
                    else:
                        name = cur_dir.joinpath(name)
                        try:
                            # name.touch(0o644)
                            f = open(name, 'wb', self._options['uploadWriteChunk'])
                            for chunk in self._fbuffer(data):
                                f.write(chunk)
                            f.close()

                            uploaded_size += name.lstat().st_size

                            if self._is_upload_allow(str(name)):
                                name.chmod(self._file_options['fileMode'])
                                self._response[RSP_SELECT].append(make_hash(str(name)))
                            else:
                                self._set_error_data(str(name), "Not allowed file type")
                                try:
                                    name.unlink()
                                except OSError:
                                    pass
                        except:  # OSError
                            self._set_error_data(str(name), "Unable to save uploaded file")

                        if uploaded_size > max_size:
                            try:
                                name.unlink()
                                self._set_error_data(str(name), "File exceeds the maximum allowed filesize'")
                            except OSError:
                                pass
                            break

            if self._error_data:
               if len(self._error_data) == total:
                   self._response[RSP_ERROR] = "Unable to upload files"
               else:
                   self._response[RSP_ERROR] = "Some files was not uploaded"

            self._content(cur_dir, False)
            return


    def _cmd_resize(self) -> None:
        """ Scale image size. """
        cur_dir = self._find_dir(self._request[API_CURRENT], None)
        cur_file = self._find(self._request.get(API_TARGET), cur_dir)
        width = int(self._request.get(API_WIDTH))
        height = self._request.get(API_HEIGHT)

        if not (cur_file is not None and width is not None and height is not None):
            self._response[RSP_ERROR] = "Invalid parameters"
            return

        width = int(width)
        height = int(height)

        if width < 1 or height < 1:
            self._response[RSP_ERROR] = "Invalid parameters"
            return

        if not self._is_allowed(cur_file, ACCESS_WRITE):
            self._response[RSP_ERROR] = "Access denied to write file"
            return

        if self._mimetype(cur_file).find('image') != 0:
            self._response[RSP_ERROR] = "Invalid parameters"
            return

        self._debug('resize', f"Resize {cur_file}: to {width}x{height}")

        if not self._init_img_lib():
            return

        try:
            img = self._im.open(cur_file)
            img_resized = img.resize((width, height), self._im.ANTIALIAS)  # type: ignore
            img_resized.save(cur_file)
            self._rm_tmb(cur_file)
        except OSError as exc:
            self._debug(f"resizeFailed_{cur_file}", str(exc))
            self._response[RSP_ERROR] = "Unable to resize image"
            return

        self._response[RSP_SELECT] = [make_hash(str(cur_file)), ]
        self._content(cur_dir, True)

    def _cmd_thumbnails(self) -> bool:
        """ Create previews for images. """
        if API_CURRENT in self._request:
            cur_dir = self._find_dir(self._request[API_CURRENT], None)
            if not cur_dir or cur_dir == self._options['tmbDir']:
                return False
        else:
            return False

        self._init_img_lib()

        if self._can_create_tmb():
            tmb_max = 0
            if self._options['tmbAtOnce'] > 0:
                tmb_max = self._options['tmbAtOnce']

            self._response[API_CURRENT] = make_hash(str(cur_dir))
            self._response[RSP_IMAGES] = {}
            i = 0

            for f in cur_dir.iterdir():
                fhash = make_hash(str(f))

                _can_create_thumb_f = self._can_create_tmb(f)
                _allow_read_f = self._is_allowed(f, ACCESS_READ)

                if self._can_create_tmb(f) and self._is_allowed(f, ACCESS_READ):
                    tmb_path = Path(self._options['tmbDir']).joinpath(f"{fhash}.png")

                    if not tmb_path.exists():

                        if self._make_tmb(str(f), str(tmb_path)):
                            self._response[RSP_IMAGES].update(
                                {fhash: self._path2url(tmb_path), }
                            )
                            i += 1

                if i >= tmb_max:
                    self._response['tmb'] = True
                    break

        else:
            return False

        return True

    def _cmd_ping(self) -> None:
        """ Workaround for Safari. """
        self.http_status_code = 200
        self.http_header["Connection"] = "close"

    def _content(self, path: Path, tree):
        """ CWD + CDC + maybe(TREE) """
        self._cwd(path)
        self._cdc(path)

        if tree:
            self._response[API_TREE] = self._get_dirs_tree(Path(self._options['root']))

    def _cwd(self, path: Path) -> None:
        """ Get Current Working Directory. """
        name = path.name
        if path == self._options['root']:
            name = self._options['rootAlias']
            root = True
        else:
            root = False

        if self._options['rootAlias']:
            basename = self._options['rootAlias']
        else:
            basename = Path(self._options['root']).name

        rel = basename + str(path)[len(self._options['root']):]

        self._response['cwd'] = {
            'hash': make_hash(str(path)),
            'name': self._check_utf8(name),
            'mime': 'directory',
            'rel': self._check_utf8(rel),
            'size': 0,
            'date': datetime.fromtimestamp(Path(path).stat().st_mtime).strftime('%d %b %Y %H:%M'),
            'read': True,
            'write': self._is_allowed(path, ACCESS_WRITE),
            'rm': not root and self._is_allowed(path, ACCESS_RM),
        }

    def _cdc(self, path: Path):
        """ Current Directory Content" """
        files = []
        dirs = []

        for item in sorted(path.iterdir()):
            if not self._is_accepted(str(item)):
                continue

            path_joined = path.joinpath(item)
            # info = {}
            info = self._info(path_joined)
            info['hash'] = make_hash(str(path_joined))

            if info['mime'] == 'directory':
                dirs.append(info)
            else:
                files.append(info)

        dirs.extend(files)
        self._response['cdc'] = dirs

    def _info(self, path: Path) -> Dict:
        mime = ''
        filetype = "file"

        # pure_path = Path(path)
        if path.is_fifo():
            filetype = 'file'
        if path.is_dir():
            filetype = 'dir'
        if path.is_symlink():
            filetype = 'link'

        stat = path.stat()
        stat_date = datetime.fromtimestamp(stat.st_mtime)

        find_date = ''
        if stat.st_mtime >= self._today:
            find_date = f"Today {stat_date.strftime('%H:%M')}"
        elif self._yesterday <= stat.st_mtime < self._today:
            find_date = f"Yesterday {stat_date.strftime('%H:%M')}"
        else:
            find_date = stat_date.strftime('%d %b %Y %H:%M')

        info = {
            'name': path.name,
            'hash': make_hash(str(path)),
            'mime': 'directory' if filetype == 'dir' else self._mimetype(path),
            'date': find_date,
            'size': self._get_dir_size(path) if filetype == 'dir' else stat.st_size,
            'read': self._is_allowed(path, ACCESS_READ),
            'write': self._is_allowed(path, ACCESS_WRITE),
            'rm': self._is_allowed(path, ACCESS_RM),
        }

        if filetype == 'link':
            link_path = read_link(path)

            if not link_path:
                info['mime'] = 'symlink-broken'
                return info

            if Path(link_path).is_dir():
                info['mime'] = 'directory'
            else:
                info['parent'] = make_hash(str(Path(link_path).parent))
                info['mime'] = self._mimetype(path)

            if self._options['rootAlias']:
                basename = self._options['rootAlias']
            else:
                basename = Path(self._options['root']).name

            info['link'] = make_hash(str(link_path))
            info['linkTo'] = basename + link_path[len(self._options['root']):]
            info['read'] = info['read'] and self._is_allowed(link_path, ACCESS_READ)
            info['write'] = info['write'] and self._is_allowed(link_path, ACCESS_WRITE)
            info['rm'] = self._is_allowed(link_path, ACCESS_RM)
        else:
            link_path = False

        if not info['mime'] == 'directory':
            if self._options['fileURL'] and info['read'] is True:
                if link_path:
                    info['url'] = self._path2url(link_path)
                else:
                    info['url'] = self._path2url(path)

            if info['mime'][0:5] == 'image':
                if self._can_create_tmb():
                    dim = self._get_img_size(path)
                    if dim:
                        info['dim'] = dim
                        info['resize'] = True

                    # if we are in tmb dir, files are thumbs itself
                    if path.parent == self._options['tmbDir']:
                        info['tmb'] = self._path2url(path)
                        return info

                    tmb = Path(self._options['tmbDir']).joinpath(f"{info['hash']}.png'")

                    if Path(tmb).exists():
                        tmb_url = self._path2url(tmb)
                        info['tmb'] = tmb_url
                    else:
                        self._response['tmb'] = True

        return info

    def _get_dirs_tree(self, dir_path: Path):
        """ Return directory tree starting from path. """
        if not dir_path.is_dir():
            return ""
        if dir_path.is_symlink():
            return ""

        if str(dir_path) == self._options['root'] and self._options['rootAlias']:
            name = self._options['rootAlias']
        else:
            name = dir_path.name

        tree = {
            'hash': make_hash(str(dir_path)),
            'name': self._check_utf8(name),
            'read': self._is_allowed(dir_path, ACCESS_READ),
            'write': self._is_allowed(dir_path, ACCESS_WRITE),
            'dirs': []
        }

        if self._is_allowed(dir_path, ACCESS_READ):
            for d in sorted(os.listdir(dir_path)):
                pd = dir_path.joinpath(d)
                if os.path.isdir(pd) and not os.path.islink(pd) and self._is_accepted(d):
                    tree['dirs'].append(self._get_dirs_tree(pd))

        return tree

    def _remove(self, target: Path) -> bool:
        """ Provide internal remove procedure. """
        if not self._is_allowed(target, ACCESS_RM):
            self._set_error_data(str(target), "Access denied")

        if not target.is_dir():
            try:
                self._rm_tmb(target)
                target.unlink()
                return True
            except:
                self._set_error_data(str(target), "Remove failed")
                return False
        else:
            for item in target.iterdir():
                if self._is_accepted(str(item)):
                    self._remove(target.joinpath(item))

            try:
                target.rmdir()
                return True
            except:
                self._set_error_data(str(target), "Access denied")
                return False
        pass

    def _copy(self, src: Path, dest: Path) -> bool:
        """ Provide internal copy procedure. """
        dest_dir = Path(dest).parent

        if not self._is_allowed(src, ACCESS_READ):
            self._set_error_data(str(src), "Access denied")
            return False

        if not self._is_allowed(dest_dir, ACCESS_WRITE):
            self._set_error_data(str(dest_dir), "Access denied")
            return False

        if dest.exists():
            self._set_error_data(str(dest), "File or folder with the same name already exists")
            return False

        if not src.is_dir():
            try:
                shutil.copyfile(src, dest)
                shutil.copymode(src, dest)
                return True
            except:
                self._set_error_data(str(src), "Unable to copy files")
                return False
        else:
            try:
                # dest.mkdir()
                shutil.copytree(src, dest)
                shutil.copymode(src, dest)
            except:
                self._set_error_data(str(src), "Unable to copy files")
                return False

        return True

    def _find_dir(self, fhash: str, path: Optional[Path] = None) -> Optional[Path]:
        """ Find directory by hash. """
        find_hash = str(fhash)
        if not path:
            path = Path(self._options['root'])
            if find_hash == make_hash(str(path)):
                return path

        if not path.is_dir():
            return None

        for d in path.iterdir():
            path_joined = path.joinpath(d)
            if path_joined.is_dir() and not path_joined.is_symlink():
                if find_hash == make_hash(str(path_joined)):
                    return path_joined
                else:
                    ret_val = self._find_dir(find_hash, path_joined)
                    if ret_val:
                        return ret_val

        return None

    def _find(self, fhash: str, parent_dir: Optional[Path] = None) -> Optional[Path]:
        """ Find file/dir by hash. """
        find_hash = str(fhash)

        if parent_dir.is_dir():
            for d in parent_dir.iterdir():
                path_joined = parent_dir.joinpath(d)
                if find_hash == make_hash(str(path_joined)):
                    return path_joined

        return None

    def _cmd_read(self):
        if API_CURRENT in self._request and API_TARGET in self._request:
            cur_dir = self._find_dir(self._request[API_CURRENT], None)
            cur_file = self._find(self._request[API_TARGET], cur_dir)

            if cur_dir and cur_file:
                if self._is_allowed(cur_dir, ACCESS_READ):
                    self._response[RSP_CONTENT] = open(cur_file, "r").read()
                else:
                    self._response[RSP_ERROR] = "Access denied"
                return

        self._response[RSP_ERROR] = "Invalid parameters"
        return

    def _cmd_edit(self):
        """ Save content in file """
        if API_CURRENT in self._request and API_TARGET in self._request and API_CONTENT in self._request:
            cur_dir = self._find_dir(self._request[API_CURRENT], None)
            cur_file = self._find(self._request[API_TARGET], cur_dir)

            if cur_dir and cur_file:
                if self._is_allowed(cur_file, ACCESS_WRITE):
                    try:
                        with open(cur_file, "w") as f:
                            f.write(self._request[API_CONTENT])

                        self._response[API_TARGET] = self._info(cur_file)
                    except :
                        self._response[RSP_ERROR] = "Unable to write to file"
                else:
                    self._response[RSP_ERROR] = "Access denied"
            return

        self._response[RSP_ERROR] = "Invalid parameters"
        return


    def _mimetype(self, path: Path) -> str:
        """ Detect mimetype of file. """
        mime = mimetypes.guess_type(path)[0] or "unknown"
        ext = path.suffix

        if mime == 'unknown' and ext in mimetypes.types_map:
            mime = mimetypes.types_map[ext]

        if mime == 'text/plain' and ext == '.pl':
            mime = self._mimeType_list[ext]

        if mime == 'application/vnd.ms-office' and ext == '.doc':
            mime = self._mimeType_list[ext]

        if mime == 'unknown':
            if Path(path).stem in ['README', 'ChangeLog']:
                mime = 'text/plain'
            else:
                mime = self._mimeType_list.get(ext, mime)

        return mime

    def _make_tmb(self, path: str, tmb_path: str) -> bool:
        """ Provide internal thumbnail create procedure. """
        try:
            im = self._im.open(path).copy()
            size = self._options['tmbSize'], self._options['tmbSize']
            box = crop_tuple(im.size)

            if box:
                im.crop(box)

            im.thumbnail(size, self._im.ANTIALIAS)
            im.save(tmb_path, 'PNG')

        except Exception as e:
            self._debug(f"tmbFailed_{path}", str(e))
            return False

        return True

    def _rm_tmb(self, path: Path) -> None:
        """ Remove thumbnail for get image file """
        tmb = Path(self._tmb_path(path))
        if tmb:
            if tmb.exists():
                try:
                    tmb.unlink()
                except OSError:
                    pass

    def _get_dir_size(self, path: Path) -> int:
        """ Get size of directory entry """
        total_size = 0

        if self._options['dirSize']:
            for dir_path, dir_names, file_names in os.walk(path):
                for f in file_names:
                    fp = Path(dir_path).joinpath(f)
                    if fp.exists():
                        total_size += fp.stat().st_size
        else:
            total_size = Path(path).stat().st_size

        return total_size

    def _fbuffer(self, f, chunk_size=_options['uploadWriteChunk']):
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def _can_create_tmb(self, path: Optional[Path] = None) -> bool:
        """ Check file path for ability to creating thumbnail """
        if self._options['imgLib'] and self._options['tmbDir']:
            if path is not None:
                mime = self._mimetype(path)
                if mime[0:5] != "image":
                    return False
            return True
        else:
            return False

    def _tmb_path(self, path: Path):
        """ Generate path for thumbnail """
        tmb = ""
        if self._options['tmbDir']:
            if not path.parent == self._options['tmbDir']:
                tmb = Path(self._options['tmbDir']).joinpath(f"{make_hash(str(path))}.png")
        return tmb

    def _is_upload_allow(self, name: str) -> bool:
        allow = False
        deny = False
        mime = self._mimetype(Path(name))

        if 'all' in self._options['uploadAllow']:
            allow = True
        else:
            for a in self._options['uploadAllow']:
                if mime.find(a) == 0:
                    allow = True

        if 'all' in self._options['uploadDeny']:
            deny = True
        else:
            for d in self._options['uploadDeny']:
                if mime.find(d) == 0:
                    deny = True

        if self._options['uploadOrder'][0] == 'allow':  # ,deny
            if deny is True:
                return False
            elif allow is True:
                return True
            else:
                return False
        else:  # deny,allow
            if allow is True:
                return True
            elif deny is True:
                return False
            else:
                return True

    def _is_accepted(self, target: str) -> bool:
        if target in ('.', '..',):
            return False
        if target[0:1] == '.' and not self._options['dotFiles']:
            return False

        return True

    def _is_allowed(self, path: Path, access: str) -> bool:
        """ Check access rights (on read, write or remove) for path """
        if not path.exists():
            return False

        if access == 'read':
            if not os.access(path, os.R_OK):
                self._set_error_data(str(path), access)
                return False
        elif access == 'write':
            if not os.access(path, os.W_OK):
                self._set_error_data(str(path), access)
                return False
        elif access == 'rm':
            if not os.access(path.parent, os.R_OK):
                self._set_error_data(str(path), access)
                return False
        else:
            return False

        # TODO - make len add from path
        return bool(self._options['defaults'][access])

    def _path2url(self, path: Path) -> str:
        cur_dir = str(path)
        length = len(self._options["root"])
        url = self._check_utf8(self._options['URL'] + cur_dir[length:]).replace(os.sep, "/")
        url = quote(url, safe='/')
        return url

    def _set_error_data(self, path: str, msg: str) -> None:
        """ Collect error/warning messages. """
        # self._set_error_data(path, msg)
        self._error_data[path] = msg

    def _init_img_lib(self):
        """ Try import image class from PIL, if 'imgLib' options is not set """
        if not self._options['imgLib'] is False and self._im is None:
            try:
                from PIL import Image
                self._im = Image
                self._options['imgLib'] = 'PIL'
            except ImportError:
                self._im = False
                self._options['imgLib'] = False
                self._debug("ImgLib", "Cannot import 'Image' from PIL")

            self._debug("ImgLib", self._options['imgLib'])

            return self._options['imgLib']

    def _get_img_size(self, path: str):
        """ Get size of image by path. Return string value (WxH) of False value. """
        self._init_img_lib()
        if self._can_create_tmb():
            try:
                im = self._im.open(path)
                return f"{im.size[0]}x{im.size[1]}"
            except:
                pass

        return False

    def _debug(self, key: str, val: Any) -> None:
        """ Add messages to debug dict """
        if self._options[RSP_DEBUG]:
            self._response[RSP_DEBUG].update(
                {key: val, }
            )

    def _check_utf8(self, name: Union[str, bytes]) -> str:
        if isinstance(name, str):
            return name
        try:
            str_name = name.decode('utf-8')
        except UnicodeDecodeError:
            str_name = str(name, 'utf-8', 'replace')
            self._debug("invalid encoding", str_name)
        return str_name

    def _check_name(self, filename: str) -> bool:
        """ Check for valid file name. """
        pattern = r'[\/\\\:\<\>]'
        if re.search(pattern, filename):
            return False
        return True
