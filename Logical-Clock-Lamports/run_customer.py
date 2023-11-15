import sys
import json
from threading import Thread, Lock
import os

import Customer as client


"""
    Create Customer Process and execute events
"""
def execute_customer_events(id, events, lock):
    customer_obj = client.Customer(id, events)
    customer_obj.createStub()
    return customer_obj.executeEvents(lock)

def consolidate_customer(count, type):
    with open('./output/output_customer.json') as f:
        lines = [line.rstrip() for line in f]

    output = {}
    for line in lines:
        params = json.loads(str(line).replace("\'", "\""))
        id = params["id"]
        del params["id"]
        del params["type"]

        if id in output:
            output[id].append(params)
        else:
            output[id] = [params]

    result = []
    for i in range(count):
        res = {"id": i+1, "type": type, "events": output[i+1]}
        result.append(res)

    # write to file
    with open(r'./output/final_output_customer.json', 'w') as fp:
        fp.write('[')
        fp.write(','.join(str(res).replace("\'", "\"") for res in result))
        fp.write(']')

def consolidate_branch(count, type):
    output = {}
    result = []
    for i in range(count):

        with open('./output/output_branch_{}.json'.format(i+1)) as f:
            lines = [line.rstrip() for line in f]

        for line in lines:
            params = json.loads(str(line).replace("\'", "\""))
            id = params["id"]
            del params["id"]
            del params["type"]

            if id in output:
                output[id].append(params)
            else:
                output[id] = [params]

        res = {"id": i+1, "type": type, "events": output[i+1]}
        result.append(res)

    # write to file
    with open(r'./output/final_output_branch.json', 'w') as fp:
        fp.write('[')
        fp.write(','.join(str(res).replace("\'", "\"") for res in result))
        fp.write(']')

def consolidate_all_events(count):
    result = []

    for i in range(count):
        with open('./output/output_branch_{}.json'.format(i+1)) as f:
            lines = [line.rstrip() for line in f]

        for line in lines:
            params = json.loads(str(line).replace("\'", "\""))
            result.append(params)

    for i in range(count):
        with open('./output/output_customer.json'.format(i+1)) as f:
            lines = [line.rstrip() for line in f]

        for line in lines:
            params = json.loads(str(line).replace("\'", "\""))
            result.append(params)

    # write to file
    with open(r'./output/final_output_all_events.json', 'w') as fp:
        fp.write('[')
        fp.write(','.join(str(res).replace("\'", "\"") for res in result))
        fp.write(']')


def main():
    # parse input json
    with open(sys.argv[1], 'r') as f:
        input_json = json.load(f)

    worker_threads = []

    #create lock
    lock = Lock()

    for input in input_json:
        if input["type"] == "customer":

            id = int(input["id"])
            events = input["customer-requests"]

            workerThread = Thread(target=execute_customer_events, args=[id, events, lock])
            worker_threads.append(workerThread)
            workerThread.start()

    # wait for thread to finish
    for t in worker_threads:
        t.join()

    count = int(len(input_json)/2)
    consolidate_customer(count, "customer")
    consolidate_branch(count, "branch")
    consolidate_all_events(count)

    #delete other files
    os.remove('./output/output_customer.json')

    for i in range(count):
        os.remove('./output/output_branch_{}.json'.format(i+1))

    print("All output files:")
    print("Customer: ./output/final_output_customer.json")
    print("Branch: ./output/final_output_branch.json")
    print("Branch: ./output/final_output_all_events.json")



if __name__ == "__main__":
    main()