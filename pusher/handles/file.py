import sys
import os
import logging

logger = logging.getLogger(__name__)

from .base import IHandle

from zope.interface import implements

class FileHandle:
  implements(IHandle)

  scheme = "file"

  def __init__(self, url, version, config):
    self.url      = url
    self.version  = version
    self.config   = config

    self.size     = None
    self.fileobj  = None
    self.name     = None
    self.mtime    = None
    self.mimetype = None

  def request(self):
    import mimetypes
    mimetypes.init()

    self.size     = os.path.getsize(self.url.path)
    self.fileobj  = file(self.url.path, "r")
    self.name     = os.path.basename(self.url.path)
    self.mtime    = os.stat(self.url.path).st_mtime
    self.mimetype = mimetypes.guess_type(self.name)[0]

  def close(self):
    if self.fileobj is not None:
      self.fileobj.close()
      self.fileobj = None
