import json
import sys
import os
import signal
import subprocess


def term(sig, frame):

    for child in workers:
        print("Terminating child:", child.pid)
        os.kill(child.pid, signal.SIGTERM)

    print("All child processes terminated. Exiting gracefully.")
    sys.exit(0)


"""
    create Branch servers
    
    create a child process for Branch.py
    Branch.py is responsible to create the server on port
"""


def main():
    # parse input json
    with open(sys.argv[1], 'r') as f:
        input_json = json.load(f)

    base_port = 50050
    ports = []

    for input in input_json:
        if input["type"] == "branch":

            id = int(input["id"])
            port = base_port + id
            ports.append(port)

    # add handlers to terminate child processes on exit of main thread
    signal.signal(signal.SIGINT, term)
    signal.signal(signal.SIGTERM, term)

    global workers

    workers = []
    i = 0
    for input in input_json:
        if input["type"] == "branch":

            # branch ID and balance
            id = int(input["id"])
            branch_balance = int(input["balance"])

            # port numbers of all branches except for this branch itself
            branches = [p for p in ports if p != ports[i]]
            i = i+1

            try:
                worker = subprocess.Popen(["python", "Branch.py", str({"id": id, "balance": branch_balance, "branches": branches}).replace(" ", "")])
                workers.append(worker)

            except Exception as e:
                print("Error creating server for branch: ", id)

    # wait for workers to finish
    for worker in workers:
        worker.wait()



if __name__ == "__main__":
    # invoke main logic
    main()




