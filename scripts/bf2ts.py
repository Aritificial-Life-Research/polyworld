import argparse
import os
import re
import pw_agent
import sys

def parseArgs():
    parser = argparse.ArgumentParser(description = "Converts brain function files to time series.")
    parser.add_argument("run", metavar = "RUN", help = "run directory")
    parser.add_argument("--steps", metavar = "STEPS", type = int, help = "number of timesteps")
    return parser.parse_args()

args = parseArgs()
sys.stdout.write("# BEGIN ARGUMENTS\n")
sys.stdout.write("# END ARGUMENTS\n")
funcPath = os.path.join(args.run, "brain", "function")
anatPath = os.path.join(args.run, "brain", "anatomy")
for funcFileName in os.listdir(funcPath):
    match = re.search(r"^(?:incomplete_)?brainFunction_(\d+)(\.txt(?:\.gz)?)$", funcFileName)
    if match is None:
        continue
    anatFileName = "brainAnatomy_{0}_incept{1}".format(match.group(1), match.group(2))
    agent = pw_agent.pw_agent(os.path.join(funcPath, funcFileName), os.path.join(anatPath, anatFileName))
    sys.stdout.write("# AGENT {0}\n".format(agent.func.agent_index))
    sys.stdout.write("# DIMENSIONS {0} {1} {2}\n".format(agent.func.num_neurons - 1, agent.func.num_inputneurons, len(agent.func.neurons["behavior"])))
    sys.stdout.write("# BEGIN SYNAPSES\n")
    for neuron1 in range(agent.anat.num_neurons - 1):
        sys.stdout.write("{0}".format(neuron1))
        for neuron2 in range(agent.anat.num_neurons - 1):
            if agent.anat.cxnmatrix[neuron2, neuron1] != 0:
                sys.stdout.write(" {0}".format(neuron2))
        sys.stdout.write("\n")
    sys.stdout.write("# END SYNAPSES\n")
    sys.stdout.write("# BEGIN ENSEMBLE\n")
    stepCount = 0
    while True:
        sys.stdout.write("# BEGIN TIME SERIES\n")
        for step in range(agent.func.timesteps_lived):
            for neuron in range(agent.func.num_neurons - 1):
                if neuron > 0:
                    sys.stdout.write(" ")
                sys.stdout.write("{0}".format(agent.func.acts[neuron, step]))
            sys.stdout.write("\n")
            stepCount += 1
            if args.steps is not None and stepCount == args.steps:
                break
        sys.stdout.write("# END TIME SERIES\n")
        if args.steps is None or stepCount == args.steps:
            break
    sys.stdout.write("# END ENSEMBLE\n")
