from carl_car import CARL
import argparse






if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Example script.')
    parser.add_argument('--number', type=int, help='An integer number')
    parser.add_argument('--verbose', action='store_true', help='Increase output verbosity')

    args = parser.parse_args()

    if args.verbose:
        print(f"Verbose mode on. Number is {args.number}")
    else:
        print(f"Number is {args.number}")

    
    print("Test")
    print("Running")
    carl = CARL()
    carl.run()

    print("Deleting carl")
    del carl
    print("End\n")