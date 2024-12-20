import arg_parser
import graphic
import logicAI
import scrapper
from sys import exit

def main():
  args = arg_parser.run_argument_parser()
  # proccess_arguments

  if args.debug:
    print("debug mode active")
    # TODO

  if args.clean:
    scrapper.clean()
    exit(0)

  graphic.run_app(args)

####################### main ####################### 

if __name__ == '__main__':
  main()
