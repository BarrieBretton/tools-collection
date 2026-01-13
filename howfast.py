import time
import os
import sys
import shutil

from datetime import datetime as dt


def cpuspeed(testcount=3, runtime=20, log=True): # In seconds, total runtime = 20*3 = 60 seconds
    print('\nInitiating cpu speed test')

    numslist = []

    for _ in range(testcount):
        start = time.time()
        store = []
        num = -1
        while time.time() - start <= runtime:
            num += 1
            store.append(num)
            print(f'  Test {_+1} of {testcount}: Processed {num} calculations', end='\r')

        print()
        numslist.append(num)

    print()

    return numslist, int(sum(numslist)/len(numslist))

def fileIOspeed(testcount=5, runtime=3, log=True): # In seconds, total runtime = 1*3 = 3 seconds
    print('Initiating file I/O speed test')

    testcounts = []

    for _ in range(testcount):
        start = time.time()
        counter = -1

        while time.time() - start <= runtime:
            counter += 1
            os.mkdir(f"TESTDIR_{counter}")
            with open(f'TESTDIR_{counter}/testfile{counter}.test', 'w') as f:
                f.write('')
            os.remove(f'TESTDIR_{counter}/testfile{counter}.test')

            # Patchy way to get around the problem of "Permission Error [WinError 32]" which pops up at random times,
            # so no clue on how to solve it yet...
            # while not os.path.exists(f"TESTDIR_{counter}"):

            while 1:
                try:
                    os.rmdir(f"TESTDIR_{counter}")
                    break
                except OSError:
                    pass

            print(f'  Test {_+1} of {testcount}: Processed #{counter} dirs and files', end='\r')

        print()
        testcounts.append(counter)

    print()

    return testcounts, int(sum(testcounts)/len(testcounts))

def run(log = True, cpuonly=False, ioonly=False):

    '''
    CPU Calcs:
        Factorials till 10k
    OS IO:
        Create dir VIVOJAY.howfast_test_results
        Create multiple folders with 1 file each
        Delete folder after creation
    '''

    unsupportedos = False

    match sys.platform: # Linux unsupported
        # Mac
        case "darwin":
            platf = 'Platform: Mac'

        # Windows
        case "win32":
            platf = 'Platform: Windows'

        case _:
            platf = 'Platform: {unknown/unsupported}'+'\n'+'Aborting - Reason: Unsupported OS'
            unsupportedos = True


    print(f'Ready to run test, logs {["dis", "en"][log]}abled')
    permission = input('Press "y" to confirm run, any other key to abort: ')

    if permission.lower().strip() == 'y':
        if unsupportedos:
            sys.exit('Aborting program due to unsupported OS')

        os.chdir(os.path.expanduser('~/Desktop'))
        if not os.path.isdir('VIVOJAY.howfast_test_results'):
            os.mkdir('VIVOJAY.howfast_test_results')
            os.chdir('VIVOJAY.howfast_test_results')
        else:
            try:
                shutil.rmtree('VIVOJAY.howfast_test_results')
                os.mkdir('VIVOJAY.howfast_test_results')
                os.chdir('VIVOJAY.howfast_test_results')
            except Exception:
                sys.exit('Unexpected error experienced, please delete the folder "VIVOJAY.howfast_test_results" from your desktop folder manually')

        if log:
            try:
                os.mkdir('logs')
                os.chdir('logs')
            except OSError:
                print('Directory creation failed') # Non fatal error

            if os.path.isfile('howfast_computer_test.log'):
                print("[INFO] Overwriting existing test log")

            with open('howfast_computer_test.log', 'w') as file:
                file.write("\n")
                file.write("\n"+f"Test Start Datetime: {dt.now()}"+"\n")
                file.write(platf)
                file.write("\n")
                file.write("\n")

        # Display results
        CPUS, IOS = cpuspeed(log=log), fileIOspeed(log=log)
        print(f'\n\nIndividual test scores: Processed {CPUS[0]} items and {IOS[0]} files and dirs')
        print(f'AVG: Processed {CPUS[1]} items and {IOS[1]} files and dirs')

        if log:
            print('Writing logs')

            try:
                with open('howfast_computer_test.log', 'a') as file:
                    file.write(f'CPU speed check individual test scores: {", ".join([str(i) for i in CPUS[0]])}')
                    file.write("\n")

                    file.write(f'IO speed check individual test scores: {", ".join([str(i) for i in IOS[0]])}')
                    file.write("\n")

                    file.write('Aborting - Reason: Successful completion of test\n')
                    file.write("-"*80)
                    file.write("\n")

                    file.write("\n")

                print("CUR DIR"+os.getcwd())

                if os.path.isfile('howfast_computer_result.json'):
                    print("[INFO] Overwriting existing results json")

                with open('howfast_computer_result.json', 'w') as file:
                    import json
                    json.dump(
                        {
                            "CPUSpeed": {
                                "individual_results": CPUS[0],
                                "avg_result": CPUS[1],
                            },
                            "IOSpeed": {
                                "individual_results": IOS[0],
                                "avg_result": IOS[1],
                            },
                        }, file
                    )

                print('Successfully written logs')

            except Exception:
                print('Failed to write logs')

        print("Exiting...")

    else:
        sys.exit('Test aborted...')

if __name__ == '__main__':

    argc = len(sys.argv)
    switchdescs = {
        '-h': 'Show this help',

        '-r': 'Run default test',
        '-s': 'Silent [No logs, not recommended] - Use with "-r" only'
    }

    match argc:
        case 1:
            sys.exit("No switches provided")
            # break
        case 2:
            match sys.argv[1]:
                case '-h':
                    print('Commands:')
                    print(f'Switch{" "*8}|{" "*8}Description')
                    print('='*14+'+'+'='*65)

                    switch, desc = list(switchdescs.items())[0]
                    print(f'{switch}{" "*12}|{" "*8}{desc}')
                    print('- '*40)

                    for switch, desc in list(switchdescs.items())[1:]:
                        print(f'{switch}{" "*12}|{" "*8}{desc}')

                    # break
                case '-r':
                    run()
                    # break
                case '-s':
                    sys.exit("'-s' switch requires '-r' switch, can't be used separately")
        case 3:
            if '-s' in sys.argv:
                if '-r' in sys.argv:
                    run(log=False)
                    # break
                elif '-c' in sys.argv:
                    run(cpuonly=True, log=False)
                elif '-i' in sys.argv:
                    run(ioonly=True, log=False)
                else:
                    if '-h' not in sys.argv:
                        sys.exit("Unknows or illegal order of switches provided")
                    else:
                        sys.exit("'-h' cannot be used with any other switch")

        case _:
            sys.exit("Too many args")


