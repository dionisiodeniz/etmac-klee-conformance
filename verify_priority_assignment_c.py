import subprocess
import re
import shutil

def klee_createSchedulingAssignments(testdir,thread_variables):
    outfile = open(testdir+"/klee_app_thread_setschedparam_assertions.h","w")
    outfile.write("ghost_scheduling_policy = policy;\n")
    outfile.write("ghost_sched_param_thread = t;\n")
    for i in range(len(thread_variables)):
        outfile.write("if (t == "+thread_variables[i]+"){\n")
        outfile.write("\tghost_"+thread_variables[i]+"_sched_parameter.sched_priority = p->sched_priority;\n")
        outfile.write("\tghost_"+thread_variables[i]+"_scheduling_policy = policy;\n")
        # outfile.write("\tassert(ghost_"+thread_variables[i]+"_scheduling_policy == "+policies[i]+");\n")
        # outfile.write("\tassert(ghost_"+thread_variables[i]+"_sched_parameter.sched_priority == "+priorities[i]+");\n")
        outfile.write("}\n")
    outfile.close()

def klee_createMakeSymbolics(testdir,thread_variables):
    outfile = open(testdir+"/klee_app_make_symbolic.h","w")
    outfile.write("#ifdef KLEE_EXECUTION\n")
    outfile.write('klee_make_symbolic(&ghost_scheduling_policy, sizeof(int),"policy");\n')
    outfile.write('klee_make_symbolic(&ghost_sched_param_thread, sizeof(pthread_t),"ghost_sched_param_thread");\n')
    for i in range(len(thread_variables)):
        outfile.write('klee_make_symbolic(&'+thread_variables[i]+',sizeof(pthread_t),"'+thread_variables[i]+'");\n')
        outfile.write('klee_make_symbolic(&ghost_'+thread_variables[i]+'_sched_parameter.sched_priority, sizeof(ghost_'+thread_variables[i]+'_sched_parameter.sched_priority),"ghost_'+thread_variables[i]+'_sched_parameter.sched_priority");\n')
        outfile.write('klee_make_symbolic(&ghost_'+thread_variables[i]+'_scheduling_policy,sizeof(ghost_'+thread_variables[i]+'_scheduling_policy),"ghost_'+thread_variables[i]+'_scheduling_policy");\n')
    outfile.write("#endif\n")
    outfile.close()

def klee_createGhostVariables(testdir,thread_variables):
    outfile = open(testdir+"/klee_app_ghost_variables.h","w")
    outfile.write("int ghost_scheduling_policy;\n")
    outfile.write("pthread_t ghost_sched_param_thread;\n")
    for i in range(len(thread_variables)):
        outfile.write("struct sched_param ghost_"+thread_variables[i]+"_sched_parameter;\n")
        outfile.write("int ghost_"+thread_variables[i]+"_scheduling_policy;\n")
    outfile.close()

def klee_addKleeIncludes(testdir,input_file,output_file):
    file = open(testdir+"/"+input_file,"r")
    outfile = open(testdir+"/"+output_file,"w")
    outfile.write('#define KLEE_EXECUTION 1\n')
    stage = 0
    for line in file.readlines():
        trimmedLine = line.strip()
        if stage == 0:
            if (any(x in trimmedLine for x in ["#define","#include","//"]) or len(trimmedLine) == 0):
                outfile.write(line)
            else:
                outfile.write('#include "klee_app_ghost_variables.h"\n')
                outfile.write('#include "klee_includes.h"\n')
                outfile.write(line)
                stage = stage + 1
        elif stage == 1:
            if "(" in trimmedLine and not "#define" in trimmedLine:
                outfile.write('#include "klee_thread_library.h"\n')
                stage = stage +1
            outfile.write(line)
        elif stage == 2:
            m =  re.search("main[\t ]*[(]",trimmedLine)
            if not m is None:
                stage = stage +1
            outfile.write(line)            
        elif stage == 3:
            if any(x in trimmedLine for x in ["(","="]):
                outfile.write('#include "klee_app_make_symbolic.h"\n')
                stage = stage +1
            outfile.write(line)
        else:
            outfile.write(line)
    outfile.close()

def klee_addKleeIncludesToThreadMainFunctions(testdir,input_file,output_file,threadMainFunctions,threadpriorities,threadpolicies,threadLoopLine):
    infile = open(testdir+"/"+input_file,"r")
    outfile = open(testdir+"/"+output_file,"w")
    stage = 0
    threadvar =""
    lineNumber=0
    for line in infile.readlines():
        trimmedLine = line.strip()
        if stage == 0 :
            for tv in threadMainFunctions:
                m =  re.search(threadMainFunctions[tv]+"[\t ]*[(]",trimmedLine)
                if not m is None:
                    stage += 1
                    threadvar = tv
                    lineNumber = 0
                    break
        elif stage == 1:
            if lineNumber == threadLoopLine[threadvar]:
                stage += 1
            else:
                lineNumber += 1
        else:# stage == 2
            if any(x in trimmedLine for x in ["(","="]):
                # write assertion
                outfile.write("\tassert(ghost_"+threadvar+"_scheduling_policy == "+threadpolicies[threadvar]+");\n")
                outfile.write("\tassert(ghost_"+threadvar+"_sched_parameter.sched_priority == "+threadpriorities[threadvar]+");\n")
                outfile.write("\treturn NULL;\n")
                stage = 0
        outfile.write(line)
    outfile.close()

def klee_getThreadMainFunctions(fn,thread_creation_function_name):
    threadMainFunctions = {}
    file = open(fn,"r")
    for line in file.readlines():
        m = re.search(thread_creation_function_name+"[(]",line)
        if not m is None:
            x =re.split(thread_creation_function_name+"[(]",line)
            y = re.split("[,]",x[1])
            threadVar = y[0][1:]
            threadMainFunctions[threadVar] = y[2]
            #return y[2]
    return threadMainFunctions

def klee_verifyPriorityAssignment(compilerCommand, verifierCommand, testdir,source_file,thread_variables,threadpriorities,threadpolicies,error0):
    compilationProcess = subprocess.run([compilerCommand+" "+source_file], cwd=testdir, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("compilaton stdout:\n"+compilationProcess.stdout)
    # print("compilation stderrt:\n"+compilationProcess.stderr)
    checkingProcess = subprocess.run([verifierCommand+" "+source_file], cwd=testdir, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("check stdout:\n"+checkingProcess.stdout)
    # print("check stdout parsed:\n"+checkingProcess.stderr)
    for line in checkingProcess.stderr.splitlines():
        if "ERROR:" in line:
            # print(line)
            idx = line.find("ASSERTION FAIL:")
            if idx != -1:
                line = line[idx+len("ASSERTION FAIL:"):]
                for i in range(len(thread_variables)):
                    if thread_variables[i] in line:
                        if "policy" in line:
                            error0[0] += "Thread: "+thread_variables[i]+" not assigned scheduling policy "+threadpolicies[thread_variables[i]]
                        elif "priority" in line:
                            error0[0] += "Thread: "+thread_variables[i]+" not assigned scheduling priority "+threadpriorities[thread_variables[i]]
                        else:
                            error0[0] += line
                        break
            return False
    return True

def klee_copyVerifierFilesToWorkingDirectory(verifierDir,testdir):
    shutil.copy(verifierDir+"/klee_includes.h", testdir+"/")
    shutil.copy(verifierDir+"/klee_thread_library.h",testdir+"/") 

def klee_verifyPthreadSchedulingConfiguration(verifierDir,testdir,sourceFile,thread_variables,threadpriorities,threadpolicies,threadMainFunctions,threadLoopLine,error0):
    compilerCommand = "/home/dionisio/etmac-workspace/klee/compile.sh"
    verifierCommand = "/home/dionisio/etmac-workspace/klee/check.sh"
    klee_copyVerifierFilesToWorkingDirectory(verifierDir,testdir)
    klee_createGhostVariables(testdir,thread_variables)
    klee_createMakeSymbolics(testdir,thread_variables)
    klee_createSchedulingAssignments(testdir,thread_variables)
    klee_addKleeIncludes(testdir,sourceFile+".c",sourceFile+"-pass1.c")
    klee_addKleeIncludesToThreadMainFunctions(testdir,sourceFile+"-pass1.c",sourceFile+"-klee.c",threadMainFunctions,threadpriorities,threadpolicies,threadLoopLine)
    if klee_verifyPriorityAssignment(compilerCommand,verifierCommand, testdir,sourceFile+"-klee",thread_variables,threadpriorities,threadpolicies,error0):
        print("Verification Successful")
        return True
    else:
        print("Failed verification, error: "+error0[0])
        return False

verifierDir = "/home/dionisio/etmac-workspace/klee"
testdir = "/home/dionisio/etmac-workspace/klee/testdir"
compilerCommand = "/home/dionisio/etmac-workspace/klee/compile.sh"
verifierCommand = "/home/dionisio/etmac-workspace/klee/check.sh"
sourceFile = "rt-threads-example-3" # assumed to be .c file
error0=[""]
thread_variables = ["t1","t2"]
threadpriorities = {"t1":"2","t2":"3"}
threadpolicies = {"t1":"SCHED_FIFO","t2":"SCHED_FIFO"}
threadMainFunctions = {"t1":"thread_main1","t2":"thread_main2"} #getThreadMainFunctions("rt-threads-example-3.c","pthread_create_proxy")
threadLoopLine = {"t1":7,"t2":7}
klee_verifyPthreadSchedulingConfiguration(verifierDir,testdir,sourceFile,thread_variables,threadpriorities,threadpolicies,threadMainFunctions,threadLoopLine,error0)

# klee_copyVerifierFilesToWorkingDirectory(verifierDir,testdir)
# klee_createGhostVariables(testdir,thread_variables)
# klee_createMakeSymbolics(testdir,thread_variables)
# klee_createSchedulingAssertions(testdir,thread_variables,priorities,policies)
# klee_addKleeIncludes(testdir,sourceFile+".c",sourceFile+"-pass1.c")
# klee_addKleeIncludesToThreadMainFunctions(testdir,sourceFile+"-pass1.c",sourceFile+"-klee.c",threadMainFunctions,threadpriorities,threadpolicies,threadLoopLine)
# if klee_verifyPriorityAssignment(compilerCommand,verifierCommand, testdir,sourceFile+"-klee",thread_variables,priorities,error0):
#     print("Verification Successful")
# else:
#     print("Failed verification, error: "+error0[0])
