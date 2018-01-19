from requests import Session
from signalr import Connection
import cfscrape

with Session() as session:
    #create a connection
    with cfscrape.create_scraper() as connection:
        connection = Connection(None, connection)
    connection.url='https://socket-stage.bittrex.com/signalr'
    #get chat hub
    chat = connection.register_hub('coreHub')

    #start a connection
    connection.start()
    def print_received_message(data):
        print('received: ', data)
    print('client on ')
    chat.client.on('updateExchangeState', print_received_message)
    chat.client.on('updateSummaryState', print_received_message)


    chat.server.invoke('SubscribeToSummaryDeltas')
    #create new chat message handler


    #create new chat topic handler
    def print_topic(topic, user):
        print('topic: ', topic, user)

    #create error handler
    def print_error(error):
        print('error: ', error)

    #receive new chat messages from the hub


    #change chat topic
    chat.client.on('topicChanged', print_topic)

    #process errors
    connection.error += print_error

    #start connection, optionally can be connection.start()

    chat.client.on('newMessageReceived', print_received_message)

    print('byby')

    connection.wait(30)