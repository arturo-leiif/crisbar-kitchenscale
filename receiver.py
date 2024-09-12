import machine
from machine import Pin
import network
import socket
import ujson
import time

from hx711 import HX711
from utime import sleep_us

# Initialize a global dictionary to store the order number and weight range
order_weights = {}

# connect to Wi-Fi network
def wifi_connect(SSID, password):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, password)
    while not wifi.isconnected():
        pass
    print("Wifi connected")
    print("IP: ", wifi.ifconfig()[0])

def socket_connect(pushbutton, buzzer, scales):
    # create a HTTP server socket (HTTP endpoint)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(1)
     
    # wait for incoming requests
    while True:
        print("Waiting for event")
        client_socket, client_address = server_socket.accept()
        
        # Get the header
        request_header = client_socket.recv(1024)
        
        # Get the body
        request_body = client_socket.recv(1024)
        
        payload = ujson.loads(request_body)
        
        # To do: Implement signature authentication
        
        # Get the type and event
        data_type = payload.get('type')
        event = payload.get('event')
        
        # Type: Order
        # Events:
        #   - in_progress (new order incoming)
        #   - ready
        #   - completed
        
        # If not 'order' type, then skip
        if (data_type != 'order'):
            respond(client_socket)
            continue
        
        # For new orders (in_progress), get total weight and order number, then save data
        if (event == "in_progress"):
            
            print("NEW ORDER!!!")
            
            # Get order id
            order_id = payload['data']['id']
            print("Order id.", order_id)
            
            # Initialize minimum and maximum total weights
            min_total_weight = 0
            max_total_weight = 0

            # Add each item in the order to total weights
            for item in payload['data']['order_items']:
                # Extract lower and upper weights by splitting the string (from SKU)
                lower_weight, upper_weight = map(int, item['sku'].split(','))

                # Convert quantity to integer
                quantity = int(item['quantity'])

                # Calculate minimum and maximum weights for each item
                min_total_weight += lower_weight * quantity
                max_total_weight += upper_weight * quantity

            print("Minimum Total Weight:", min_total_weight)
            print("Maximum Total Weight:", max_total_weight)
            
            # Save the order-weight range pair
            save_order_weight(order_id, min_total_weight, max_total_weight)
            
        # send response back to the client
        respond(client_socket)
        
        # For testing purposes, we go straight to weigh in
        weigh_in(get_order_weight(order_id), pushbutton, buzzer, scales)
        
    
def respond(client_socket):
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nData received"
    client_socket.send(response.encode())
    client_socket.close()

def save_order_weight(order_number, min_weight, max_weight):
    """
    Save the order number and weight range in memory.
    """
    global order_weights
    # Store the weight range as a tuple (min_weight, max_weight)
    order_weights[order_number] = (min_weight, max_weight)
    print(f"Order {order_number} weight range saved: ({min_weight}, {max_weight})")

def get_order_weight(order_number):
    """
    Retrieve the weight range for the given order number and free up memory.
    """
    global order_weights
    
    # Check if the order number exists in memory
    if order_number in order_weights:
        weight_range = order_weights.pop(order_number)  # Remove and return the weight range
        print(f"Order {order_number} weight range: {weight_range}")
        return weight_range
    else:
        print(f"Order {order_number} not found.")
        return None

def weigh_in(weight_range, pushbutton, buzzer, scales):
    print("Ready to weight in")
    print("Waiting for button press")
    # Wait for button press
    while True:
        if pushbutton.value() == 1:
            print("Pressed")
            break
        time.sleep(0.2)
    
    # Weigh in when button is pressed
    val = scales.stable_value()
    final_val = round(val * 0.00142)
    print(final_val, "g")
    
    # Check if within range
    if final_val >= weight_range[0] and final_val <= weight_range[1]:
        buzz_correct(buzzer)
    else:
        # Keep buzzing until object is removed
        while True:
            buzz_incorrect(buzzer)
            time.sleep(0.5)
            val = scales.stable_value()
            final_val = round(val * 0.00142)
            if final_val == 0:
                break

def buzz_correct(buzzer):
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)
    time.sleep(0.03)
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)
    
def buzz_incorrect(buzzer):
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)
    time.sleep(0.03)
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)
    time.sleep(0.03)
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)
    
class Scales(HX711):
    def __init__(self, d_out, pd_sck):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = 0

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=10, delay_us=500):
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        return self._stabilizer(values)

    @staticmethod
    def _stabilizer(values, deviation=10):
        weights = []
        for prev in values:
            if (prev !=0):
                weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]


def main():
    # Declare components
    pushbutton = Pin(14, Pin.IN, Pin.PULL_DOWN)
    buzzer = Pin(15, Pin.OUT)
    
    # Tare scale
    scales = Scales(d_out=5, pd_sck=4)
    scales.tare()
    
    # Declare wifi info
    SSID = "Jared Wifi-2G"
    password = "Ja19982002"
    
    # Connect to wifi
    wifi_connect(SSID, password)
    
    # Connect to webhook
    socket_connect(pushbutton, buzzer, scales)
    
main()