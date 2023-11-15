import grpc

import bank_pb2
import bank_pb2_grpc

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None
        # logical clock
        self.logical_clock = 0

    def createStub(self):
        port = 50050 + int(self.id)  # add the offset for the branch port
        channel = grpc.insecure_channel(f"localhost:{port}")
        self.stub = bank_pb2_grpc.BankStub(channel)

    def executeEvents(self, lock):
        bank_response_futures = []

        for event in self.events:

            # increment logical clock
            self.logical_clock = self.logical_clock + 1

            # send request to branch asynchronously
            bank_response_future = self.stub.MsgDelivery.future(bank_pb2.BankRequest(
                id=self.id,
                interface=event["interface"],
                money=event["money"],
                customer_request_id=event["customer-request-id"],
                logical_clock=self.logical_clock
            ))

            # write customer event to the file with lock
            with lock:
                # write to file
                result = [
                    "\"id\":{}".format(self.id),
                    "\"customer-request-id\":{}".format(event["customer-request-id"]),
                    "\"type\":\"customer\"",
                    "\"logical_clock\":{}".format(self.logical_clock),
                    "\"interface\":\"{}\"".format(event["interface"]),
                    "\"comment\":\"event_sent from customer {}\"".format(self.id)
                ]

                with open(r'./output/output_customer.json', 'a') as fp:
                    fp.write('{')
                    fp.write(','.join(str(res) for res in result))
                    fp.write('}\n')

            bank_response_futures.append(bank_response_future)

        # yield the result
        for bank_response_future in bank_response_futures:
            print("response received from branch: ", bank_response_future.result())
