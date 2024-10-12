import globalVars
import argparse

def run_argument_parser():
  parser = argparse.ArgumentParser(
                      prog=globalVars.app_name,
                      description='What the program does',
                      epilog='Text at the bottom of help')

  parser.add_argument('-d', '--debug', action = 'store_true', help='print debug information') 
  parser.add_argument('-r', '--rescrap', action = 'store_true', help='force scrap data, overwrite existing scrapped data') 
  parser.add_argument('-c', '--clean', action = 'store_true', help='clean directory from scrapped data') 

  return parser.parse_args()
