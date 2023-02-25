"""Imports"""
import json
import re
import subprocess
import sys
import os
import shutil

"""Global Variables"""
data = {}
fieldname=["insts", "maxBytes", "maxHeap", "extHeap", "maxStack"]
root_dir = "/pqc/pqc-docker"
output_dir = "/pqc/output"
algs_dir = "/pqc/pqc-docker/algs/"
kem_algs = []
sig_algs = []

#***********************************************************************
def get_algs():
    """Function for creating list of algorithms"""

    # Setting alg text file directories
    kem_algs_file = algs_dir + "kem-algs-list.txt"
    sig_algs_file = algs_dir + "sig-algs-list.txt"

    # # Getting the kem algs
    with open(kem_algs_file, "r") as kem_file:

        for line in kem_file:
            kem_algs.append(line.strip())
    
    # Getting the digital siganture algorithms
    with open(sig_algs_file, "r") as alg_file:

        for line in alg_file:
            sig_algs.append(line.strip())


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
   """some random function they had for getting config data ro something??"""
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
def do_test(alg, meth, exepath):
   """Performing the tests and outputing the results"""

   # Running the valgrind memory profiler and saving output
   process = subprocess.Popen(["valgrind", "--tool=massif", "--stacks=yes", "--massif-out-file=valgrind-out", exepath, alg, str(meth)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
   (outs, errs) = process.communicate()


   # Copying the valgrin.out file
   val_out_filename = output_dir + "/" + alg + "-" + "valgrind.out"
   shutil.copyfile("./valgrind.out", val_out_filename)

   # Valgrind exception handling
   if process.returncode != 0:

      print("Valgrind died with retcode %d and \n%s\n%s\nFatal error. Exiting." % (process.returncode, outs, errs))
      exit(1)

   if len(data["config"]) == 0:

      parse_config(outs)

   # Parsing valgrind.out file through ms_print
   process = subprocess.Popen(["ms_print", "valgrind-out"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
   (outs, errs) = process.communicate()

   # Copy ms_print output
   ms_out_filename = output_dir + "/" + alg  + "-" + "ms-out.txt"
   with open(ms_out_filename, "w") as file:
       file.write(outs)

   # Parsing memory metrics
   result = get_peak(outs.splitlines())

   # Printing out test results to terminal
   try: 
      print("Result for %s: %s" % (alg, " ".join(result)))

   except TypeError:
      print("Result for %s: " % (alg))
      print(result)
      print(outs.splitlines())

#*******************************************************************
def main ():
   """Main function that sets up and execute tests"""

   # Checking if enough arguments have been passed to the script
   if len(sys.argv) != 2:
      print("Not enough arguments")
      exit(1)

   # Setting the input variables
   exepath=sys.argv[1]

   # Setting the method names based on the test progamme being supplied
   if exepath.find("kem") > 0:

      #methnames=["keygen","encaps","decaps"]
      algs = kem_algs

   else:

      #methnames=["keygen","sign","verify"]
      algs = sig_algs

   # Looping throuhg algs and running the tests
   for alg in algs:
       
       # looping throuhg operations
       for op in range(3):
           do_test(alg, op, exepath)


#*******************************************************************

"""Boiler Plate"""
if __name__ == "__main__":
    main()
