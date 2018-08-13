#!/opt/application/Python/python2.6/bin/python2.6
# coding: utf-8
from os.path import abspath, basename, dirname
from sys import argv, exit, path
from os import system

NAME_SELF = basename(__file__)
DIR_SELF = dirname(abspath(__file__))
DIR_TOP = dirname(DIR_SELF)
WORKING_DIR="/etc/haproxy/autoconf/working"
TARGET_DIR="/etc/haproxy"
DATA_DIR="/etc/haproxy/autoconf/data"

path.append(DIR_TOP)

from getopt import getopt, GetoptError
from json import dumps
from re import search
import subprocess
#from subprocess import call,check_output

table = [] # Table of all dico
DEBUG=0
class OurList(list):
# allows to translate list of letter to a list of word
    def join(self, s):
        string =  s.join(self).rstrip().split(" ")
        return string

def main(argv):
    project_receiver    = None
    id_number           = None
    ip_address          = None
    move_cfgfile='mv -f ' + TARGET_DIR + '/*.cfg ' + WORKING_DIR
    recover_cfgfile='mv -f ' + WORKING_DIR + '/*.cfg ' + TARGET_DIR 
    # Get parameters
    print "Work on Generate Conf"
    try:

        opts, args = getopt(argv, "h:u", ["help", "grammar="])
        TargetDir = TARGET_DIR
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                exit(2)
            #elif opt == '-u':
            #    TargetDir = TARGET_DIR

        #print "Start"
        #res =  subprocess.check_output("grep ListenPort *.data | cut -d \"=\" -f2 | sort | uniq |awk '{ msg=$0 \" \" msg ;}END{print msg}'", shell = True )
        print "Backup existing .cfg files"
        subprocess.check_call('rm -f ' + WORKING_DIR + '/*', shell = True)
        subprocess.check_call(move_cfgfile, shell = True)
        res =  subprocess.Popen("grep ListenPort " + DATA_DIR + "/" + "*.data | cut -d \"=\" -f2 | sort | uniq |awk '{ msg=$0 \" \" msg ;}END{print msg}'",stdout=subprocess.PIPE, shell=True).communicate()[0]
#   print "grep ListenPort " + DATA_DIR + "/" + "*.data | cut -d \"=\" -f2 | sort | uniq |awk '{ msg=$0 \" \" msg ;}END{print msg}'"
        for elt in ( OurList(res).join("") ):

            del table[:]

            if len(elt) == 0:
                print "Empty files in " + DATA_DIR
                exit(2)

            # In order to known how many config files we need
            if DEBUG == 1:
                print "Config File generate " + TargetDir + "/" + elt + ".cfg"
            # Load start of config file
            if ( elt == "80" or elt == "8080" or elt == "5050" or elt == "3128" ):
                subprocess.Popen( "cat " + DATA_DIR +  "/port_http.start | awk -v var=" + elt + " \'{ gsub(\"{{port}}\",var,$0); print $0;}\' > " + TargetDir + "/" + elt + ".cfg",shell= True)
            elif (elt == "389" or elt == "636" ):
                subprocess.Popen( "cat " + DATA_DIR +  "/port_tcp.start | awk -v var=" + elt + " \'{ gsub(\"{{port}}\",var,$0); print $0;}\' > " + TargetDir + "/" + elt + ".cfg",shell= True)
            elif (elt == "8443" or elt == "2222" or elt == "2013" or elt == "8081" or elt == "3306" or elt == "15672" or elt == "15674" or elt == "1883" or elt == "5671" or elt == "5672" or elt == "61613" or elt == "61614" or elt == "8883"):
                subprocess.Popen( "cat " + DATA_DIR +  "/port_tcp_timer.start | awk -v var=" + elt + " \'{ gsub(\"{{port}}\",var,$0); print $0;}\' > " + TargetDir + "/" + elt + ".cfg",shell= True)
            else :
                subprocess.Popen( "cat " + DATA_DIR +  "/port_https.start | awk -v var=" + elt + " \'{ gsub(\"{{port}}\",var,$0); if( $0 ~ /bind/ ) $0 = $0 \" ssl crt /etc/haproxy/certificats/\"; print $0;}\' > " + TargetDir + "/" + elt + ".cfg",shell= True)
            file = open( TargetDir + "/" + elt + ".cfg", "a")

            LoadDataFile(file,elt)

            if DEBUG == 1:
                for i in table:
                        for key, value in i.items():
                                print "On a " + key + " => " + value
            RedirectPart(file)

            FrontEndPart(file)

            BackEndPart(file,elt)
        
            file.close()

            #Checking generated working file
            check_cmd="/usr/sbin/haproxy -f "+TargetDir+"/"+elt+".cfg -c"

            try:
                subprocess.check_call(check_cmd, shell = True)
                print TargetDir+"/"+elt+".cfg generated and verified successfully\n"
            except subprocess.CalledProcessError as e:
                print "Command line or .data file is not valid \nPlease check .data file\n"
                #del_file_cmd="rm " + TargetDir + "/" + elt + ".cfg"
                #system(del_file_cmd)
                subprocess.check_call(recover_cfgfile, shell = True)
                print "Previous .cfg files recovered"
                exit(2)

            #Applying new .cfg files
            #apply_cfg="/etc/haproxy/autoconf/bin/python autoconf.py -u"
            #subprocess.check_call("python autoconf.py -u", shell = True)
        
        
        #Reload HAproxy service

        try:
            subprocess.check_call('cp -f ' + WORKING_DIR + '/haproxy.cfg ' + TARGET_DIR, shell = True)
            subprocess.check_call('service haproxy reload', shell = True)
            print "HAProxy status : reloaded successfully"
            print"\n"
        except subprocess.CalledProcessError as e1:
            print "HAproxy status : ERROR can't reload"
            print "\n"
            exit(e1.returncode)

    except GetoptError:
        print "ERROR occurs during process"
        print "Recovering previous .cfg files"
        subprocess.check_call(recover_cfgfile, shell = True)
        exit(2)

def RedirectPart(file):

        file.write("\n\n\t#\tREDIRECT PART\n\n\n")
        # All data are recorded then write it in cfg files
        for i in table:
            try:
                  if len(i["SSL_FC"]) != 0 :
                      file.write("\tredirect scheme https code 301 if { hdr(Host)")
                      for j in  i["SSL_FC"].split():
                          try:
                              file.write(" -i " + j + " ")
                          except KeyError:
                              None
                      file.write("} !{ ssl_fc }\n")
                  if len(i["REDIRECT_PREFIX"]) != 0 :
                      for j in  i["REDIRECT_PREFIX"].split(";"):
                          if len(j) > 1 :
                              file.write("\tredirect prefix " + j.split("|")[0] + " if { hdr(host) -i "  + j.split("|")[1] + " }\n")
            except KeyError:
                  None
        file.write("\tredirect scheme https if !{ ssl_fc }\n")

def BackEndPart(file,elt):

        # BACKEND PART

        file.write("\n\n#---------------------------------------------------------------------\n")
        file.write("## static backend for serving up images, stylesheets and such\n")
        file.write("##---------------------------------------------------------------------\n")
#
        file.write("\n\n\t#\tBACKEND PART\n\n\n")

        # All data are recorded then write it in cfg files
        for i in table:
            try:
                if not len(i["BACK_ListIP"]) == 0 :
                    file.write("\n# service " + i["Service"] + "\n")
                    file.write("# " + i["Comment"] + "\n")
                    file.write("backend\t\t" + i["Service"].lower() + "-backend-" + i["FRONT_ListenPort"] + "\n")
                    if (elt == "389" or elt == "636" or elt == "8443" or elt == "2222" or elt == "2013" or elt == "8081" or elt == "3306" or elt == "15672" or elt == "15674" or elt == "1883" or elt == "5671" or elt == "5672" or elt == "61613" or elt == "61614" or elt == "8883"):
                        file.write("\tbalance\t\tleastconn\n\tmode\t\ttcp\n")
                    else :
                        file.write("\tbalance\t\troundrobin\n\tmode\t\thttp\n")
                    try:
                        if len(i["BACK_Cookie"]) != 0 :
                            file.write("\tcookie\t\t" + i["BACK_Cookie"] + "\n")
                    except KeyError:
                        None
                    try:
                        if len(i["BACK_Option"]) != 0 :
                            for j in  i["BACK_Option"].split(";"):
                                if len(j) > 1 :
                                    file.write("\toption\t\t" + j + "\n")
                    except KeyError:
                        None
                    try:
                        if len(i["BACK_WholeLine"]) != 0 :
                            for j in  i["BACK_WholeLine"].split(";"):
                                if len(j) > 1 :
                                    file.write("\t" + j + "\n")
                    except KeyError:
                        None
                    cpt = 1
                    try:
                        for j in  i["BACK_ListIP"].split():
                            try:
                                file.write("\tserver\t\t" + i["Service"].lower() + "_" + str(cpt) + "\t" + j )
                            except KeyError:
                                None
                            try:
                            # option like :         server                                  pcf_rtr1 10.110.140.15:80 check inter 1000
                                if len(i["BACK_IPOption"]) != 0 :
                                    file.write(" " + i["BACK_IPOption"])
                            except KeyError:
                                None
                            try:
                                if len(i["BACK_IPOptionServer"]) != 0 :
                                    file.write(" " + i["BACK_IPOptionServer"] + " " + i["Service"].lower() + "_" + str(cpt))
                            except KeyError:
                                None
                            file.write("\n")
                            cpt += 1
                    except KeyError:
                        None
            except KeyError:
                None

def FrontEndPart(file):

        file.write("\n\n\t#\tFRONT END\n\n\n")
        l_Url = False
        # All data are recorded then write it in cfg files
        for i in table:
            try:
                try:
                    if not len(i["Service"]) == 0 :
                        # FRONT END PART
                        file.write("\t# service " + i["Service"] + "\n")
                except KeyError:
                    None
                try:
                    if not len(i["FRONT_HDR"]) == 0 :
                        # acl
                        file.write("\tacl is_" + i["Service"].lower() + "\t\thdr(host) ")
                        for j in  i["FRONT_HDR"].split():
                            file.write(" -i " + j )
                        file.write("\n")
                        l_Url = True
                except KeyError:
                    None
                try:
                    if not len(i["FRONT_HDR_END"]) == 0 :
                        # acl
                        file.write("\tacl is_" + i["Service"].lower() + "\t\thdr_end(host) ")
                        for j in  i["FRONT_HDR_END"].split():
                            file.write(" -i " + j )
                        file.write("\n")
                        l_Url = True
                except KeyError:
                    None
                try:
                    if not len(i["FRONT_HDR_REG"]) == 0 :
                        # acl
                        file.write("\tacl is_" + i["Service"].lower() + "\t\thdr_reg(host) ")
                        for j in  i["FRONT_HDR_REG"].split():
                            file.write(" -i " + j )
                        file.write("\n")
                        l_Url = True
                except KeyError:
                    None
                try:
                    if not len(i["FRONT_HDR_DOM"]) == 0 :
                        # acl
                        file.write("\tacl is_" + i["Service"].lower() + "\t\thdr_dom(host) ")
                        for j in  i["FRONT_HDR_DOM"].split():
                            file.write(" -i " + j )
                        file.write("\n")
                        l_Url = True
                except KeyError:
                    None
                if l_Url ==  True:
                    file.write("\tuse_backend\t\t" + i["Service"].lower() + "-backend-"  +  i["FRONT_ListenPort"] + " if is_" + i["Service"].lower() + "\n\n")
            except KeyError:
                None


def LoadDataFile(file,port):

        #res =  check_output("grep ListenPort *.data | grep " + port + " | cut -d: -f1 |awk '{ msg=$0 \" \" msg ;}END{print msg}'", shell = True )
#        res =  subprocess.Popen("grep ListenPort *.data | grep " + port + " | cut -d: -f1 |awk '{ msg=$0 \" \" msg ;}END{print msg}'", stdout=subprocess.PIPE, shell=True).communicate()[0]
        if DEBUG == 1:
            print "grep -l ListenPort=" + port + "$ " + DATA_DIR + "/*.data |awk '{ msg=$0 \" \" msg ;}END{print msg}'"
        res =  subprocess.Popen("grep -l ListenPort=" + port + "$ " + DATA_DIR + "/*.data |awk '{ msg=$0 \" \" msg ;}END{print msg}'", stdout=subprocess.PIPE, shell=True).communicate()[0]

        for elt in ( OurList(res).join("") ):

            dico = {}
            if DEBUG == 1:
                print "work on " + elt
            DataFileDesc  = open(elt, "r")
            lignes = DataFileDesc.readlines()
            for ligne in lignes:
                if ligne.find("=") != -1 :
                    #print "First On a " + ligne.split("=")[0] + " et " + ligne.split("=")[1].rstrip()
                    dico[ligne.split("=")[0]] = ligne.split("=")[1].rstrip()

            # Store this dico in the global table
            table.append(dico)

            # Close Data file
            DataFileDesc.close()



def usage():
    print('Description:')
    print('    - Generate Conf to HAPROXY')
    print("         - From " +  DATA_DIR + "/*.data files defined manually, updates conf files available for HAPROXY in  " + WORKING_DIR)
    print("         - u      : updates HAPROXY  conf in the release directory " + TARGET_DIR +  " instead of working directory " + WORKING_DIR )

if __name__ == "__main__":
    main(argv[1:])
