import csv 
import os
import sys
import threading
from geopy import geocoders
from select import select
from time import sleep

numRows = sum(1 for line in open('predictive-plotting.csv'))
rows = 0
skipped = 0
google = 0
failed = 0

class InputWatcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        raw_input()

class Geocoder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global failed
        global skipped
        global rows
        global google
        
        self.running = True
        with open('predictive-plotting.csv', 'rb') as f:
            with open('predictive-plotting.temp.csv', 'wb') as f2:
                reader = csv.reader(f)
                writer = csv.writer(f2)
                geocoder = geocoders.googlev3.GoogleV3()
                
                for row in reader:
                    rows += 1
                    if not self.running:
                        failed += 1
                    elif len(row) > 4:
                        skipped += 1
                    else:
                        address = row[3].strip() + ', Virginia Beach, VA'
                        try:
                            place, (lat, lng) = geocoder.geocode(address, exactly_one=False)[0]
                            sleep(0.1)
                            row.append(place)
                            row.append(lat)
                            row.append(lng)
                            google += 1
                        except:
                            failed += 1
                    writer.writerow(row)
                    sys.stdout.write('\rProcessed {0}/{1}. Errors: {2}'.format(str(rows), str(numRows), failed))
                    sys.stdout.flush()
    
    def stop(self):
        self.running = False

print 'Geocoding File. Press Enter to stop.'
g = Geocoder()
g.start()

watcher = InputWatcher()
watcher.start()

while g.isAlive():
    watcher.join(1)
    if not watcher.isAlive():
        g.stop()
        g.join()

os.rename('predictive-plotting.temp.csv', 'predictive-plotting.csv')
print '\nDONE'
print '================='
print 'Rows:' + str(rows)
print 'Already Done:' + str(skipped)
print 'Google Geocode:' + str(google)
print 'Not Geocoded:' + str(failed)
print 'File {0}% Geocoded'.format(100 - (100*float(failed)/float(rows)))
print 'Press Enter to exit'
