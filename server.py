import socket
import logging
import re


class Server:
    def __init__(self):
        self.Host = '127.0.0.1'
        self.Port = 1052

        self.client = None
        self.Attempts = 10

        self.objectList = [['********************'],
                           ['**********@@********'],
                           ['**********@@********'],
                           ['********************'],
                           ['********************']]
        self.objectSize = 4
        self.foundPoints = 0
        self.field = \
"""
********************
********************
********************
********************
********************
"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.getLogger("Server")
        logging.basicConfig(filename="server_log.log", level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

        self.run_server()

    def run_server(self):
        logging.info("Server was run")
        self.connect()
        self.sock.listen(1)
        print('Waiting for client :', self.sock.getblocking())

        try:
            self.client, addr = self.sock.accept()
            print('Connected to a client:', addr)
            logging.info(f'Connected to a client {addr}')
            self.client.send(self.initial_message().encode('utf-8'))
            logging.info("Sent info")
            print('Listening to the client...')
            logging.info('Listening to the client')

            while True:
                client_msg = self.client.recv(256).decode('utf-8')
                print('Client\'s message :', client_msg)
                logging.info(f'Client\'s message: {client_msg}')

                try:
                    answer = str(self.handle_client_msg(client_msg))
                    if 'stop' in answer:
                        answer += self.final_message()
                        self.client.send(answer.encode('utf-8'))
                        logging.info(f'Send answer: {answer}')

                        logging.info("Stop marker founded.")
                        logging.info("Connection closed.")
                        logging.info("\n" + "-" * 30 + "\n")
                        break

                    if self.foundPoints == self.objectSize:
                        print(answer)
                        answer += 'You have found full object! You won!'
                        self.client.send(answer.encode('utf-8'))
                        logging.info(f'Send answer: {answer}')

                        logging.info("Stop marker founded.")
                        logging.info("Connection closed.")
                        logging.info("\n" + "-" * 30 + "\n")
                        break

                    if self.Attempts == 0:
                        print(answer)
                        answer += 'You have wasted all your attempts! You lose!'
                        self.client.send(answer.encode('utf-8'))
                        logging.info(f'Send answer: {answer}')

                        logging.info("Stop marker founded.")
                        logging.info("Connection closed.")
                        logging.info("\n" + "-" * 30 + "\n")
                        break

                    self.client.send(answer.encode('utf-8'))
                    logging.info(f'Sent answer: {answer}')

                except Exception as exp:
                    print('Exception:', exp)
                    logging.warning(f'Exception: {exp}')
                    break

        except Exception as exp:
            print('Exception', exp)
            logging.info("Error. Connection closed.")
            self.client.send('stop'.encode('utf-8'))

        finally:
            try:
                self.client.close()
            except Exception as exp:
                print('Exception', exp)
                logging.warning(f'Exception: {exp}')
                print('Connection ended.')
                logging.info("Server stopped!\n" + "-" * 30 + "\n")

    def connect(self):
        try:
            self.sock.bind((self.Host, self.Port))
        except OSError:
            print("Host is used.")
            logging.warning('Host is used.')
            exit()

    def handle_client_msg(self, msg):
        if len(msg) > 0:
            if msg.lower() == 'stop':
                return 'stop\n'
            elif msg.lower() == 'who':
                return self.who()
            elif msg.lower() == 'get_field':
                return self.field
            elif msg[0] == '=':
                return self.parse_request(msg[1:])
            else:
                return 'This command is not supported!'
        else:
            return 'Empty request'

    def parse_request(self, msg):
        self.Attempts -= 1
        pattern = re.compile(
            r"(1?[0-9])\s*\,\s*([0-4])\s*")

        it = re.match(pattern, msg)
        if it:
            pure_msg = it.group(0, 1, 2)

            x_dot = int(pure_msg[1])
            y_dot = int(pure_msg[2])
            try:
                for j, y in enumerate(self.objectList):
                    if j == y_dot:
                        y = y[0]
                        for i, x in enumerate(y):
                            if i == x_dot:
                                if x == '@':
                                    self.foundPoints += 1
                                    self.update_field(x_dot, y_dot)
                                    print(f'Dot at position {x_dot}, {y_dot}, was found!')
                                    logging.info(f'Dot at position {x_dot}, {y_dot}, was found!')
                                    return self.field + f'Dot at position {x_dot}, {y_dot}, was found!\n'

            except Exception as exp:
                print('Exception:', exp)
                logging.warning(f'Exception: {exp}')
                return f'Exception: {exp}'
        else:
            print('Exception : Wrong string index or incorrect expression')
            logging.warning(f'Exception : Wrong string index or incorrect expression')
            return 'Exception : Wrong string index or incorrect expression'

        print(f'Dot at position {x_dot}, {y_dot} was not found!')
        logging.warning(f'Dot at position {x_dot}, {y_dot} was not found!')
        return f'Dot at position {x_dot}, {y_dot} was not found!\n'

    def update_field(self, x_dot, y_dot):
        result = ''
        for i, y in enumerate(self.objectList):
            result += '\n'
            y = y[0]
            for j, x in enumerate(y):
                if i == y_dot and j == x_dot:
                    result += '@'
                else:
                    result += '*'

        for i, ch in enumerate(result):
            if ch == '@':
                s = list(self.field)
                s[i] = '@'
                self.field = "".join(s)

    @staticmethod
    def initial_message():
        return "Write a command from the list below, this will be sent to the server.\n" \
               "Command list:\n\t" \
               "1)'who' : returns information about author.\n\t" \
               "2)'get_field' : returns field of size 20x5 where you should find a hidden object. (count from 0)'\n\t" \
               "3)'=x, y' where x is width position of your dot and y is height position," \
               " you have to count from left top corner.\n\t" \
               "You have only 10 attempts to guess the positions, if you waste all attempts or find the object," \
               " the program end automaticly!\n\t" \
               "Example: =0,4\n\t" \
               "4)'stop' : stops the session."

    @staticmethod
    def final_message():
        return 'You have just ended this program!'

    @staticmethod
    def who():
        return 'Algin Danylo, K25, V27, \'Object recovery\''


def main():
    Server()


if __name__ == "__main__":
    main()
