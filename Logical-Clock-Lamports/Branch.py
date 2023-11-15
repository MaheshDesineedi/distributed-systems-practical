from concurrent import futures
import json
import sys
from threading import Lock

import grpc
import bank_pb2
import bank_pb2_grpc

class Branch(bank_pb2_grpc.BankServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # logical clock
        self.logical_clock = 0
        # lock for local thread (Branch)
        self.lock = Lock()
        # iterate the processID of the branches
        for branch in self.branches:
            channel = grpc.insecure_channel(f"localhost:{branch}")
            stub = bank_pb2_grpc.BankStub(channel)
            self.stubList.append(stub)

    # RPC method to handle Customer and Branch requests
    def MsgDelivery(self, request, context):

        # receive customer or branch event by updating clock, balance and add log
        Helper.receive_event(request, self)

        # update clock and send propogate message for each branch asynchronously
        propogate_request = {
            'id': self.id,
            'interface': request.interface,
            'money': request.money,
            'customer_request_id': request.customer_request_id
        }
        Helper.propogate_event(propogate_request, self)

        # send response to customer
        return bank_pb2.BankResponse(result="success", balance=self.balance)

class Helper:
    def serve(id, balance, branches):
        port = 50050 + id  # add the offset for the branch port
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        bank_pb2_grpc.add_BankServicer_to_server(Branch(id, balance, branches), server)
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        print(f"Server started. Listening on port {port}")
        server.wait_for_termination()

    # handle request from customer or branch
    def receive_event(request, branch):
        with branch.lock:
            # update clock according to send/recv order
            branch.logical_clock = max(branch.logical_clock, request.logical_clock) + 1

            if request.interface in ["deposit", "withdraw", "query"]:
                source = ("customer", request.id)
                if request.interface == "deposit":
                    branch.balance = branch.balance + request.money
                elif request.interface == "withdraw":
                    branch.balance = branch.balance - request.money
            else:
                source = ("branch", request.id)
                if request.interface == "Propogate_Deposit":
                    branch.balance = branch.balance + request.money
                elif request.interface == "Propogate_Withdraw":
                    branch.balance = branch.balance - request.money

            # write to a unique branch file
            # other threads sending requests to this branch might write to file so lock is needed
            result = [
                "\"id\":{}".format(branch.id),
                "\"customer-request-id\":{}".format(request.customer_request_id),
                "\"type\":\"branch\"",
                "\"logical_clock\":{}".format(branch.logical_clock),
                "\"interface\":\"{}\"".format(request.interface),
                "\"comment\":\"event_recv from {0} {1}\"".format(source[0], source[1])
            ]

            with open(r'./output/output_branch_{}.json'.format(branch.id), 'a') as fp:
                fp.write('{')
                fp.write(','.join(str(res) for res in result))
                fp.write('}\n')

    def propogate_event(params, branch):

        if params["interface"] == "query":
            return

        # ignore if this is already a propogate request
        if params["interface"] in ["Propogate_Deposit", "Propogate_Withdraw"]:
            return

        # set propogate interface
        propogate_interface = "Propogate_Deposit" if params["interface"] == "deposit" else "Propogate_Withdraw"

        response_futures = []
        # send propogate messages asynchronously
        with branch.lock:
            for i,stub in enumerate(branch.stubList):
                # update clock according to program order
                branch.logical_clock = branch.logical_clock + 1

                response_future = stub.MsgDelivery.future(bank_pb2.BankRequest(
                    id=params["id"],
                    interface=propogate_interface,
                    money=params["money"],
                    customer_request_id=params["customer_request_id"],
                    logical_clock=branch.logical_clock
                ))

                # write to file
                result = [
                    "\"id\":{}".format(branch.id),
                    "\"customer-request-id\":{}".format(params["customer_request_id"]),
                    "\"type\":\"branch\"",
                    "\"logical_clock\":{}".format(branch.logical_clock),
                    "\"interface\":\"{}\"".format(propogate_interface),
                    "\"comment\":\"event_sent to branch {}\"".format(branch.branches[i]-50050)
                ]

                with open(r'./output/output_branch_{}.json'.format(branch.id), 'a') as fp:
                    fp.write('{')
                    fp.write(','.join(str(res) for res in result))
                    fp.write('}\n')

                response_futures.append(response_future)

        for response_future in response_futures:
            # yield result
            response_future.result()



# parse arguments
parameters = json.loads(str(sys.argv[1]).replace("\'", "\""))

Helper.serve(int(parameters["id"]), int(parameters["balance"]), parameters["branches"])
