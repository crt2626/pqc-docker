"""Imports"""
import json
import re
import subprocess
import sys
import os
import shutil

"""Global Variables"""
# JSON data dict
data = {}

# metric headers
fieldname=["insts", "maxBytes", "maxHeap", "extHeap", "maxStack"]

# root dir

#*******************************************************************
def get_peak(lines):
    """Function for getting the peak memory metrics"""

    # Setting the intinal peak value
    peak = -1

    # Looping through output file lines looking for peak
    for line in lines: 
        
        # Getting snapshot number that has peak values
        if line.startswith(" Detailed snapshots: ["):
            match=re.search("\d+ \(peak\).*", line)

            if match:
                peak = int(match.group(0).split()[0])

         # Getting the line the file that has the peak metrics 
        if (peak > 0):
            
            if line.startswith('{: >3d}'.format(peak)): # remove "," and print all numbers except first:
                
                nl = line.replace(",", "")
                res = nl.split()
                del res[0]
                #print(" ".join(res))
                return res


#*******************************************************************
def parse_config(output):
   """"""
   lines = output.splitlines()
   loading = False
   for line in lines:
      if loading:
         if line == "\n": # done
            return
         elif line.startswith("Started at"):
                data["config"]["start"] = line[len("Started at "):]
         elif ":" in line:
                data["config"][line[:line.index(":")]]=line[line.index(":")+1:].lstrip()
      elif line.startswith("====="):
         loading=True



#*******************************************************************
def do_test(alg, meth, methnames, exepath):
   """Performing the tests and outputing the results"""

   #


   # Running the valgrind memory profiler and saving output
   process = subprocess.Popen(["valgrind", "--tool=massif", "--stacks=yes", "--massif-out-file=valgrind-out", exepath, alg, str(meth)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)

   (outs, errs) = process.communicate()

   # # Copying the valgrin.out file
   # if alg == "SPHINCS+-Haraka-256f-robust":
   #    shutil.copyfile("./valgrind.out", "./valgrind-test.txt")


   if process.returncode != 0:
      print("Valgrind died with retcode %d and \n%s\n%s\nFatal error. Exiting." % (process.returncode, outs, errs))
      exit(1)
   if len(data["config"]) == 0:
      parse_config(outs)
   process = subprocess.Popen(["ms_print", "valgrind-out"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
   (outs, errs) = process.communicate()

   # Copy ms_print output
   if alg == "SPHINCS+-Haraka-256f-robust":
      with open("test.txt", "w") as file:
         file.write(outs)


   result = get_peak(outs.splitlines())
   data[alg][methnames[meth]] = {}
   try: 
      print("Result for %s: %s" % (alg, " ".join(result)))
      for i in range(5):
         data[alg][methnames[meth]][fieldname[i]] = result[i]
   except TypeError:
      print("Result for %s: " % (alg))
      print(result)
      print(outs.splitlines())

#*******************************************************************
"""Doing the tests"""

# Checking if enough arguments have been passed to the script
if len(sys.argv) != 3:
   print("Not enough arguments")
   exit(1)

# Setting the input variables
exepath=sys.argv[1]
output_dir = sys.argv[2]

# Setting the method names based on the test progamme being supplied
if exepath.find("kem")>0:
   methnames=["keygen","encaps","decaps"]
   setKemAlgs = setKem
else:
   methnames=["keygen","sign","verify"]


# first determine all enabled algorithms
process = subprocess.Popen([exepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
(outs, errs) = process.communicate()
for line in outs.splitlines():
   print(line)
   if line.startswith("  algname: "):
      algs = line[len("  algname: "):].split(", ")

activealgs=[]
# weed out algs not enabled
for alg in algs:
   process = subprocess.Popen([exepath, alg, "0"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
   (outs, errs) = process.communicate()
   enabled=True
   for line in outs.splitlines():
      if "not enabled" in line:
         enabled=False
   if enabled:
         activealgs.append(alg)

for alg in activealgs:
   data[alg]={}
   # Activate this for a quick test:
   #if alg=="DEFAULT":
   for i in range(3):
      do_test(alg, i, methnames, exepath)

# Dump data
with open(exepath+".json", 'w') as outfile:
    json.dump(data, outfile)

