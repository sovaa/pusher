import sys
import os
import logging

logger = logging.getLogger(__name__)

from .base import CompBase

class Deploy(CompBase):
  __group__ = "deploys"

  __keys__ = {
    "modules": list,
    "checks": list,
    "servers": list,
  }

  def setup(self, env):
    for attr in self.__keys__:
      d = list()
      sym = self.config.get(attr, [])

      real = getattr(env, attr)
      for s in sym:
        if s not in real:
          raise RuntimeError, "{0}: symbol not valid: {1}".format(attr, s)
        i = real[s]
        d.append(i.__class__(i.config.subp(self.config)))

      setattr(self, attr, d)

