import scrapper
import argParser
import graphic
import logicAI
import scrapper
from sys import exit

def main():
  args = argParser.run_argument_parser()
  # proccess_arguments

  if args.debug:
    print("debug mode active")
    # TODO

  if args.clean:
    scrapper.clean()
    exit(0)

  scrapper.get_data(args.rescrap)
  graphic.run_app(args)

####################### main ####################### 

if __name__ == '__main__':
  main()
