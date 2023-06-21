import datetime as dt
import logging
import struct

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.animation as anim
from serial import Serial
from serial.serialutil import PortNotOpenError, SerialException
from serial.tools.list_ports import comports

# graph properties
VALS_WINDOW = 60  # seconds before moving graph along
STYLESHEET = r'C:\Users\lnick\Documents\Personal\Programming\Python\Resources\proplot_style.mplstyle'  # larger screen size

# temperature safe limits - warnings will be set off outside this range
T_MAX = 45  # hot limit
T_MIN = 40  # cold limit

# hardware properties
USE_COM_PORT = None  # can be autodetected if not known e.g. 'COM5'
_BAUD_RATE = 115200  # baud rate, set by arduino program
_PORT_DESC_KEYWORD = 'Standard Serial over Bluetooth link'  # search COM port descriptions for this keyword
_TIME_STEP = 1  # value sent once per second, set by arduino program

# logging/recording/saving data
OUTPUT_FILENAME = 'all_temp_vals.csv'  # output all temp data after closing
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='temperature_sensor.log', encoding='utf-8', level=logging.DEBUG)
logging.captureWarnings(True)


if STYLESHEET is not None:
    plt.style.use(STYLESHEET)


def read_last_temp(ser: Serial, current_time: dt.datetime):

    data = ser.read(4)
    sensor_value_bytes = data[:2]
    index_bytes = data[2:]
    sensor_value = struct.unpack('H', sensor_value_bytes)[0]
    index_value = struct.unpack('H', index_bytes)[0]

    voltage = sensor_value * (5.0 / 1023.0)  # sensor_value = analogRead(A0);  // from 0 to 1023
    temperature = (voltage - 1.375) / 0.0225  # convert voltage of middle pin to temperature (data sheet)
    rounded_temperature = round(temperature / 0.2) * 0.2  # round to resolution 0.2 C

    print(f'T = {rounded_temperature:.1f} \t\t t = {current_time} \t\t frame = {index_value}')
    return rounded_temperature


def animate(frame: int, ser: Serial, times_raw: list[float], temps_raw: list[float]):

    # get time at measurement and read the value
    current_time = dt.datetime.now()
    last_temp = read_last_temp(ser, current_time)
    last_temp = round(last_temp, 3)

    # save, format dates and truncate to most recent readings
    times_raw.append(current_time)
    temps_raw.append(last_temp)
    times = [timestamp.strftime('%H:%M:%S') for timestamp in times_raw[-1 * VALS_WINDOW :]]
    temps = temps_raw[-1 * VALS_WINDOW :]

    # clear and set axis properties
    plt.cla()
    plt.title('PS5 Outlet Temperature')
    plt.xlabel('Time / hr min sec ')
    plt.ylabel('Temperature / $ ^{\circ} C $ ')
    plt.xticks(rotation=30)
    plt.gca().xaxis.set_major_locator(MaxNLocator(15))

    # plot upper and lower safe limit lines
    plt.plot(times, [T_MAX] * len(times),
        label=r'$ T_{max} = $' + f'{T_MAX} ' + r'$ ^{\circ} C $',
        color='orangered', linestyle='dashed')
    plt.plot(times, [T_MIN] * len(times),
        label=r'$ T_{min} = $' + f'{T_MIN} ' + r'$ ^{\circ} C $',
        color='dodgerblue', linestyle='dashed')
    
    # plot temperature record line
    plt.plot(times, temps,
        label=f'Last temp = {last_temp}' + r' $ ^{\circ} C $',
        color='silver')
    
    plt.legend(loc='upper left')


def main():

    # init
    times_raw, temps_raw = [], []
    fig = plt.figure()

    # find COM port of arduino
    if USE_COM_PORT is None:
        port_nos = [(portno, desc) for portno, desc, _ in comports() if _PORT_DESC_KEYWORD in desc]
        port_nos.sort(key=lambda p: p[0])
        if port_nos != []:
            port, desc = port_nos[-1]
        else:
            raise NameError('Could not find a COM port. Try specifying the port number in USE_COM_PORT.')
    else:
        port, desc = USE_COM_PORT, None

    # read data continuously from serial and make animated live plot
    try:
        with Serial(port, _BAUD_RATE, timeout=1) as s:
            if not s.is_open:
                logging.error('Port is not open.')
            else:
                logging.debug(f'Connected to {port}: {desc}')
            ani = anim.FuncAnimation(fig, animate, fargs=(s, times_raw, temps_raw))
            plt.show()
    
    except (SerialException, PortNotOpenError) as e:
        logging.error(f'Failed to connect to device: {type(e)}: {e}.')

    # export all data as .csv when graph window closed
    with open(OUTPUT_FILENAME, 'a') as f:
        f.truncate(0)
        f.write('Number,Time / hh:mm:ss,Temperature / C\n')
        for frame, (timestamp, temp) in enumerate(zip(times_raw, temps_raw)):
            f.write(f'{frame},{timestamp},{temp}\n')
        logging.debug(f'Output data written to {OUTPUT_FILENAME}')



if __name__ == '__main__':

    main()
