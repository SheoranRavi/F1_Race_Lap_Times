import PyPDF2
import re
import matplotlib.pyplot as plt

FIG_SIZE = (8,6)
FILE = 'N:/Downloads/race_laps.pdf'
DRIVERS = ['Daniel RICCIARDO', 'Lando NORRIS', 
                'Sebastian VETTEL', 'Kimi RAIKKONEN',
                'Romain GROSJEAN', 'Pierre GASLY',
                'Sergio PEREZ', 'Charles LECLERC',
                'Lance STROLL', 'Kevin MAGNUSSEN',
                'Alexander ALBON', 'Daniil KVYAT',
                'Nico HULKENBERG', 'Max VERSTAPPEN',
                'Lewis HAMILTON', 'Carlos SAINZ',
                'George RUSSELL', 'Valtteri BOTTAS',
                'Robert KUBICA', 'Antonio GIOVINAZZI']

def get_lap_times(pdfReader, drivers):
    num_pages =  pdfReader.numPages
    # store driver names and their lap times in a list
    lap_times = []
    for i in range(num_pages):
        pageObj = pdfReader.getPage(i)
        text = pageObj.extractText()
        # Use regex to search for drivers and lap times in the pdf text
        lap_times += re.findall('|'.join(drivers)+
                                '|[0-9].[0-9][0-9].[0-9][0-9][0-9]', text)
        
    # Create a dictionary to store a driver's lap times
    # after converting them into float seconds
    curr_driver = lap_times[0]
    driver_lap_times = {}
    
    for lap in lap_times:
        try:
            secs = float(lap[2:])
            secs = secs + float(lap[0])*60
            driver_lap_times[curr_driver].append(round(secs, 3))
        except ValueError:
            curr_driver = lap
            driver_lap_times[curr_driver] = []
        
    return driver_lap_times

def plot_times(lap_times):
    drivers_of_interest = ['Sebastian VETTEL', 'Charles LECLERC',
                       'Lewis HAMILTON', 'Valtteri BOTTAS',
                       'Max VERSTAPPEN']
    #drivers_of_interest = DRIVERS
#    drivers_of_interest = ['Charles LECLERC',
#                           'Max VERSTAPPEN']    
    
    # Configure pyplot
    plt.style.use('tableau-colorblind10')
    plt.figure(figsize=FIG_SIZE)
    plt.xlabel('Lap Number')
    plt.ylabel('Lap Time (seconds)')
    plt.title('2019 Australian Grand Prix')
    # change ylim and xticks based on race track
    plt.ylim((85,95))
    plt.xticks([i for i in range(0, 60, 5)], rotation=90)
    for driver, times in lap_times.items():
        if driver in drivers_of_interest:
            plt.plot([i for i in range(len(times))], times, 'o-',
                      linewidth=1, markersize=2.5,
                      label=driver.split(' ')[1][:3])
#            plt.text(len(times)-1, times[-1], driver.split(' ')[1][:3],
#                   fontsize=10)
    
    plt.grid(axis='y', linestyle='--')
    plt.legend()
    
def plot_percent_times(lap_times):
    drivers_of_interest = ['Sebastian VETTEL', 'Charles LECLERC',
                       'Lewis HAMILTON', 'Valtteri BOTTAS',
                       'Max VERSTAPPEN']
    # find out the fastest lap of the race
    fastest_lap = 1000
    for driver, times in lap_times.items():
        curr_best = min(lap_times[driver])
        if curr_best < fastest_lap:
            fastest_lap = curr_best
            fastest_driver = driver
    # convert all laps to percentage of fastest lap
    percent_times = {}
    for driver, times in lap_times.items():
        percent_times[driver] = []
        for curr in times:
            percent_times[driver].append(curr/fastest_lap*100)
            
    # Configure pyplot
    plt.style.use('tableau-colorblind10')
    plt.figure(figsize=FIG_SIZE)
    plt.xlabel('Lap Number')
    plt.ylabel('Percent of fastest lap')
    plt.title('2019 Australian Grand Prix')
    # change ylim and xticks based on race track
    plt.ylim((99, 108))
    plt.xticks([i for i in range(0, 60, 5)], rotation=90)
    for driver, times in percent_times.items():
        if driver in drivers_of_interest:
            plt.plot([i for i in range(len(times))], times, 'o-',
                      linewidth=1, markersize=2.5,
                      label=driver.split(' ')[1][:3])
        
    plt.grid(axis='y', linestyle='--')
    plt.legend()
    
    return percent_times
            
if __name__ == '__main__':
    pdfFileObj = open(FILE, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    # Get the lap times
    lap_times = get_lap_times(pdfReader, DRIVERS)

    plot_times(lap_times)
    percent_times = plot_percent_times(lap_times)