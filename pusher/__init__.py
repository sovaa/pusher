import sys
import os
import logging
import getopt

logger = logging.getLogger(__name__)

from .environment import create_env

def exit_usage(env):
  print("Usage: pusher <command>")
  for c, (short, usage, _) in sorted(env.list_commands()):
    print "  {:25}: {}".format(usage, short)
  sys.exit(1)

def entry():
  """
  Locate pusher.yaml in the current working directory and bootstrap a interactive deploy environment.
  """
  import yaml

  opts = {
    "config": os.path.join(os.getcwd(), "pusher.yaml")
  }

  try:
    getopts, args = getopt.gnu_getopt(sys.argv[1:], "c:l:")
  except getopt.GetoptError, e:
    print >> sys.stderr, "Option parsing failed: " + str(e)
    sys.exit(1)

  for (o, v) in getopts:
    if o == "-c": opts["config"] = v
    if o == "-l": opts["log_level"] = v

  root = os.path.dirname(opts["config"])

  if not os.path.isfile(opts["config"]):
    print >> sys.stderr, "Could not find {}".format(opts["config"])
    sys.exit(1)

  config_yaml = None

  try:
    config_dict = yaml.load(open(opts["config"]))
  except Exception, e:
    print >> sys.stderr, "Failed to open configuration:", str(e)
    sys.exit(1)

  try:
    env = create_env(root, config_dict, opts);
  except RuntimeError, e:
    print >> sys.stderr, str(e)
    sys.exit(1);

  log_level = env.config.get("log_level", "INFO")

  if not hasattr(logging, log_level):
    print >> sys.stderr, "no such log level: " + log_level
    sys.exit(1);

  f="%(asctime)s - %(name)-20s - %(levelname)-7s - %(message)s"
  logging.basicConfig(level=getattr(logging, log_level), format=f)

  if len(args) < 1:
    exit_usage(env)

  command = args[0]
  args    = args[1:]

  try:
    validator, run = env.get_command(command)
  except RuntimeError, e:
    print >> sys.stderr, "Command error: " + str(e)
    exit_usage(env)

  try:
    args, opts = validator(args)
  except RuntimeError, e:
    print >> sys.stderr, "Invalid arguments: " + str(e)
    print >> sys.stderr, ""
    short, usage, docs = env.parse_help_for(run.func_doc)
    print >> sys.stderr, "Usage:", usage
    print >> sys.stderr, "Short:", short
    sys.exit(1)

  status = 0

  try:
    if run(*args):
      logger.info("Command Successful")
    else:
      logger.info("Command Failed")
      status = 1
  finally:
    env.shutdown()

  sys.exit(status)
